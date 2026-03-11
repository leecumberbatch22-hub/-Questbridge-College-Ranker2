"""
Weight sliders with a hard 100% budget.

Each slider's maximum is dynamically capped so the total can never exceed 100%.
Unchecked criteria are excluded entirely from scoring and the comparison table.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import CRITERIA

# Integer defaults that sum to exactly 100 across 11 criteria
_DEFAULTS = {
    "campus_life":     10,
    "food":             9,
    "location":        10,
    "majors":          10,
    "dorms":            9,
    "social":           9,
    "diversity":        9,
    "grad_rate":        9,
    "acceptance_rate":  9,
    "faculty_ratio":    9,
    "median_earnings":  7,
}


def render_sliders() -> dict:
    """
    Renders a checkbox + slider per criterion with a hard 100% budget.
    - Unchecked criteria are removed from scoring and the table.
    - Each slider's max is capped so the total can never exceed 100%.
    Returns dict {criterion_key: fraction} for active criteria, fractions sum to 1.0.
    """
    st.subheader("Adjust Weights")
    st.caption(
        "Each slider controls how much that factor influences your final score. "
        "Your budget is 100% — raising one criterion limits others. "
        "Uncheck a criterion to remove it from scoring and the table entirely."
    )

    # Reset button
    if st.button("↺ Reset to defaults", use_container_width=True):
        for key in CRITERIA:
            st.session_state[f"slider_{key}"] = _DEFAULTS.get(key, 9)
            st.session_state[f"check_{key}"] = True
        st.rerun()

    # ── Read current slider values from session state (set by previous render) ──
    current = {
        key: int(st.session_state.get(f"slider_{key}", _DEFAULTS.get(key, 11)))
        for key in CRITERIA
    }

    # ── Determine which criteria are active (from previous checkbox state) ──
    active_keys = [
        k for k in CRITERIA
        if st.session_state.get(f"check_{k}", True)
    ]

    # ── Render each criterion ──
    raw_weights = {}
    for key, crit in CRITERIA.items():
        col_check, col_slide = st.columns([1, 4])

        with col_check:
            is_active = st.checkbox(
                label=" ",
                value=True,
                key=f"check_{key}",
                label_visibility="collapsed",
            )

        with col_slide:
            if is_active:
                cur_val = current[key]
                # Budget remaining = 100 minus every OTHER active slider's current value
                other_total = sum(
                    current[k] for k in active_keys if k != key
                )
                budget_for_this = max(0, 100 - other_total)

                if budget_for_this == 0 and cur_val == 0:
                    # Budget fully used by other criteria — show as locked at 0
                    st.markdown(f"{crit['label']}: **0%** *(budget full)*")
                    raw_weights[key] = 0
                else:
                    max_val = max(cur_val, budget_for_this, 1)
                    raw_weights[key] = st.slider(
                        label=crit["label"],
                        min_value=0,
                        max_value=max_val,
                        value=cur_val,
                        step=1,
                        key=f"slider_{key}",
                    )
            else:
                st.markdown(f"~~{crit['label']}~~", help="Excluded from scoring")

    # ── Total display ──
    total = sum(raw_weights.values())
    remaining = 100 - total

    if not raw_weights:
        st.warning("All criteria removed — please enable at least one.")
        n = len(CRITERIA)
        return {k: 1.0 / n for k in CRITERIA}

    # Progress bar
    pct = min(total, 100)
    if total == 100:
        bar_color = "#2ecc71"
        label = "Budget: 100% ✓"
    elif total == 0:
        bar_color = "#e74c3c"
        label = f"Budget: 0% used — {remaining}% remaining"
    else:
        bar_color = "#3498db"
        label = f"Budget: {total}% used — {remaining}% remaining"

    st.markdown(f"""
<div class="budget-bar-wrap">
  <div class="budget-bar-bg">
    <div class="budget-bar-fill" style="width:{pct}%;background:{bar_color};"></div>
  </div>
  <div class="budget-label">{label}</div>
</div>
""", unsafe_allow_html=True)

    if total == 0:
        n = len(raw_weights)
        st.warning("All weights are 0 — using equal weights.")
        return {k: 1.0 / n for k in raw_weights}

    return {k: v / total for k, v in raw_weights.items()}
