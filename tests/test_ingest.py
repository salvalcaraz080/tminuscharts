from unittest.mock import MagicMock, patch, call

import pytest
import requests

import ingest


# ---------------------------------------------------------------------------
# fetch_page
# ---------------------------------------------------------------------------

class TestFetchPage:
    def _mock_response(self, status_code=200, json_data=None, headers=None):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = json_data or {"results": [], "next": None, "count": 0}
        resp.headers = headers or {}
        resp.raise_for_status = MagicMock()
        return resp

    def test_successful_request_returns_json(self):
        expected = {"results": [{"id": "abc"}], "next": None, "count": 1}
        with patch("ingest.requests.get", return_value=self._mock_response(json_data=expected)):
            result = ingest.fetch_page("https://api.example.com", "launch/previous", 0, {})
        assert result == expected

    def test_passes_correct_params(self):
        with patch("ingest.requests.get", return_value=self._mock_response()) as mock_get:
            ingest.fetch_page("https://api.example.com", "launch/previous", 100, {"net__gte": "2023-01-01"})

        _, kwargs = mock_get.call_args
        params = kwargs.get("params") or mock_get.call_args[0][1] if mock_get.call_args[0] else {}
        call_kwargs = mock_get.call_args[1] if mock_get.call_args[1] else {}
        actual_params = call_kwargs.get("params", mock_get.call_args.kwargs.get("params", {}))
        assert actual_params["offset"] == 100
        assert actual_params["limit"] == ingest.PAGE_SIZE
        assert actual_params["net__gte"] == "2023-01-01"

    def test_429_waits_and_retries(self):
        rate_limited = self._mock_response(status_code=429, headers={"Retry-After": "10"})
        rate_limited.raise_for_status = MagicMock()  # 429 branch skips raise_for_status
        success = self._mock_response()

        with patch("ingest.requests.get", side_effect=[rate_limited, success]), \
             patch("ingest.time.sleep") as mock_sleep:
            result = ingest.fetch_page("https://api.example.com", "launch/previous", 0, {})

        mock_sleep.assert_called_once_with(10)
        assert result == success.json.return_value

    def test_429_uses_retry_after_header(self):
        rate_limited = self._mock_response(status_code=429, headers={"Retry-After": "3600"})
        success = self._mock_response()

        with patch("ingest.requests.get", side_effect=[rate_limited, success]), \
             patch("ingest.time.sleep") as mock_sleep:
            ingest.fetch_page("https://api.example.com", "launch/previous", 0, {})

        mock_sleep.assert_called_once_with(3600)

    def test_request_exception_retries_up_to_3_times(self):
        with patch("ingest.requests.get", side_effect=requests.exceptions.ConnectionError("timeout")), \
             patch("ingest.time.sleep"):
            result = ingest.fetch_page("https://api.example.com", "launch/previous", 0, {})

        assert result == {"results": [], "next": None, "count": 0}

    def test_request_exception_succeeds_on_second_attempt(self):
        success = self._mock_response(json_data={"results": [{"id": "xyz"}], "next": None, "count": 1})

        with patch("ingest.requests.get", side_effect=[
            requests.exceptions.ConnectionError("err"),
            success
        ]), patch("ingest.time.sleep"):
            result = ingest.fetch_page("https://api.example.com", "launch/previous", 0, {})

        assert result["count"] == 1
