"""
Color-coded comparison table showing each college's score per criterion.
"""

import pandas as pd
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import CRITERIA, MAJORS


def render_comparison(scored_df: pd.DataFrame, weights: dict, selected_major: str = "general"):
    """Render a styled comparison table with green-yellow-red color coding.

    Only shows columns for criteria that are active (present in weights).
    When a specific major is selected, relabels the Majors column accordingly.
    """
    if scored_df.empty:
        return

    # Only show active criteria (those the user hasn't excluded)
    active_criteria = {k: v for k, v in CRITERIA.items() if k in weights}

    score_cols = [v["col"] for v in active_criteria.values()]
    label_map = {v["col"]: v["label"] for v in active_criteria.values()}

    # Relabel the majors column to reflect the chosen major
    if selected_major != "general" and "majors" in active_criteria:
        major_label = MAJORS.get(selected_major, "Majors/Programs")
        label_map["score_majors"] = major_label

    display_df = scored_df[["name"] + score_cols + ["weighted_score"]].copy()
    display_df = display_df.rename(columns={**label_map, "name": "College", "weighted_score": "Total Score"})
    display_df = display_df.set_index("College")

    display_df = display_df.round(1)

    style_cols = [label_map.get(c, c) for c in score_cols] + ["Total Score"]

    styled = (
        display_df.style
        .background_gradient(
            subset=style_cols,
            cmap="RdYlGn",
            vmin=0,
            vmax=100,
        )
        .format("{:.1f}", na_rep="N/A", subset=style_cols)
    )

    st.dataframe(styled, use_container_width=True, height=min(100 + 40 * len(display_df), 600))

    st.caption(
        "Scores are on a 0–100 scale. Green = strong, red = weak. "
        "Niche-based scores (campus life, food, etc.) are converted from A+–F letter grades. "
        "Graduation rate is scaled relative to the schools you selected — 100 means best among your picks, not best overall. "
        "N/A means no data was available for that school."
    )
