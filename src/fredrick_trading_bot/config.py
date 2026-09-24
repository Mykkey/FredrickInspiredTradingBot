"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


class ConfigurationError(ValueError):
    """Raised when required or unsafe configuration is supplied."""


@dataclass(frozen=True)
class Settings:
    api_key: str
    secret_key: str
    paper: bool
    dry_run: bool
    state_file: Path
    market_timezone: str
    buy_window_minutes_after_open: int
    sell_window_minutes_before_close: int

    @classmethod
    def from_environment(cls, env_file: str | Path | None = None) -> "Settings":
        if env_file is not None:
            load_dotenv(env_file)
        else:
            load_dotenv()

        api_key = os.getenv("ALPACA_API_KEY", "").strip()
        secret_key = os.getenv("ALPACA_SECRET_KEY", "").strip()
        paper = _read_bool("ALPACA_PAPER", default=True)
        dry_run = _read_bool("DRY_RUN", default=True)

        if not paper:
            raise ConfigurationError(
                "Live trading is disabled in this initial implementation. Set ALPACA_PAPER=true."
            )
        if not api_key or not secret_key:
            raise ConfigurationError("ALPACA_API_KEY and ALPACA_SECRET_KEY are required.")

        return cls(
            api_key=api_key,
            secret_key=secret_key,
            paper=paper,
            dry_run=dry_run,
            state_file=Path(os.getenv("STATE_FILE", "bot_state.json")),
            market_timezone=os.getenv("MARKET_TIMEZONE", "America/New_York"),
            buy_window_minutes_after_open=_read_int(
                "BUY_WINDOW_MINUTES_AFTER_OPEN", default=5, minimum=0
            ),
            sell_window_minutes_before_close=_read_int(
                "SELL_WINDOW_MINUTES_BEFORE_CLOSE", default=10, minimum=0
            ),
        )


def _read_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ConfigurationError(f"{name} must be true or false.")
    return normalized == "true"


def _read_int(name: str, default: int, minimum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer.") from exc
    if value < minimum:
        raise ConfigurationError(f"{name} must be at least {minimum}.")
    return value
