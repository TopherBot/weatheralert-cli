# weatheralert‑cli

A **tiny** Python command‑line tool that:

1. Queries the Open‑WeatherMap *Current Weather* endpoint for a city you provide.
2. Prints a concise one‑line summary.
3. If the weather matches a *severe* pattern (storm, heavy rain, snow, heat‑wave, freezing), it sends a Telegram message to a pre‑configured chat.

## Features
- Zero‑config for quick testing (`python -m weatheralert <city>`).
- Uses **`requests`** (built‑in pip) – no heavy dependencies.
- CI pipeline with **GitHub Actions** runs lint + unit test on every push.
- Optional Telegram alert (set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`).
- Fully type‑annotated, PEP‑8 compliant, < 200 LOC.

## Quick start
```bash
# Clone & install deps
git clone https://github.com/youruser/weatheralert-cli.git && cd weatheralert-cli
python -m pip install -r requirements.txt

# Run (replace CITY with any city name)
python -m weatheralert "London"
```

## Environment variables
| Variable | Description |
|----------|-------------|
| `OPENWEATHER_API_KEY` | **Required** – sign‑up at https://openweathermap.org/api |
| `TELEGRAM_BOT_TOKEN` | Optional – Bot token from @BotFather |
| `TELEGRAM_CHAT_ID`  | Optional – Chat ID where alerts are sent |

## CI & notifications
The workflow runs on every push:
- **ruff** linting
- **pytest** unit tests
- On failure, a Telegram alert is posted (if token is set in repo secrets).

## License
MIT – see `LICENSE`.
