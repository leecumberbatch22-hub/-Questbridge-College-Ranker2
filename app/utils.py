"""
Data loading and scoring utilities for the Streamlit app.
"""

import os
import sys
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CRITERIA, COLLEGES_CSV_PATH


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load colleges.csv once per session. Cached — won't reload on slider changes."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), COLLEGES_CSV_PATH)
    if not os.path.exists(path):
        st.error(
            "No college data found. Run the data pipeline first:\n\n"
            "```\npython -m scraper.pipeline --fallback-only\n```"
        )
        st.stop()
    df = pd.read_csv(path)
    # Ensure score columns are numeric
    for key, crit in CRITERIA.items():
        col = crit["col"]
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def calculate_all_scores(df: pd.DataFrame, selected_names: list, weights: dict) -> pd.DataFrame:
    """
    Filter to selected colleges and compute a weighted_score for each.

    NaN handling: if a criterion is missing for a school, its weight is
    redistributed proportionally among the criteria that do have data.

    Args:
        df: Full college DataFrame from load_data().
        selected_names: List of college names to include.
        weights: Dict {criterion_key: fraction} where values sum to ~1.0.

    Returns:
        Filtered DataFrame with a 'weighted_score' column added.
    """
    filtered = df[df["name"].isin(selected_names)].copy()
    if filtered.empty:
        return filtered

    def score_row(row):
        available = {
            k: v for k, v in CRITERIA.items()
            if not pd.isna(row.get(v["col"], float("nan")))
        }
        if not available:
            return float("nan")
        total_weight = sum(weights.get(k, 0) for k in available)
        if total_weight == 0:
            return float("nan")
        return round(
            sum(row[CRITERIA[k]["col"]] * (weights.get(k, 0) / total_weight)
                for k in available),
            2,
        )

    filtered["weighted_score"] = filtered.apply(score_row, axis=1)
    return filtered
