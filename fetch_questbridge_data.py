"""
QuestBridge Partner Schools — College Scorecard Data Fetcher
============================================================
Fetches data for all 55 QuestBridge partner schools from the
U.S. Department of Education's College Scorecard API.

SETUP:
  1. Get a free API key at: https://api.data.gov/signup/
  2. pip install requests
  3. Replace YOUR_API_KEY_HERE with your actual key
  4. Run: python fetch_questbridge_data.py

OUTPUT:
  questbridge_colleges.json  — full data for all 55 schools
  questbridge_colleges.csv   — spreadsheet-friendly version
"""

import requests
import json
import csv
import time

# ──────────────────────────────────────────────
# CONFIG — replace with your free API key from
#          https://api.data.gov/signup/
# ──────────────────────────────────────────────
API_KEY = "1zP0NaS83UJ4rRe7yUiT4vjktfa9UF3cHnI1w1Xp"
BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"

# ──────────────────────────────────────────────
# ALL 55 QUESTBRIDGE PARTNER SCHOOLS
# ──────────────────────────────────────────────
QUESTBRIDGE_SCHOOLS = [
    "Amherst College",
    "Barnard College",
    "Bates College",
    "Boston College",
    "Boston University",
    "Bowdoin College",
    "Brown University",
    "California Institute of Technology",
    "Carleton College",
    "Case Western Reserve University",
    "Claremont McKenna College",
    "Colby College",
    "Colgate University",
    "College of the Holy Cross",
    "Colorado College",
    "Columbia University",
    "Cornell University",
    "Dartmouth College",
    "Davidson College",
    "Denison University",
    "Duke University",
    "Emory University",
    "Grinnell College",
    "Hamilton College",
    "Harvard University",
    "Haverford College",
    "Johns Hopkins University",
    "Macalester College",
    "Massachusetts Institute of Technology",
    "Middlebury College",
    "Northwestern University",
    "Oberlin College",
    "Pomona College",
    "Princeton University",
    "Rice University",
    "Scripps College",
    "Skidmore College",
    "Smith College",
    "Stanford University",
    "Swarthmore College",
    "Tufts University",
    "University of Chicago",
    "University of Notre Dame",
    "University of Pennsylvania",
    "University of Richmond",
    "University of Southern California",
    "University of Virginia",
    "Vanderbilt University",
    "Vassar College",
    "Washington and Lee University",
    "Washington University in St. Louis",
    "Wellesley College",
    "Wesleyan University",
    "Williams College",
    "Yale University",
]

# ──────────────────────────────────────────────
# FIELDS TO FETCH FROM THE API
# These map to scoring criteria in the ranker
# ──────────────────────────────────────────────
FIELDS = ",".join([
    "school.name",
    "school.city",
    "school.state",
    "school.school_url",
    "school.ownership",                        # public/private
    "latest.student.size",                     # undergrad enrollment
    "latest.admissions.admission_rate.overall",# acceptance rate
    "latest.admissions.sat_scores.midpoint.critical_reading",
    "latest.admissions.sat_scores.midpoint.math",
    "latest.admissions.act_scores.midpoint.cumulative",
    "latest.cost.avg_net_price.private",       # avg net price (private)
    "latest.cost.avg_net_price.public",        # avg net price (public)
    "latest.aid.median_debt.completers.overall",  # median debt at graduation
    "latest.aid.pell_grant_rate",              # % students receiving Pell grants
    "latest.aid.federal_loan_rate",            # % students with federal loans
    "latest.completion.rate_suppressed.overall", # 4-year graduation rate
    "latest.earnings.10_yrs_after_entry.median", # median earnings 10 yrs out
    "latest.programs.cip_4_digit",             # available majors/programs
])


def fetch_school(name):
    """Fetch data for a single school by name."""
    params = {
        "api_key": API_KEY,
        "school.name": name,
        "fields": FIELDS,
        "_per_page": 1,
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if results:
            return results[0]
        else:
            print(f"  ⚠️  No results found for: {name}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"  ❌  Error fetching {name}: {e}")
        return None


def clean_school(raw, original_name):
    """Reshape raw API data into a clean, flat dictionary."""
    if not raw:
        return {"name": original_name, "error": "not found"}

    # Acceptance rate as percentage
    admit_rate = raw.get("latest.admissions.admission_rate.overall")
    admit_pct = round(admit_rate * 100, 1) if admit_rate else None

    # Average net price (try private first, then public)
    avg_price = (
        raw.get("latest.cost.avg_net_price.private")
        or raw.get("latest.cost.avg_net_price.public")
    )

    # Enrollment → size label
    size = raw.get("latest.student.size")
    if size:
        if size < 2500:
            size_label = "Small"
        elif size < 8000:
            size_label = "Medium"
        else:
            size_label = "Large"
    else:
        size_label = None

    # Ownership label
    ownership_map = {1: "Public", 2: "Private Nonprofit", 3: "Private For-Profit"}
    ownership = ownership_map.get(raw.get("school.ownership"), "Unknown")

    return {
        # Identity
        "name": raw.get("school.name", original_name),
        "city": raw.get("school.city"),
        "state": raw.get("school.state"),
        "website": raw.get("school.school_url"),
        "type": ownership,

        # Size
        "undergrad_enrollment": size,
        "size_label": size_label,

        # Admissions
        "acceptance_rate_pct": admit_pct,
        "sat_reading_midpoint": raw.get("latest.admissions.sat_scores.midpoint.critical_reading"),
        "sat_math_midpoint": raw.get("latest.admissions.sat_scores.midpoint.math"),
        "act_midpoint": raw.get("latest.admissions.act_scores.midpoint.cumulative"),

        # Financial Aid
        "avg_net_price_usd": avg_price,
        "pell_grant_rate_pct": round(raw.get("latest.aid.pell_grant_rate", 0) * 100, 1) if raw.get("latest.aid.pell_grant_rate") else None,
        "federal_loan_rate_pct": round(raw.get("latest.aid.federal_loan_rate", 0) * 100, 1) if raw.get("latest.aid.federal_loan_rate") else None,
        "median_debt_usd": raw.get("latest.aid.median_debt.completers.overall"),

        # Outcomes
        "graduation_rate_pct": round(raw.get("latest.completion.rate_suppressed.overall", 0) * 100, 1) if raw.get("latest.completion.rate_suppressed.overall") else None,
        "median_earnings_10yr_usd": raw.get("latest.earnings.10_yrs_after_entry.median"),
    }


def main():
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌  Please set your API key first!")
        print("   Get one free at: https://api.data.gov/signup/")
        return

    print("🎓 Fetching data for 55 QuestBridge partner schools...\n")
    all_schools = []

    for i, name in enumerate(QUESTBRIDGE_SCHOOLS, 1):
        print(f"[{i:02d}/55] Fetching: {name}")
        raw = fetch_school(name)
        school = clean_school(raw, name)
        all_schools.append(school)
        time.sleep(0.3)  # be polite to the API

    # ── Save as JSON ──────────────────────────
    json_path = "questbridge_colleges.json"
    with open(json_path, "w") as f:
        json.dump(all_schools, f, indent=2)
    print(f"\n✅  Saved JSON → {json_path}")

    # ── Save as CSV ───────────────────────────
    csv_path = "questbridge_colleges.csv"
    if all_schools:
        keys = [k for k in all_schools[0].keys() if k != "error"]
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_schools)
    print(f"✅  Saved CSV  → {csv_path}")

    # ── Summary ───────────────────────────────
    found = sum(1 for s in all_schools if "error" not in s)
    print(f"\n📊  Results: {found}/55 schools fetched successfully")
    print("\nFields collected per school:")
    print("  • Identity: name, city, state, website, type")
    print("  • Size: enrollment, size label (Small/Medium/Large)")
    print("  • Admissions: acceptance rate, SAT/ACT midpoints")
    print("  • Financial Aid: avg net price, Pell grant rate, median debt")
    print("  • Outcomes: graduation rate, median earnings (10yr)")
    print("\nNext step: use questbridge_colleges.json to power the ranker website!")


if __name__ == "__main__":
    main()
