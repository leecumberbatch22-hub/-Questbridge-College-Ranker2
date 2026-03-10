"""Unit tests for scraper/normalizer.py"""

import math
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.normalizer import grade_to_score, normalize_minmax, normalize_financial_aid, build_dataset


class TestGradeToScore:
    def test_a_plus(self):
        assert grade_to_score("A+") == 100.0

    def test_a(self):
        assert grade_to_score("A") == 95.0

    def test_b_minus(self):
        assert grade_to_score("B-") == 75.0

    def test_f(self):
        assert grade_to_score("F") == 30.0

    def test_whitespace_stripped(self):
        assert grade_to_score("  A+  ") == 100.0

    def test_empty_string_returns_nan(self):
        assert math.isnan(grade_to_score(""))

    def test_none_returns_nan(self):
        assert math.isnan(grade_to_score(None))

    def test_unknown_grade_returns_nan(self):
        assert math.isnan(grade_to_score("Z+"))


class TestNormalizeMinmax:
    def test_basic_scaling(self):
        s = pd.Series([0.0, 50.0, 100.0])
        result = normalize_minmax(s)
        assert result.iloc[0] == 0.0
        assert result.iloc[1] == 50.0
        assert result.iloc[2] == 100.0

    def test_real_grad_rates(self):
        # Typical Questbridge grad rates
        s = pd.Series([0.75, 0.85, 0.95, 0.99])
        result = normalize_minmax(s)
        assert result.iloc[0] == 0.0
        assert result.iloc[-1] == 100.0
        assert 0 < result.iloc[1] < result.iloc[2] < 100

    def test_all_same_returns_50(self):
        s = pd.Series([0.90, 0.90, 0.90])
        result = normalize_minmax(s)
        assert all(result == 50.0)


class TestNormalizeFinancialAid:
    def test_lower_price_gets_higher_score(self):
        prices = pd.Series([5000.0, 15000.0, 30000.0])
        result = normalize_financial_aid(prices)
        # Lowest price should get score 100
        assert result.iloc[0] == 100.0
        # Highest price should get score 0
        assert result.iloc[-1] == 0.0

    def test_middle_value_is_between(self):
        prices = pd.Series([5000.0, 15000.0, 30000.0])
        result = normalize_financial_aid(prices)
        assert 0 < result.iloc[1] < 100


class TestBuildDataset:
    def _make_scorecard(self):
        return [
            {
                "id": "1",
                "school.name": "Test University",
                "school.city": "Boston",
                "school.state": "MA",
                "slug": "test-university",
                "_source": "scorecard",
                "latest.completion.completion_rate_4yr_150nt": 0.90,
                "latest.cost.avg_net_price.overall": 20000,
            },
            {
                "id": "2",
                "school.name": "Sample College",
                "school.city": "Chicago",
                "school.state": "IL",
                "slug": "sample-college",
                "_source": "scorecard",
                "latest.completion.completion_rate_4yr_150nt": 0.80,
                "latest.cost.avg_net_price.overall": 30000,
            },
        ]

    def _make_niche(self):
        return {
            "test-university": {
                "campus_life": "A+",
                "food": "A",
                "dorms": "A-",
                "social": "B+",
                "diversity": "A",
                "location": "A+",
                "majors": "A+",
            },
            "sample-college": {
                "campus_life": "B+",
                "food": "B",
                "dorms": "B+",
                "social": "B",
                "diversity": "B+",
                "location": "A",
                "majors": "A",
            },
        }

    def test_output_has_correct_columns(self):
        df = build_dataset(self._make_scorecard(), self._make_niche())
        for col in ["name", "score_campus_life", "score_food", "score_grad_rate", "score_financial_aid"]:
            assert col in df.columns, f"Missing column: {col}"

    def test_row_count(self):
        df = build_dataset(self._make_scorecard(), self._make_niche())
        assert len(df) == 2

    def test_scores_in_range(self):
        df = build_dataset(self._make_scorecard(), self._make_niche())
        for col in ["score_campus_life", "score_food", "score_grad_rate", "score_financial_aid"]:
            for val in df[col].dropna():
                assert 0 <= val <= 100, f"{col} value {val} out of range"

    def test_higher_grad_rate_gets_higher_score(self):
        df = build_dataset(self._make_scorecard(), self._make_niche())
        tu = df[df["slug"] == "test-university"].iloc[0]
        sc = df[df["slug"] == "sample-college"].iloc[0]
        assert tu["score_grad_rate"] > sc["score_grad_rate"]

    def test_lower_price_gets_higher_financial_aid_score(self):
        df = build_dataset(self._make_scorecard(), self._make_niche())
        tu = df[df["slug"] == "test-university"].iloc[0]
        sc = df[df["slug"] == "sample-college"].iloc[0]
        assert tu["score_financial_aid"] > sc["score_financial_aid"]

    def test_missing_niche_data_is_nan(self):
        # Pass empty niche data
        df = build_dataset(self._make_scorecard(), {})
        assert df["score_campus_life"].isna().all()

    def test_last_updated_set(self):
        df = build_dataset(self._make_scorecard(), self._make_niche())
        assert df["last_updated"].notna().all()
