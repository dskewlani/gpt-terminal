"""
app.py — ProTrader Terminal v3
Professional Trading Terminal: Equity · Options · Futures · Auto Trading
All data persists across sessions via local JSON storage.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import math

import storage as db

import engine as eng
from ui import (
    TERMINAL_CSS, sig_badge, strength_bar, pnl_fmt,
    ticker_item, metric_card, level_box, profit_book_row, greek_box
)

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ProTrader Terminal v3",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(TERMINAL_CSS, unsafe_allow_html=True)

# ─── Persistent State Bootstrap ───────────────────────────────────────────────
def load_persistent():
    if "loaded" not in st.session_state:
        for key, default in [
            ("eq_portfolio",  []),
            ("eq_history",    []),
            ("opt_portfolio", []),
            ("opt_history",   []),
            ("fut_portfolio", []),
            ("fut_history",   []),
            ("etf_portfolio", []),
            ("etf_history",   []),
            ("mcx_portfolio", []),
            ("mcx_history",   []),
            ("journal",       []),
            ("kelly_wr",      0.55),
            ("scan_eq",       []),
            ("scan_opt",      []),
            ("scan_fut",      []),
            ("auto_eq",       False),
            ("auto_opt",      False),
            ("auto_fut",      False),
            ("auto_etf",      False),
            ("auto_mcx",      False),
            ("auto_eq_end",   None),
            ("auto_opt_end",  None),
            ("auto_fut_end",  None),
            ("auto_etf_end",  None),
            ("auto_mcx_end",  None),
        ]:
            st.session_state[key] = db.load(key, default)
        st.session_state["loaded"] = True

load_persistent()

def save_all():
    for key in ["eq_portfolio","eq_history","opt_portfolio","opt_history",
                "fut_portfolio","fut_history","etf_portfolio","etf_history","mcx_portfolio","mcx_history","journal","kelly_wr"]:
        db.save(key, st.session_state[key])

# ─── Safe number_input helper ─────────────────────────────────────────────────
def safe_num_input(label, hardcoded_min, dynamic_max, step=1, key=None, **kwargs):
    """
    Prevents StreamlitValueBelowMinError when dynamic_max < hardcoded_min.
    Computes a safe min, max, and default value automatically.
    """
    safe_max = max(int(hardcoded_min), int(dynamic_max))
    safe_min = min(int(hardcoded_min), int(dynamic_max))
    safe_min = max(1, safe_min)
    safe_max = max(safe_min, safe_max)
    safe_val = safe_max  # default to scanning everything
    safe_step = max(1, int(step))
    return st.number_input(label, safe_min, safe_max, safe_val, safe_step, key=key, **kwargs)

# ─── Live Index Data ──────────────────────────────────────────────────────────
@st.cache_data(ttl=20)
def get_indices():
    """Live index data from NSE India public API (no login, no API key)."""
    try:
        return eng.get_all_indices()
    except Exception:
        return {k: {"p": 0, "c": 0, "pct": 0, "h": 0, "l": 0}
                for k in ["BN", "NF", "VIX", "SX", "IT", "MID"]}

@st.cache_data(ttl=3600)
def get_expiries(n=5):
    dates = []
    d = datetime.now().date()
