"""
Central configuration: Questbridge college list, scoring criteria, and default weights.
Every other module imports from here.
"""

QUESTBRIDGE_COLLEGES = [
    {"name": "Massachusetts Institute of Technology", "slug": "massachusetts-institute-of-technology", "search": "Massachusetts Institute of Technology", "qb_slug": "massachusetts-institute-of-technology"},
    {"name": "Stanford University",                   "slug": "stanford-university",                    "search": "Stanford University",                   "qb_slug": "stanford-university"},
    {"name": "Yale University",                       "slug": "yale-university",                        "search": "Yale University",                       "qb_slug": "yale-university"},
    {"name": "Princeton University",                  "slug": "princeton-university",                   "search": "Princeton University",                  "qb_slug": "princeton-university"},
    {"name": "Harvard University",                    "slug": "harvard-university",                     "search": "Harvard University",                    "qb_slug": "harvard-college"},
    {"name": "Duke University",                       "slug": "duke-university",                        "search": "Duke University",                       "qb_slug": "duke-university"},
    {"name": "Vanderbilt University",                 "slug": "vanderbilt-university",                  "search": "Vanderbilt University",                 "qb_slug": "vanderbilt-university"},
    {"name": "Rice University",                       "slug": "rice-university",                        "search": "Rice University",                       "qb_slug": "rice-university"},
    {"name": "Emory University",                      "slug": "emory-university",                       "search": "Emory University",                      "qb_slug": "emory-university"},
    {"name": "University of Notre Dame",              "slug": "university-of-notre-dame",               "search": "University of Notre Dame",              "qb_slug": "university-of-notre-dame"},
    {"name": "Georgetown University",                 "slug": "georgetown-university",                  "search": "Georgetown University",                 "qb_slug": "georgetown-university"},
    {"name": "Tufts University",                      "slug": "tufts-university",                       "search": "Tufts University",                      "qb_slug": "tufts-university"},
    {"name": "Tulane University",                     "slug": "tulane-university",                      "search": "Tulane University",                     "qb_slug": "tulane-university"},
    {"name": "University of Chicago",                 "slug": "university-of-chicago",                  "search": "University of Chicago",                 "qb_slug": "university-of-chicago"},
    {"name": "Columbia University",                   "slug": "columbia-university-in-the-city-of-new-york", "search": "Columbia University",              "qb_slug": "columbia-university"},
    {"name": "Brown University",                      "slug": "brown-university",                       "search": "Brown University",                      "qb_slug": "brown-university"},
    {"name": "Dartmouth College",                     "slug": "dartmouth-college",                      "search": "Dartmouth College",                     "qb_slug": "dartmouth-college"},
    {"name": "Cornell University",                    "slug": "cornell-university",                     "search": "Cornell University",                    "qb_slug": "cornell-university"},
    {"name": "University of Pennsylvania",            "slug": "university-of-pennsylvania",             "search": "University of Pennsylvania",            "qb_slug": "university-of-pennsylvania"},
    {"name": "California Institute of Technology",    "slug": "california-institute-of-technology",     "search": "California Institute of Technology",    "qb_slug": "california-institute-of-technology"},
    {"name": "Davidson College",                      "slug": "davidson-college",                       "search": "Davidson College",                      "qb_slug": "davidson-college"},
    {"name": "Grinnell College",                      "slug": "grinnell-college",                       "search": "Grinnell College",                      "qb_slug": "grinnell-college"},
    {"name": "Haverford College",                     "slug": "haverford-college",                      "search": "Haverford College",                      "qb_slug": "haverford-college"},
    {"name": "Pomona College",                        "slug": "pomona-college",                         "search": "Pomona College",                        "qb_slug": "pomona-college"},
    {"name": "Swarthmore College",                    "slug": "swarthmore-college",                     "search": "Swarthmore College",                    "qb_slug": "swarthmore-college"},
    {"name": "Wellesley College",                     "slug": "wellesley-college",                      "search": "Wellesley College",                     "qb_slug": "wellesley-college"},
    {"name": "Smith College",                         "slug": "smith-college",                          "search": "Smith College",                         "qb_slug": "smith-college"},
    {"name": "Amherst College",                       "slug": "amherst-college",                        "search": "Amherst College",                       "qb_slug": "amherst-college"},
    {"name": "Williams College",                      "slug": "williams-college",                       "search": "Williams College",                      "qb_slug": "williams-college"},
    {"name": "Bowdoin College",                       "slug": "bowdoin-college",                        "search": "Bowdoin College",                       "qb_slug": "bowdoin-college"},
    {"name": "Colby College",                         "slug": "colby-college",                          "search": "Colby College",                         "qb_slug": "colby-college"},
    {"name": "Middlebury College",                    "slug": "middlebury-college",                     "search": "Middlebury College",                    "qb_slug": "middlebury-college"},
    {"name": "Vassar College",                        "slug": "vassar-college",                         "search": "Vassar College",                        "qb_slug": "vassar-college"},
    {"name": "Carleton College",                      "slug": "carleton-college",                       "search": "Carleton College",                      "qb_slug": "carleton-college"},
    {"name": "Oberlin College",                       "slug": "oberlin-college",                        "search": "Oberlin College",                       "qb_slug": "oberlin-college"},
    {"name": "Kenyon College",                        "slug": "kenyon-college",                         "search": "Kenyon College",                        "qb_slug": "kenyon-college"},
    {"name": "Macalester College",                    "slug": "macalester-college",                     "search": "Macalester College",                    "qb_slug": "macalester-college"},
    {"name": "Colorado College",                      "slug": "colorado-college",                       "search": "Colorado College",                      "qb_slug": "colorado-college"},
    {"name": "University of Rochester",               "slug": "university-of-rochester",                "search": "University of Rochester",               "qb_slug": "university-of-rochester"},
    {"name": "Case Western Reserve University",       "slug": "case-western-reserve-university",        "search": "Case Western Reserve University",       "qb_slug": "case-western-reserve-university"},
    {"name": "Wake Forest University",                "slug": "wake-forest-university",                 "search": "Wake Forest University",                "qb_slug": "wake-forest-university"},
]

# Name → QuestBridge URL lookup
QB_URLS = {
    c["name"]: f"https://www.questbridge.org/partners/college-partners/{c['qb_slug']}"
    for c in QUESTBRIDGE_COLLEGES
}

# Scoring criteria: key → display label, normalized column name, data source
CRITERIA = {
    "campus_life":      {"label": "Campus Life",           "col": "score_campus_life",      "source": "niche"},
    "food":             {"label": "Food",                   "col": "score_food",             "source": "niche"},
    "location":         {"label": "Location/City",          "col": "score_location",         "source": "niche"},
    "majors":           {"label": "Majors/Programs",        "col": "score_majors",           "source": "niche"},
    "dorms":            {"label": "Dorms",                  "col": "score_dorms",            "source": "niche"},
    "social":           {"label": "Social Scene",           "col": "score_social",           "source": "niche"},
    "diversity":        {"label": "Diversity",              "col": "score_diversity",        "source": "niche"},
    "grad_rate":        {"label": "Graduation Rate",        "col": "score_grad_rate",        "source": "scorecard"},
    "acceptance_rate":  {"label": "Selectivity",            "col": "score_acceptance_rate",  "source": "scorecard"},
    "faculty_ratio":    {"label": "Student-Faculty Ratio",  "col": "score_faculty_ratio",    "source": "scorecard"},
    "median_earnings":  {"label": "Graduate Earnings",      "col": "score_median_earnings",  "source": "scorecard"},
}

# Descriptions shown in the "What does each criterion mean?" section
CRITERIA_DESCRIPTIONS = {
    "campus_life":     "Overall quality of student life on campus — clubs, events, traditions, and the general vibe.",
    "food":            "Quality and variety of dining halls and on-campus food options.",
    "location":        "The city or town the school is in — access to culture, jobs, nature, and things to do.",
    "majors":          "Strength and variety of academic programs and majors offered. Switch the Major Focus above to compare schools on a specific field.",
    "dorms":           "Quality, size, and comfort of on-campus housing.",
    "social":          "Greek life, parties, nightlife, and the overall social scene.",
    "diversity":       "Racial, ethnic, and socioeconomic diversity of the student body.",
    "grad_rate":       "4-year graduation rate — a proxy for student success and institutional support. Scaled relative to your selected schools.",
    "acceptance_rate": "How selective the school is — lower acceptance rate = higher score. A proxy for academic prestige and peer quality.",
    "faculty_ratio":   "Student-to-faculty ratio. Fewer students per professor means smaller classes and more individualized attention. Lower ratio = higher score.",
    "median_earnings": "Median salary of graduates 10 years after enrolling (U.S. College Scorecard). Higher earnings = higher score.",
}

# Default: equal weight across all criteria (must sum to 100)
DEFAULT_WEIGHTS = {k: round(100 / len(CRITERIA), 2) for k in CRITERIA}

# All normalized score columns in order
SCORE_COLS = [v["col"] for v in CRITERIA.values()]

# Majors available for per-major comparison
MAJORS = {
    "engineering":        "Engineering",
    "computer_science":   "Computer Science",
    "political_science":  "Political Science",
    "economics":          "Economics",
    "biology":            "Biology / Pre-Med",
    "english":            "English & Humanities",
    "mathematics":        "Mathematics",
    "art_music":          "Art & Music",
}

# Paths
DATA_DIR = "data"
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
SCORECARD_RAW_PATH = "data/raw/scorecard_raw.json"
NICHE_RAW_PATH = "data/raw/niche_raw.json"
NICHE_FALLBACK_PATH = "data/raw/niche_manual_fallback.json"
MAJOR_SCORES_PATH = "data/raw/major_scores.json"
SCORECARD_FALLBACK_PATH = "data/raw/scorecard_manual_fallback.json"
COLLEGES_CSV_PATH = "data/processed/colleges.csv"
