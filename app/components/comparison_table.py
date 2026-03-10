"""
Color-coded comparison table showing each college's score per criterion.
"""

import pandas as pd
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import CRITERIA, MAJORS


def _rdylgn_style(val):
    """Map 0-100 to a red-yellow-green inline CSS style string."""
    try:
        v = max(0.0, min(100.0, float(val))) / 100.0
    except (TypeError, ValueError):
        return ""
    if v <= 0.5:
        r, g = 255, int(255 * (v / 0.5))
    else:
        r, g = int(255 * ((1.0 - v) / 0.5)), 255
    return f"background-color:rgb({r},{g},80);color:#111;padding:4px 8px;"


def _fmt(val):
    try:
        return f"{float(val):.1f}"
    except (TypeError, ValueError):
        return "N/A"


def render_comparison(scored_df: pd.DataFrame, weights: dict, selected_major: str = "general"):
    """Render a color-coded comparison table using HTML (no matplotlib needed)."""
    if scored_df.empty:
        return

    active_criteria = {k: v for k, v in CRITERIA.items() if k in weights}
    score_cols = [v["col"] for v in active_criteria.values()]
    label_map = {v["col"]: v["label"] for v in active_criteria.values()}

    if selected_major != "general" and "majors" in active_criteria:
        label_map["score_majors"] = MAJORS.get(selected_major, "Majors/Programs")

    display_df = scored_df[["name"] + score_cols + ["weighted_score"]].copy()
    display_df = display_df.rename(columns={**label_map, "name": "College", "weighted_score": "Total Score"})
    display_df = display_df.set_index("College")
    display_df = display_df.round(1)

    style_cols = [label_map.get(c, c) for c in score_cols] + ["Total Score"]

    # Build HTML table
    headers = "".join(
        f'<th style="padding:4px 8px;border-bottom:2px solid #ddd;">{col}</th>'
        for col in display_df.columns
    )
    rows_html = ""
    for college, row in display_df.iterrows():
        cells = f'<td style="padding:4px 8px;font-weight:bold;">{college}</td>'
        for col in display_df.columns:
            val = row[col]
            style = _rdylgn_style(val) if col in style_cols else "padding:4px 8px;"
            cells += f"<td style='{style}'>{_fmt(val)}</td>"
        rows_html += f"<tr>{cells}</tr>"

    html = f"""
    <div style="overflow-x:auto;">
    <table style="border-collapse:collapse;width:100%;font-size:0.9em;">
      <thead><tr>
        <th style="padding:4px 8px;border-bottom:2px solid #ddd;">College</th>
        {headers}
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    st.caption(
        "Scores are on a 0–100 scale. Green = strong, red = weak. "
        "Niche-based scores (campus life, food, etc.) are converted from A+–F letter grades. "
        "Graduation rate is scaled relative to the schools you selected — 100 means best among your picks, not best overall. "
        "N/A means no data was available for that school."
    )
