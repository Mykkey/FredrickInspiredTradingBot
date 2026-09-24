from dataclasses import dataclass

from fredrick_trading_bot.strategy import DailyStrategy, StateStore


@dataclass
class Asset:
    symbol: str


@dataclass
class Order:
    id: str


class FakeBroker:
    def __init__(self) -> None:
        self.assets = [Asset("AAA"), Asset("BBB")]
        self.buys: list[str] = []
        self.sells: list[str] = []

    def get_available_stocks(self) -> list[Asset]:
        return self.assets

    def buy_stock(self, symbol: str) -> Order:
        self.buys.append(symbol)
        return Order("buy-1")

    def sell_stock(self, symbol: str) -> Order:
        self.sells.append(symbol)
        return Order("sell-1")


def test_buy_is_randomly_choosable_and_restart_safe(tmp_path):
    broker = FakeBroker()
    strategy = DailyStrategy(broker, StateStore(tmp_path / "state.json"), dry_run=False)

    first = strategy.buy_for_day("2026-09-24", chooser=lambda assets: assets[1])
    second = strategy.buy_for_day("2026-09-24", chooser=lambda assets: assets[0])

    assert first.symbol == "BBB"
    assert second.symbol == "BBB"
    assert broker.buys == ["BBB"]
    assert first.buy_order_id == "buy-1"


def test_sell_is_restart_safe(tmp_path):
    broker = FakeBroker()
    strategy = DailyStrategy(broker, StateStore(tmp_path / "state.json"), dry_run=False)
    strategy.buy_for_day("2026-09-24", chooser=lambda assets: assets[0])

    first = strategy.sell_for_day("2026-09-24")
    second = strategy.sell_for_day("2026-09-24")

    assert first.sell_order_id == "sell-1"
    assert second.sell_order_id == "sell-1"
    assert broker.sells == ["AAA"]
