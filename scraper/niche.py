"""
Niche.com scraper for college quality grades.

Strategy:
1. Attempt to scrape the school's Niche page for letter grades.
2. If blocked (403/429) or grades not found, fall back to niche_manual_fallback.json.

The manual fallback is a one-time effort — Niche grades change slowly (annually).
"""

import json
import os
import random
import sys
import time

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import QUESTBRIDGE_COLLEGES, NICHE_RAW_PATH, NICHE_FALLBACK_PATH

try:
    from fake_useragent import UserAgent
    _ua = UserAgent()
    def get_user_agent():
        return _ua.random
except Exception:
    def get_user_agent():
        return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


NICHE_BASE = "https://www.niche.com/colleges"

# Map Niche page section names to our internal keys
NICHE_SECTION_MAP = {
    "Academics":    "majors",
    "Value":        None,       # skip
    "Student Life": "campus_life",
    "Housing":      "dorms",
    "Food":         "food",
    "Social":       "social",
    "Diversity":    "diversity",
    "Location":     "location",
}


def _parse_grades(html: str) -> dict:
    """Parse letter grades from a Niche school page HTML."""
    soup = BeautifulSoup(html, "lxml")
    grades = {}

    # Niche renders grades in elements with class containing "niche__grade" or similar.
    # Look for <div> blocks that have a section label and a grade nearby.
    # Strategy: find all grade badges/elements and map them to categories.

    # Try finding grade report cards — Niche uses a consistent structure
    # with data-testid="badge-icon" or class patterns
    for section_tag in soup.find_all(["section", "div"], attrs={"data-testid": True}):
        testid = section_tag.get("data-testid", "")
        # Grade report sections have testids like "ranking-badge"
        grade_el = section_tag.find(class_=lambda c: c and "grade" in c.lower())
        if grade_el:
            grade_text = grade_el.get_text(strip=True)
            label_el = section_tag.find(["h2", "h3", "h4", "span"],
                                         class_=lambda c: c and "title" in c.lower())
            if label_el:
                label = label_el.get_text(strip=True)
                key = NICHE_SECTION_MAP.get(label)
                if key:
                    grades[key] = grade_text

    # Fallback: scan all elements that look like grade badges (A+, A, B+, etc.)
    if not grades:
        import re
        grade_pattern = re.compile(r"^[A-D][+-]?$|^F$")
        for el in soup.find_all(class_=lambda c: c and ("grade" in c.lower() or "badge" in c.lower())):
            text = el.get_text(strip=True)
            if grade_pattern.match(text):
                # Try to find nearby label
                parent = el.parent
                if parent:
                    label_el = parent.find(["h2", "h3", "h4", "p", "span"])
                    if label_el and label_el != el:
                        label = label_el.get_text(strip=True)
                        key = NICHE_SECTION_MAP.get(label)
                        if key and key not in grades:
                            grades[key] = text

    return grades


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=5, max=30),
    retry=retry_if_exception_type(requests.RequestException),
    reraise=False,
)
def _fetch_niche_page(slug: str):
    """Fetch a single Niche college page. Returns HTML string or None."""
    url = f"{NICHE_BASE}/{slug}/"
    headers = {
        "User-Agent": get_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    resp = requests.get(url, headers=headers, timeout=20)
    if resp.status_code in (403, 429):
        print(f"    [BLOCKED] {slug} (HTTP {resp.status_code}) — will use fallback")
        return None
    resp.raise_for_status()
    return resp.text


def scrape_school(slug: str) -> dict:
    """Scrape Niche grades for one school. Returns dict of grades (may be empty)."""
    html = _fetch_niche_page(slug)
    if not html:
        return {}
    grades = _parse_grades(html)
    return grades


def load_fallback() -> dict:
    """Load the manually-curated fallback JSON file."""
    if not os.path.exists(NICHE_FALLBACK_PATH):
        return {}
    with open(NICHE_FALLBACK_PATH) as f:
        return json.load(f)


def scrape_all() -> dict:
    """
    Scrape Niche for all Questbridge schools.
    Uses fallback data for any school that can't be scraped.
    Returns dict keyed by slug.
    """
    fallback = load_fallback()
    results = {}
    total = len(QUESTBRIDGE_COLLEGES)

    print(f"Scraping Niche.com for {total} schools...")
    for i, college in enumerate(QUESTBRIDGE_COLLEGES, 1):
        slug = college["slug"]
        print(f"  [{i}/{total}] {college['name']}", end="", flush=True)

        grades = scrape_school(slug)

        if grades:
            # Fill any missing fields from fallback
            fallback_grades = fallback.get(slug, {})
            for key in ["campus_life", "food", "dorms", "social", "diversity", "location", "majors"]:
                if key not in grades and key in fallback_grades:
                    grades[key] = fallback_grades[key]
            print(f" → scraped ({len(grades)} grades)")
            results[slug] = grades
        elif slug in fallback:
            print(f" → using fallback ({len(fallback[slug])} grades)")
            results[slug] = fallback[slug]
        else:
            print(f" → no data available")
            results[slug] = {}

        # Polite delay between requests
        time.sleep(random.uniform(2.0, 3.5))

    os.makedirs(os.path.dirname(NICHE_RAW_PATH), exist_ok=True)
    with open(NICHE_RAW_PATH, "w") as f:
        json.dump(results, f, indent=2)

    found = sum(1 for v in results.values() if v)
    print(f"\nNiche: {found}/{total} schools have data → saved to {NICHE_RAW_PATH}")
    return results


if __name__ == "__main__":
    scrape_all()
