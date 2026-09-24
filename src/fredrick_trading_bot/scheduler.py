"""Market-calendar-aware daily execution."""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from alpaca.trading.client import TradingClient

from .strategy import DailyStrategy


class MarketScheduler:
    def __init__(
        self,
        client: TradingClient,
        strategy: DailyStrategy,
        timezone: str = "America/New_York",
        buy_minutes_after_open: int = 5,
        sell_minutes_before_close: int = 10,
    ) -> None:
        self.client = client
        self.strategy = strategy
        self.timezone = ZoneInfo(timezone)
        self.buy_minutes_after_open = buy_minutes_after_open
        self.sell_minutes_before_close = sell_minutes_before_close

    def run_for_date(self, trading_date: date, now: datetime | None = None) -> str:
        calendar = self.client.get_calendar(start=trading_date, end=trading_date)
        if not calendar:
            return "market_closed"

        session = calendar[0]
        current = now.astimezone(self.timezone) if now else datetime.now(self.timezone)
        open_at = _session_datetime(session.open, trading_date, self.timezone)
        close_at = _session_datetime(session.close, trading_date, self.timezone)
        trading_date_text = trading_date.isoformat()

        if current >= close_at:
            state = self.strategy.store.load()
            if state.trading_date == trading_date_text and state.symbol and not state.sell_order_id:
                self.strategy.sell_for_day(trading_date_text)
                return f"sold {state.symbol}"
            return "market_closed"

        if current >= open_at + timedelta(minutes=self.buy_minutes_after_open):
            state = self.strategy.buy_for_day(trading_date_text)
            if current >= close_at - timedelta(minutes=self.sell_minutes_before_close):
                self.strategy.sell_for_day(trading_date_text)
                return f"sold {state.symbol}"
            return f"holding {state.symbol}"
        return "waiting_for_buy_window"


def _session_datetime(value: object, session_date: date, timezone: ZoneInfo) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(timezone)
    if isinstance(value, time):
        return datetime.combine(session_date, value, tzinfo=timezone)
    return datetime.combine(value, datetime.min.time(), tzinfo=timezone)
