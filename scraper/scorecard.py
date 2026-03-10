"""
College Scorecard API client.
Free API key: https://api.data.gov/signup/

Fetches graduation rate and net price data for all Questbridge partner schools.
"""

import json
import time
import os
import sys

import requests
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import QUESTBRIDGE_COLLEGES, SCORECARD_RAW_PATH

load_dotenv()

SCORECARD_BASE = "https://api.collegescorecard.ed.gov/v1/schools"
FIELDS = ",".join([
    "id",
    "school.name",
    "school.city",
    "school.state",
    "latest.completion.completion_rate_4yr_150nt",
    "latest.cost.avg_net_price.overall",
    "latest.admissions.admission_rate.overall",
    "latest.student.size",
    "latest.student.faculty_ratio",
    "latest.earnings.10_yrs_after_entry.median",
])


def fetch_school(search_name: str, api_key: str):
    """Fetch one school from the College Scorecard API by name search."""
    params = {
        "api_key": api_key,
        "school.name": search_name,
        "fields": FIELDS,
        "_per_page": 1,
    }
    try:
        resp = requests.get(SCORECARD_BASE, params=params, timeout=15)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if results:
            return results[0]
        print(f"  [WARN] No results for: {search_name}")
        return None
    except requests.RequestException as e:
        print(f"  [ERROR] Failed to fetch {search_name}: {e}")
        return None


def fetch_all() -> list[dict]:
    """Fetch all Questbridge schools and save to scorecard_raw.json."""
    api_key = os.getenv("SCORECARD_API_KEY")
    if not api_key or api_key == "your_key_here":
        print("[ERROR] SCORECARD_API_KEY not set in .env file.")
        print("  Get a free key at: https://api.data.gov/signup/")
        print("  Then add it to your .env file as: SCORECARD_API_KEY=yourkey")
        return []

    results = []
    total = len(QUESTBRIDGE_COLLEGES)
    print(f"Fetching College Scorecard data for {total} schools...")

    for i, college in enumerate(QUESTBRIDGE_COLLEGES, 1):
        print(f"  [{i}/{total}] {college['name']}")
        data = fetch_school(college["search"], api_key)
        if data:
            data["slug"] = college["slug"]
            data["_source"] = "scorecard"
            results.append(data)
        time.sleep(0.2)  # Stay well within API rate limits

    os.makedirs(os.path.dirname(SCORECARD_RAW_PATH), exist_ok=True)
    with open(SCORECARD_RAW_PATH, "w") as f:
        json.dump(results, f, indent=2)

    found = len(results)
    print(f"\nScorecard: {found}/{total} schools fetched → saved to {SCORECARD_RAW_PATH}")
    return results


if __name__ == "__main__":
    fetch_all()
