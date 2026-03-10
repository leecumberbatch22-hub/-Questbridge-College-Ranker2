"""
Pipeline orchestrator: runs all scrapers and builds colleges.csv.

Usage:
    python -m scraper.pipeline
    python -m scraper.pipeline --scorecard-only   # skip Niche scraping, use fallback only
    python -m scraper.pipeline --niche-only        # skip Scorecard, use existing raw data
    python -m scraper.pipeline --fallback-only     # no network calls, use cached/fallback data
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SCORECARD_RAW_PATH, NICHE_RAW_PATH, NICHE_FALLBACK_PATH, COLLEGES_CSV_PATH, MAJOR_SCORES_PATH, SCORECARD_FALLBACK_PATH
from scraper.normalizer import build_dataset


def load_json(path: str):
    with open(path) as f:
        return json.load(f)


def run(scorecard_only=False, niche_only=False, fallback_only=False):
    print("=" * 55)
    print("  Questbridge College Ranker — Data Pipeline")
    print("=" * 55)

    # ── Step 1: College Scorecard ─────────────────────────────
    if (fallback_only or niche_only) and os.path.exists(SCORECARD_RAW_PATH):
        print("\n[1/3] Loading cached Scorecard data...")
        scorecard_raw = load_json(SCORECARD_RAW_PATH)
    elif fallback_only:
        # No cached file and no API key — build stub entries from config
        print("\n[1/3] No cached Scorecard data — building stubs from college list...")
        from config import QUESTBRIDGE_COLLEGES
        sc_fallback = load_json(SCORECARD_FALLBACK_PATH) if os.path.exists(SCORECARD_FALLBACK_PATH) else {}
        scorecard_raw = [
            {
                "id": str(i),
                "school.name": c["name"],
                "school.city": "",
                "school.state": "",
                "slug": c["slug"],
                "_source": "stub",
                "latest.completion.completion_rate_4yr_150nt": None,
                "latest.cost.avg_net_price.overall": None,
                "latest.admissions.admission_rate.overall": sc_fallback.get(c["slug"], {}).get("admission_rate"),
                "latest.student.faculty_ratio": sc_fallback.get(c["slug"], {}).get("faculty_ratio"),
                "latest.earnings.10_yrs_after_entry.median": sc_fallback.get(c["slug"], {}).get("median_earnings"),
            }
            for i, c in enumerate(QUESTBRIDGE_COLLEGES, 1)
        ]
    else:
        print("\n[1/3] Fetching College Scorecard data...")
        from scraper.scorecard import fetch_all
        scorecard_raw = fetch_all()
        if not scorecard_raw:
            print("\n[!] Scorecard fetch failed or returned no data.")
            print("    Check your API key in .env and try again.")
            print("    To use cached data, run: python -m scraper.pipeline --fallback-only")
            sys.exit(1)

    # ── Step 2: Niche ─────────────────────────────────────────
    if scorecard_only or fallback_only:
        print("\n[2/3] Using Niche fallback data only (no scraping)...")
        if os.path.exists(NICHE_FALLBACK_PATH):
            niche_raw = load_json(NICHE_FALLBACK_PATH)
        else:
            print("  [WARN] Fallback file not found — Niche data will be missing.")
            niche_raw = {}
    elif os.path.exists(NICHE_RAW_PATH) and niche_only:
        print("\n[2/3] Loading cached Niche data (--niche-only mode)...")
        niche_raw = load_json(NICHE_RAW_PATH)
    else:
        print("\n[2/3] Scraping Niche.com...")
        from scraper.niche import scrape_all
        niche_raw = scrape_all()

    # ── Step 3: Normalize and build CSV ───────────────────────
    print("\n[3/3] Normalizing and building colleges.csv...")
    major_scores = load_json(MAJOR_SCORES_PATH) if os.path.exists(MAJOR_SCORES_PATH) else {}
    df = build_dataset(scorecard_raw, niche_raw, major_scores)

    os.makedirs(os.path.dirname(COLLEGES_CSV_PATH), exist_ok=True)
    df.to_csv(COLLEGES_CSV_PATH, index=False)

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "=" * 55)
    print(f"  Done! {len(df)} colleges saved to {COLLEGES_CSV_PATH}")
    print()

    score_cols = [
        "score_campus_life", "score_food", "score_location", "score_majors",
        "score_dorms", "score_social", "score_diversity", "score_grad_rate",
    ]
    import pandas as pd
    issues = df[df["missing_fields"].str.len() > 0][["name", "missing_fields"]]
    if issues.empty:
        print("  All criteria data complete — no missing fields!")
    else:
        print(f"  {len(issues)} school(s) have missing data:")
        for _, row in issues.iterrows():
            print(f"    {row['name']}: {row['missing_fields']}")

    print()
    print("  Run the app with:")
    print("    streamlit run app/main.py")
    print("=" * 55)


if __name__ == "__main__":
    args = sys.argv[1:]
    run(
        scorecard_only="--scorecard-only" in args,
        niche_only="--niche-only" in args,
        fallback_only="--fallback-only" in args,
    )
