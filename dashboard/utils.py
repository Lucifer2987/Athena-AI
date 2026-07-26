"""
utils.py  --  Athena AI Dashboard data loading helpers

Changes:
 - UTF-8 primary with latin1 fallback (handles degree sign in old CSVs).
 - ai_only_rows() filters out fallback/rule-based decisions for clean AI metrics.
 - load_savings_data() for the savings report page.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "simulation_log.csv"

REQUIRED_COLUMNS = [
    "step", "temperature", "pmv", "electricity",
    "reward", "action", "tool", "reasoning", "confidence",
]
NUMERIC_COLUMNS = ["step", "temperature", "pmv", "electricity",
                   "reward", "action", "confidence"]


# ---------------------------------------------
# Core loader
# ---------------------------------------------

def load_data() -> pd.DataFrame:
    """Load the simulation log with the fixed Athena CSV schema.

    Tries UTF-8 first (new logs), then latin1 (handles legacy degree signs).
    """
    if not LOG_FILE.exists():
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    df = None
    for encoding in ("utf-8", "utf-8-sig", "latin1"):
        try:
            df = pd.read_csv(LOG_FILE, encoding=encoding)
            break
        except Exception:
            continue

    if df is None or df.empty:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    # Ensure all required columns exist
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[REQUIRED_COLUMNS].copy()

    # Coerce numerics
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = (
        df.dropna(subset=["step"])
          .sort_values("step")
          .reset_index(drop=True)
    )
    return df


# ---------------------------------------------
# Row helpers
# ---------------------------------------------

def latest_row(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {col: None for col in REQUIRED_COLUMNS}
    return df.iloc[-1].to_dict()


def previous_row(df: pd.DataFrame) -> dict:
    if df is None or len(df) < 2:
        return {col: None for col in REQUIRED_COLUMNS}
    return df.iloc[-2].to_dict()


def current_time_label(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "No simulation data"
    step = df.iloc[-1]["step"]
    try:
        return f"Step {int(step):,}"
    except (TypeError, ValueError):
        return f"Step {step}"


# ---------------------------------------------
# AI-only filter  (excludes fallback/rule-based rows)
# ---------------------------------------------

def ai_only_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows where Athena AI made a genuine LLM decision.

    Excludes:
      - Rows with confidence == 0.0 (old-style LLM failures)
      - Rows with 'fallback' or 'rule-based' in reasoning (new fallback label)
      - Rows where tool == 'N/A'
    """
    if df is None or df.empty:
        return df

    mask = (
        (df["confidence"] > 0.1)
        & (~df["reasoning"].str.lower().str.contains("fallback|rule.based", na=False))
        & (df["tool"].str.upper() != "N/A")
    )
    return df[mask].copy()


# ---------------------------------------------
# Summary computation
# ---------------------------------------------

def compute_summary(df: pd.DataFrame) -> dict:
    empty = {
        "rows": 0, "temperature": None, "pmv": None,
        "electricity": None, "reward": None, "confidence": None,
        "temp_delta": 0.0, "pmv_delta": 0.0,
        "energy_delta": 0.0, "reward_delta": 0.0,
    }
    if df is None or df.empty:
        return empty

    row  = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else row

    def delta(col):
        v, p = row.get(col), prev.get(col)
        if pd.notna(v) and pd.notna(p):
            return float(v) - float(p)
        return 0.0

    return {
        "rows":         len(df),
        "temperature":  row.get("temperature"),
        "pmv":          row.get("pmv"),
        "electricity":  row.get("electricity"),
        "reward":       row.get("reward"),
        "confidence":   row.get("confidence"),
        "temp_delta":   delta("temperature"),
        "pmv_delta":    delta("pmv"),
        "energy_delta": delta("electricity"),
        "reward_delta": delta("reward"),
    }


# ---------------------------------------------
# Savings data (for savings_report.py)
# ---------------------------------------------

def load_savings_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return (full_df, baseline_df, athena_df)."""
    df = load_data()
    if df.empty:
        empty = pd.DataFrame(columns=REQUIRED_COLUMNS)
        return empty, empty, empty

    fallback_mask = (
        df["reasoning"].str.lower().str.contains("fallback|rule.based", na=False)
        | (df["confidence"] <= 0.1)
    )
    return df, df[fallback_mask].copy(), df[~fallback_mask].copy()
