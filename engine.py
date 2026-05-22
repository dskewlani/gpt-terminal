"""
engine.py — ProTrader Terminal v5 — Angel One / NSE Free Data Edition
======================================================================
CHANGES in v5:
  ✅ REMOVED yfinance entirely — replaced with NSE India public API + Angel One
  ✅ Live prices from NSE India API (no login, no API key)
  ✅ OHLCV history from NSE/Angel One public endpoints (no login required)
  ✅ FIXED: Price not updating in auto-trading — direct NSE quote fetch
  ✅ Robust fallback chain: NSE Quote → NSE Chart → NSE Historical → mock
  ✅ All existing indicators, signals, Kelly, Greeks, strategies unchanged
  ✅ Cache TTL unchanged (15s intraday, 300s EOD)
  ✅ Angel One SmartAPI public market data used for historical OHLCV
  ✅ Rate limiting and retry logic for NSE API

DATA SOURCE PRIORITY:
  1. NSE India Live Quote:  https://www.nseindia.com/api/quote-equity
  2. NSE Chart Data:        https://www.nseindia.com/api/chart-databyindex
  3. Angel One Historical:  https://margincalculator.angelbroking.com/OpenAPI_File/files/json/
  4. NSE Historical Data:   https://www.nseindia.com/api/historical/cm/equity

NSE SYMBOL MAPPING:
  RELIANCE.NS → RELIANCE (strip .NS/.BO)
  ^NSEI       → NIFTY 50 index
  ^NSEBANK    → NIFTY BANK index
  ^INDIAVIX   → India VIX
"""

import numpy as np
import pandas as pd
import math
import time
import os
import requests
import concurrent.futures
import warnings
from datetime import datetime, date, timedelta
from io import StringIO

warnings.filterwarnings("ignore")

# ─── NSE Session (persistent cookies — required by NSE API) ──────────────────
_nse_session: requests.Session | None = None
_nse_session_ts: float = 0.0
_NSE_HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept":          "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer":         "https://www.nseindia.com/",
}

def _get_nse_session() -> requests.Session:
    """Return a session with valid NSE cookies (re-initialised every 25 min)."""
    global _nse_session, _nse_session_ts
    if _nse_session is None or (time.time() - _nse_session_ts) > 1500:
        s = requests.Session()
        s.headers.update(_NSE_HEADERS)
        try:
            # Warm-up: hit the homepage to get cookies
            s.get("https://www.nseindia.com", timeout=10)
            time.sleep(0.3)
        except Exception:
            pass
        _nse_session = s
        _nse_session_ts = time.time()
    return _nse_session


def _nse_clean_symbol(symbol: str) -> str:
    """RELIANCE.NS → RELIANCE  |  HDFCBANK.BO → HDFCBANK"""
    return symbol.replace(".NS", "").replace(".BO", "").replace(".MCX", "").upper().strip()


# --- Angel One live-price integration ---------------------------------------
_angel_obj = None
_angel_session_ts = 0.0
_angel_master_cache = {"rows": None, "ts": 0.0}

def _secret(name: str, default: str = "") -> str:
    try:
        import streamlit as st
        value = st.secrets.get(name, "")
        if value:
            return str(value)
    except Exception:
        pass
    return os.environ.get(name, default)

def _get_angel_client():
    global _angel_obj, _angel_session_ts
    if _angel_obj is not None and (time.time() - _angel_session_ts) < 1500:
        return _angel_obj
    api_key = _secret("ANGEL_API_KEY")
    client_code = _secret("ANGEL_CLIENT_CODE")
    password = _secret("ANGEL_PASSWORD")
    totp_secret = _secret("ANGEL_TOTP_SECRET")
    totp_value = _secret("ANGEL_TOTP")
    if not api_key or not client_code or not password or not (totp_secret or totp_value):
        return None
    try:
