import pandas as pd
import pytest
from data import split_past_upcoming, success_rate


# ---------------------------------------------------------------------------
# split_past_upcoming
# ---------------------------------------------------------------------------

class TestSplitPastUpcoming:
    def _df(self, dates):
        return pd.DataFrame({"net": pd.to_datetime(dates, utc=True)})

    def test_splits_into_past_and_upcoming(self):
        df = self._df(["2020-01-01", "2030-01-01"])
        past, upcoming = split_past_upcoming(df)
        assert len(past) == 1
        assert len(upcoming) == 1

    def test_all_past(self):
        df = self._df(["2020-01-01", "2021-06-15"])
        past, upcoming = split_past_upcoming(df)
        assert len(past) == 2
        assert upcoming.empty

    def test_all_upcoming(self):
        df = self._df(["2030-01-01", "2031-06-15"])
        past, upcoming = split_past_upcoming(df)
        assert past.empty
        assert len(upcoming) == 2

    def test_upcoming_is_sorted_ascending(self):
        df = self._df(["2031-06-15", "2030-01-01"])
        _, upcoming = split_past_upcoming(df)
        dates = list(upcoming["net"])
        assert dates == sorted(dates)

    def test_empty_input(self):
        empty = pd.DataFrame({"net": pd.Series([], dtype="datetime64[ns, UTC]")})
        past, upcoming = split_past_upcoming(empty)
        assert past.empty
        assert upcoming.empty


# ---------------------------------------------------------------------------
# success_rate
# ---------------------------------------------------------------------------

class TestSuccessRate:
    def _df(self, statuses):
        return pd.DataFrame({"status_name": statuses})

    def test_empty_returns_zero(self):
        assert success_rate(pd.DataFrame()) == 0.0

    def test_all_successful(self):
        df = self._df(["Launch Successful", "Launch Successful", "Success"])
        assert success_rate(df) == pytest.approx(100.0)

    def test_mixed_success_and_failure(self):
        df = self._df(["Launch Successful", "Launch Failure", "Launch Successful"])
        # 2 successes / 3 concluded = 66.67%
        assert success_rate(df) == pytest.approx(2 / 3 * 100)

    def test_partial_failure_counts_as_concluded(self):
        df = self._df(["Launch Successful", "Partial Failure"])
        assert success_rate(df) == pytest.approx(50.0)

    def test_non_concluded_status_excluded(self):
        # "In Flight" and "Go for Launch" are not in success or failure sets
        df = self._df(["Launch Successful", "In Flight", "Go for Launch"])
        # Only 1 concluded (the successful one), rate = 100%
        assert success_rate(df) == pytest.approx(100.0)

    def test_only_failures(self):
        df = self._df(["Launch Failure", "Failure"])
        assert success_rate(df) == pytest.approx(0.0)

    def test_no_concluded_launches_returns_zero(self):
        df = self._df(["In Flight", "Go for Launch"])
        assert success_rate(df) == 0.0
