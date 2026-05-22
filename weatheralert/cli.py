import os
import sys
from typing import Any, Dict

import requests

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
SEVERE_CONDITIONS = {
    "Thunderstorm",
    "Rain",
    "Snow",
    "Extreme",
    "Hot",
    "Cold",
}


def _load_env() -> Dict[str, str]:
    """Fetch required environment variables, raising clear errors if missing."""
    try:
        api_key = os.environ["OPENWEATHER_API_KEY"]
    except KeyError as exc:
        raise RuntimeError(
            "Missing OPENWEATHER_API_KEY env var – sign‑up at openweathermap.org"
        ) from exc
    # Telegram vars are optional – the notifier will silently skip if absent
    return {
        "api_key": api_key,
        "tg_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "tg_chat": os.getenv("TELEGRAM_CHAT_ID"),
    }


def _fetch_weather(city: str, api_key: str) -> Dict[str, Any]:
    """Call OpenWeatherMap API and return the JSON payload.
    Raises ``RuntimeError`` on non‑200 responses.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Weather API error {resp.status_code}: {resp.text}")
    return resp.json()


def _is_severe(weather: Dict[str, Any]) -> bool:
    """Return ``True`` if any weather condition matches our severe set."""
    main = weather.get("weather", [{}])[0].get("main", "")
    return main in SEVERE_CONDITIONS


def _format_summary(weather: Dict[str, Any], city: str) -> str:
    main = weather.get("weather", [{}])[0].get("description", "unknown")
    temp = weather.get("main", {}).get("temp", "?")
    return f"{city.title()}: {main.capitalize()}, {temp}°C"


def _send_telegram(token: str, chat_id: str, message: str) -> None:
    """Post a simple message to Telegram using the Bot API.
    Silent‑fail (log to stderr) if the request errors – we never want CI to crash.
    """
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=5)
    except Exception as exc:  # pragma: no cover – network‑flaky
        print(f"[weatheralert] Telegram notification failed: {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    """Entry‑point for the CLI.
    Returns an exit‑code (0 = success, 1 = error).
    """
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: python -m weatheralert <city>")
        return 1
    city = " ".join(argv)
    env = _load_env()
    try:
        data = _fetch_weather(city, env["api_key"])
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    summary = _format_summary(data, city)
    print(summary)

    if _is_severe(data):
        alert_msg = f"⚠️ Severe weather alert for *{city.title()}*: {summary}"
        _send_telegram(env["tg_token"], env["tg_chat"], alert_msg)
    return 0

if __name__ == "__main__":
    sys.exit(main())
