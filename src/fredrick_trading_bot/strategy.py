"""Daily one-stock strategy and restart-safe local state."""

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol


class Broker(Protocol):
    def get_available_stocks(self) -> list[Any]: ...

    def buy_stock(self, symbol: str) -> Any: ...

    def sell_stock(self, symbol: str) -> Any | None: ...


@dataclass
class DailyState:
    trading_date: str | None = None
    symbol: str | None = None
    buy_order_id: str | None = None
    sell_order_id: str | None = None


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> DailyState:
        if not self.path.exists():
            return DailyState()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return DailyState(**data)
        except (OSError, TypeError, ValueError) as exc:
            raise RuntimeError(f"Could not read state file {self.path}.") from exc

    def save(self, state: DailyState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temporary_path.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")
        temporary_path.replace(self.path)


class DailyStrategy:
    def __init__(self, broker: Broker, store: StateStore, dry_run: bool = True) -> None:
        self.broker = broker
        self.store = store
        self.dry_run = dry_run

    def buy_for_day(self, trading_date: str, chooser: Any = random.choice) -> DailyState:
        state = self.store.load()
        if state.trading_date == trading_date and state.symbol:
            return state

        assets = self.broker.get_available_stocks()
        if not assets:
            raise RuntimeError("The broker returned no tradable stocks.")
        selected = chooser(assets)
        symbol = selected.symbol
        state = DailyState(trading_date=trading_date, symbol=symbol)
        if not self.dry_run:
            order = self.broker.buy_stock(symbol)
            state.buy_order_id = _order_id(order)
        self.store.save(state)
        return state

    def sell_for_day(self, trading_date: str) -> DailyState:
        state = self.store.load()
        if state.trading_date != trading_date or not state.symbol:
            raise RuntimeError("There is no selected stock for this trading day.")
        if state.sell_order_id:
            return state

        if not self.dry_run:
            order = self.broker.sell_stock(state.symbol)
            state.sell_order_id = _order_id(order)
        self.store.save(state)
        return state


def _order_id(order: Any | None) -> str | None:
    if order is None:
        return None
    value = getattr(order, "id", order)
    return str(value)
