"""
Rankings view: sorted bar chart + numbered list.
"""

import pandas as pd
import plotly.express as px
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import CRITERIA, QB_URLS


def render_rankings(scored_df: pd.DataFrame, weights: dict):
    """Render a ranked list and bar chart based on weighted scores."""
    if scored_df.empty:
        return

    ranked = (
        scored_df[["name", "weighted_score"]]
        .dropna(subset=["weighted_score"])
        .sort_values("weighted_score", ascending=False)
        .reset_index(drop=True)
    )
    ranked.index += 1  # 1-based ranking

    if ranked.empty:
        st.warning("No scores available for the selected colleges.")
        return

    # Bar chart
    fig = px.bar(
        ranked,
        x="weighted_score",
        y="name",
        orientation="h",
        range_x=[0, 100],
        title="Your Personalized College Ranking",
        labels={"weighted_score": "Weighted Score (0–100)", "name": "College"},
        color="weighted_score",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=50,
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
        coloraxis_showscale=False,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
        height=max(300, 60 * len(ranked)),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top college QuestBridge link
    top_name = ranked.iloc[0]["name"]
    top_url = QB_URLS.get(top_name)
    if top_url:
        st.success(f"**Your #1 match: {top_name}**")
        st.link_button(f"View {top_name} on QuestBridge", top_url)
    st.divider()

    # Top 3 medal cards
    st.subheader("Ranked List")
    top3 = ranked.head(3)
    card_styles = [
        ("🥇", "gold"),
        ("🥈", "silver"),
        ("🥉", "bronze"),
    ]
    cols = st.columns(min(len(top3), 3))
    for i, (rank, row) in enumerate(top3.iterrows()):
        emoji, style = card_styles[i]
        with cols[i]:
            st.markdown(f"""
<div class="medal-card {style}">
  <div class="medal-emoji">{emoji}</div>
  <div class="college-name">{row['name']}</div>
  <div class="score-badge">{row['weighted_score']:.1f} / 100</div>
</div>
""", unsafe_allow_html=True)

    # Remaining colleges (rank 4+)
    rest = ranked.iloc[3:]
    if not rest.empty:
        st.write("")
        for rank, row in rest.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**#{rank} {row['name']}**")
            with col2:
                st.metric(label="Score", label_visibility="collapsed", value=f"{row['weighted_score']:.1f}/100")

    st.caption(
        "Rankings update instantly as you change weights or add/remove colleges in the sidebar. "
        "Try adjusting what matters most to you to see how the order shifts."
    )

    # Show the active weight breakdown
    with st.expander("Active weight breakdown"):
        for key, crit in CRITERIA.items():
            pct = weights.get(key, 0) * 100
            if pct > 0.1:
                st.write(f"- **{crit['label']}**: {pct:.1f}%")
