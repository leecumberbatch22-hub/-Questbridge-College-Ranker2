"""
All normalization logic for converting raw data to 0-100 scores.
No dependencies on other project files — can be tested independently.
"""

import pandas as pd

# Niche letter grade → 0-100 score
GRADE_MAP = {
    "A+": 100, "A": 95, "A-": 90,
    "B+": 85,  "B": 80, "B-": 75,
    "C+": 70,  "C": 65, "C-": 60,
    "D+": 55,  "D": 50, "D-": 45,
    "F":  30,
}


def grade_to_score(grade: str) -> float:
    """Convert a Niche letter grade (e.g. 'A+', 'B-') to a 0-100 float.
    Returns NaN if grade is missing or unrecognized."""
    if not grade or not isinstance(grade, str):
        return float("nan")
    cleaned = grade.strip()
    return float(GRADE_MAP.get(cleaned, float("nan")))


def break_ties(series: pd.Series, step: float = 0.05) -> pd.Series:
    """Within each tied group, add tiny decreasing offsets so no two scores are equal.
    Ordering within a group is by row position (list order), which is roughly prestige order.
    Max offset across 41 schools sharing the same grade: ~2.0 points."""
    result = series.copy().astype(float)
    for val in series.dropna().unique():
        mask = series == val
        if mask.sum() > 1:
            for rank, idx in enumerate(mask[mask].index):
                result.at[idx] = val - (rank * step)
    return result


def normalize_minmax(series: pd.Series) -> pd.Series:
    """Scale a numeric Series to 0-100 using its own min/max range.
    If all values are the same, returns 50 for all."""
    min_val = series.min()
    max_val = series.max()
    if pd.isna(min_val) or pd.isna(max_val) or max_val == min_val:
        return pd.Series([50.0] * len(series), index=series.index)
    return ((series - min_val) / (max_val - min_val)) * 100.0


def normalize_financial_aid(series: pd.Series) -> pd.Series:
    """Invert and scale: lower net price = higher financial aid score."""
    inverted = series.max() - series
    return normalize_minmax(inverted)


def build_dataset(scorecard_raw: list, niche_raw: dict, major_scores: dict = None) -> pd.DataFrame:
    """
    Merge scorecard and niche data, normalize all fields, return final DataFrame.

    Args:
        scorecard_raw: List of dicts from College Scorecard API, one per college.
        niche_raw: Dict keyed by college slug, each value a dict of raw grades.

    Returns:
        DataFrame with identity columns, raw columns, and score_ columns.
    """
    if major_scores is None:
        major_scores = {}

    rows = []

    for entry in scorecard_raw:
        college_id = str(entry.get("id", ""))
        name = entry.get("school.name", "")
        slug = entry.get("slug", "")
        city = entry.get("school.city", "")
        state = entry.get("school.state", "")

        raw_grad     = entry.get("latest.completion.completion_rate_4yr_150nt")
        raw_price    = entry.get("latest.cost.avg_net_price.overall")
        raw_admit    = entry.get("latest.admissions.admission_rate.overall")
        raw_faculty  = entry.get("latest.student.faculty_ratio")
        raw_earnings = entry.get("latest.earnings.10_yrs_after_entry.median")

        niche = niche_raw.get(slug, {})
        majors = major_scores.get(slug, {})
        source_flags = []
        if entry.get("_source") == "scorecard":
            source_flags.append("scorecard")
        if niche:
            source_flags.append("niche")

        row = {
            "college_id":            college_id,
            "name":                  name,
            "slug":                  slug,
            "city":                  city,
            "state":                 state,
            "raw_grad_rate_4yr":     float(raw_grad)     if raw_grad     is not None else float("nan"),
            "raw_net_price_avg":     float(raw_price)    if raw_price    is not None else float("nan"),
            "raw_admission_rate":    float(raw_admit)    if raw_admit    is not None else float("nan"),
            "raw_faculty_ratio":     float(raw_faculty)  if raw_faculty  is not None else float("nan"),
            "raw_median_earnings":   float(raw_earnings) if raw_earnings is not None else float("nan"),
            "raw_niche_campus_life": niche.get("campus_life", ""),
            "raw_niche_food":        niche.get("food", ""),
            "raw_niche_dorms":       niche.get("dorms", ""),
            "raw_niche_social":      niche.get("social", ""),
            "raw_niche_diversity":   niche.get("diversity", ""),
            "raw_niche_location":    niche.get("location", ""),
            "raw_niche_majors":      niche.get("majors", ""),
            "data_source_flags":     ",".join(source_flags) if source_flags else "none",
        }
        # Per-major raw grades
        for major_key in ["engineering", "computer_science", "political_science",
                          "economics", "biology", "english", "mathematics", "art_music"]:
            row[f"raw_major_{major_key}"] = majors.get(major_key, "")
        rows.append(row)

    df = pd.DataFrame(rows)

    # Apply Niche grade normalization
    niche_field_map = {
        "raw_niche_campus_life": "score_campus_life",
        "raw_niche_food":        "score_food",
        "raw_niche_dorms":       "score_dorms",
        "raw_niche_social":      "score_social",
        "raw_niche_diversity":   "score_diversity",
        "raw_niche_location":    "score_location",
        "raw_niche_majors":      "score_majors",
    }
    for raw_col, score_col in niche_field_map.items():
        df[score_col] = df[raw_col].apply(grade_to_score)

    # Apply Scorecard normalization (cohort-relative min-max)
    df["score_grad_rate"] = normalize_minmax(df["raw_grad_rate_4yr"].astype(float))
    df["score_financial_aid"] = normalize_financial_aid(df["raw_net_price_avg"].astype(float))

    # New Scorecard criteria
    # Acceptance rate: inverted (lower rate = more selective = higher score)
    admit_series = df["raw_admission_rate"].astype(float)
    df["score_acceptance_rate"] = normalize_minmax(admit_series.max() - admit_series)

    # Faculty ratio: inverted (lower ratio = more access = higher score)
    faculty_series = df["raw_faculty_ratio"].astype(float)
    df["score_faculty_ratio"] = normalize_minmax(faculty_series.max() - faculty_series)

    # Median earnings: direct scale (higher = better)
    df["score_median_earnings"] = normalize_minmax(df["raw_median_earnings"].astype(float))

    # Per-major score columns
    for major_key in ["engineering", "computer_science", "political_science",
                      "economics", "biology", "english", "mathematics", "art_music"]:
        df[f"score_major_{major_key}"] = df[f"raw_major_{major_key}"].apply(grade_to_score)
        df[f"score_major_{major_key}"] = break_ties(df[f"score_major_{major_key}"])

    # Break ties in all Niche-derived score columns so no two schools share the same score
    for score_col in ["score_campus_life", "score_food", "score_dorms", "score_social",
                      "score_diversity", "score_location", "score_majors"]:
        df[score_col] = break_ties(df[score_col])

    # Record which score fields are missing for each school
    score_cols = [
        "score_campus_life", "score_food", "score_location", "score_majors",
        "score_dorms", "score_social", "score_diversity", "score_grad_rate",
        "score_acceptance_rate", "score_faculty_ratio", "score_median_earnings",
    ]
    df["missing_fields"] = df[score_cols].apply(
        lambda row: ",".join([c for c in score_cols if pd.isna(row[c])]), axis=1
    )

    from datetime import date
    df["last_updated"] = date.today().isoformat()

    return df
