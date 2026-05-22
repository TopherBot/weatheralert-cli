import os
import types
from unittest import mock

from weatheralert import cli


def test_format_summary():
    sample = {
        "weather": [{"description": "light rain"}],
        "main": {"temp": 12.3},
    }
    assert cli._format_summary(sample, "paris") == "Paris: Light rain, 12.3°C"


def test_is_severe_true():
    sample = {"weather": [{"main": "Thunderstorm"}]}
    assert cli._is_severe(sample) is True


def test_is_severe_false():
    sample = {"weather": [{"main": "Clear"}]}
    assert cli._is_severe(sample) is False


def test_send_telegram_skips_without_token():
    with mock.patch("requests.post") as mocked:
        cli._send_telegram(None, "123", "msg")
        mocked.assert_not_called()


def test_main_success(monkeypatch, capsys):
    # stub environment & API response
    monkeypatch.setenv("OPENWEATHER_API_KEY", "dummy")
    fake_resp = {"weather": [{"description": "clear sky", "main": "Clear"}], "main": {"temp": 22}}
    with mock.patch("weatheralert.cli._fetch_weather", return_value=fake_resp):
        exit_code = cli.main(["Berlin"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Berlin: Clear sky, 22°C" in captured.out
