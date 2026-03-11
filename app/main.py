"""
Questbridge College Ranker — Main Streamlit App

Run with:
    streamlit run app/main.py
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import load_data, calculate_all_scores
from app.components.college_selector import render_selector
from app.components.weight_sliders import render_sliders
from app.components.comparison_table import render_comparison
from app.components.ranking_view import render_rankings
from config import MAJORS, CRITERIA, CRITERIA_DESCRIPTIONS

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="Questbridge College Ranker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Header ───────────────────────────────────────────────────
st.title("🎓 Questbridge College Ranker")
st.markdown(
    "Compare Questbridge partner colleges across criteria that matter to you. "
    "Adjust the weights to personalize your ranking."
)
st.divider()

# ── How to use ────────────────────────────────────────────────
with st.expander("How to use this tool"):
    st.markdown("""
**Step 1 — Select colleges:** Pick 2 or more Questbridge partner schools from the sidebar on the left. You can add as many as all 55.

**Step 2 — Focus your major (optional):** Use the Major Focus dropdown in the sidebar to choose a specific field like Engineering or Political Science. The Majors score will update to reflect each school's strength in that area instead of using a general rating.

**Step 3 — Set your weights:** Drag the sliders to reflect what matters most to you. You have a 100% budget — every point you give to one criterion takes away from others. Uncheck a criterion to remove it from scoring entirely.

**Step 4 — Read your results:** The Rankings tab shows your personalized order from best to worst, along with a bar chart. Click "Score Breakdown" to see how each school performed on every individual criterion.

**Step 5 — Explore your #1 match:** A green banner at the top of the Rankings tab shows your top school with a direct link to their official Questbridge partner page.
""")

# ── About the data ────────────────────────────────────────────
with st.expander("Where does the data come from?"):
    st.markdown("""
**Niche.com grades** (Campus Life, Food, Location, Dorms, Social Scene, Diversity, Majors)

Niche.com publishes A+–F letter grades for each school across dozens of student experience categories. This tool converts those to a 0–100 numeric scale: A+ = 100, A = 95, A- = 90, B+ = 85, B = 80, and so on in 5-point steps. Small tiebreaker offsets (less than 1 point) are applied so that no two schools ever share the exact same score within a category.

**Graduation Rate** (U.S. Department of Education — College Scorecard)

The 4-year graduation rate comes from the federal College Scorecard public dataset. It is scaled *relative to the schools you have selected* — the school with the highest graduation rate in your comparison scores 100, and the lowest scores 0. This means a school's graduation rate score will shift depending on which schools you include.

**Per-Major scores** (Major Focus feature)

When you select a specific major, each school is rated on its academic strength in that field using the same A+–F → 0–100 conversion as Niche grades. These ratings are based on published academic rankings and program reputation for each discipline.
""")

# ── Criteria explanations ─────────────────────────────────────
with st.expander("What does each criterion mean?"):
    for key, crit in CRITERIA.items():
        st.markdown(f"**{crit['label']}** — {CRITERIA_DESCRIPTIONS.get(key, '')}")

st.divider()

# ── Load data ─────────────────────────────────────────────────
df = load_data()

# ── Sidebar: controls ────────────────────────────────────────
with st.sidebar:
    selected_colleges = render_selector(df)
    st.divider()

    # Major selector
    st.subheader("Major Focus")
    st.caption("Pick a major to rank schools by strength in that field.")
    major_options = {"general": "General / All Majors"}
    major_options.update(MAJORS)
    selected_major = st.selectbox(
        label="Major:",
        options=list(major_options.keys()),
        format_func=lambda k: major_options[k],
        key="major_selector",
    )
    st.divider()

    weights = render_sliders()

# ── Main area ─────────────────────────────────────────────────
if not selected_colleges:
    st.info(
        "**Get started:** Select colleges from the sidebar on the left, "
        "then adjust the weights to reflect what matters most to you."
    )

    # Show all colleges as a reference table
    with st.expander("View all Questbridge partner colleges in the database"):
        preview = df[["name", "city", "state"]].sort_values("name")
        st.dataframe(preview, use_container_width=True, hide_index=True)

elif len(selected_colleges) == 1:
    st.warning("Select at least 2 colleges to compare them.")

else:
    # Swap in the major-specific score if a major is selected
    df_to_score = df.copy()
    if selected_major != "general":
        major_col = f"score_major_{selected_major}"
        if major_col in df_to_score.columns:
            df_to_score["score_majors"] = df_to_score[major_col]

    scored_df = calculate_all_scores(df_to_score, selected_colleges, weights)

    tab1, tab2 = st.tabs(["Rankings", "Score Breakdown"])

    with tab1:
        render_rankings(scored_df, weights)

    with tab2:
        label = MAJORS.get(selected_major, "All Majors") if selected_major != "general" else "All Majors"
        st.subheader(f"Score Breakdown by Criterion  —  Major: {label}")
        render_comparison(scored_df, weights, selected_major)

# ── Footer ────────────────────────────────────────────────────
st.divider()
st.caption(
    "Data sourced from [Niche.com](https://www.niche.com) and the "
    "[U.S. Department of Education College Scorecard](https://collegescorecard.ed.gov). "
    "For personal, non-commercial use by Questbridge students only."
)