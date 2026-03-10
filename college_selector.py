"""College selection widget."""

import pandas as pd
import streamlit as st


def render_selector(df: pd.DataFrame) -> list[str]:
    """
    Renders a searchable multiselect for college names.
    Returns list of selected college names.
    """
    st.subheader("Select Colleges")
    all_names = sorted(df["name"].dropna().tolist())

    selected = st.multiselect(
        label="Search and pick colleges to compare (min 2):",
        options=all_names,
        default=[],
        placeholder="Type to search...",
    )

    if selected:
        st.caption(f"{len(selected)} college(s) selected. Rankings update instantly as you add or remove schools.")
    else:
        st.caption("All 41 Questbridge partner colleges are available. Pick at least 2 to compare.")

    return selected
