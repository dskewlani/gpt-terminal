"""
storage.py — ProTrader Terminal
Persistent storage layer using Neon PostgreSQL (free tier).
Drop-in replacement for the original JSON file-based storage.
All function signatures are identical — app.py needs zero changes.

Setup:
  1. Sign up at https://neon.tech (free, no credit card)
  2. Create a project, copy the connection string
  3. Add to .streamlit/secrets.toml:
       DATABASE_URL = "postgresql://user:pass@ep-xxx.ap-south-1.aws.neon.tech/neondb?sslmode=require"
  4. pip install psycopg2-binary
  5. Run your app — tables are created automatically on first launch

Connection string can also be set as an environment variable:
  export DATABASE_URL="postgresql://..."
"""

import json
import os
import time
import logging
from datetime import datetime
from contextlib import contextmanager

try:
    import psycopg2
    from psycopg2.pool import ThreadedConnectionPool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("storage")

# ─── Connection String Resolution ─────────────────────────────────────────────
def _get_db_url() -> str:
    """
    Tries to get the DATABASE_URL from:
    1. Streamlit secrets (st.secrets["DATABASE_URL"]) — preferred for Streamlit Cloud
    2. Environment variable DATABASE_URL — preferred for local dev / other hosts
    Returns empty string if neither is available.
    """
    # Try Streamlit secrets first
    try:
        import streamlit as st
        url = st.secrets.get("DATABASE_URL", "")
        if url:
            return url
    except Exception:
        pass

    # Fall back to environment variable
    return os.environ.get("DATABASE_URL", "")


DATABASE_URL = _get_db_url()

# ─── Connection Pool ───────────────────────────────────────────────────────────
# A pool of 1–5 connections is ideal for a single-user Streamlit app.
# Neon free tier allows up to ~100 connections but we stay conservative.
_pool: "ThreadedConnectionPool | None" = None

def _get_pool() -> "ThreadedConnectionPool | None":
    global _pool
    if not PSYCOPG2_AVAILABLE:
        return None
    if not DATABASE_URL:
        return None
    if _pool is None:
        try:
            _pool = ThreadedConnectionPool(minconn=1, maxconn=5, dsn=DATABASE_URL)
            log.info("[Storage] Connection pool created.")
        except Exception as e:
            log.error(f"[Storage] Failed to create connection pool: {e}")
            return None
    return _pool

@contextmanager
def _conn():
    """
    Context manager that checks out a connection from the pool,
    commits on success, rolls back on error, and always returns
    the connection to the pool.
    """
    pool = _get_pool()
    if pool is None:
        raise RuntimeError(
            "[Storage] No database connection available. "
            "Check DATABASE_URL in .streamlit/secrets.toml or environment variables."
        )
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
