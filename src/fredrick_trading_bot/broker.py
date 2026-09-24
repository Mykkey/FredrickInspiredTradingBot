"""Small, testable wrapper around the Alpaca trading API."""

from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal
from typing import Any

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetClass, OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest


class BrokerError(RuntimeError):
    """Raised when a broker operation cannot be completed."""


@dataclass(frozen=True)
class StockAsset:
    symbol: str
    name: str
    exchange: str
    fractionable: bool


class AlpacaBroker:
    """Alpaca implementation of the bot's broker operations."""

    def __init__(self, api_key: str, secret_key: str, paper: bool = True) -> None:
        if not paper:
            raise BrokerError("Live trading is disabled in this initial implementation.")
        self.client = TradingClient(api_key, secret_key, paper=paper)

    def get_available_stocks(self) -> list[StockAsset]:
        try:
            assets = self.client.get_all_assets()
        except Exception as exc:
            raise BrokerError("Could not retrieve available stock assets.") from exc

        return [
            StockAsset(
                symbol=asset.symbol,
                name=asset.name,
                exchange=str(asset.exchange),
                fractionable=bool(asset.fractionable),
            )
            for asset in assets
            if asset.status.value == "active"
            and asset.tradable
            and asset.asset_class == AssetClass.US_EQUITY
            and asset.symbol.isalpha()
        ]

    def buy_stock(self, symbol: str) -> Any:
        symbol = _normalize_symbol(symbol)
        try:
            account = self.client.get_account()
            buying_power = Decimal(str(account.buying_power))
            asset = self.client.get_asset(symbol)
        except Exception as exc:
            raise BrokerError(f"Could not validate buy for {symbol}.") from exc

        if not asset.tradable or asset.asset_class != AssetClass.US_EQUITY:
            raise BrokerError(f"{symbol} is not a tradable US equity.")
        if buying_power <= 0:
            raise BrokerError("The account has no available buying power.")

        request = MarketOrderRequest(
            symbol=symbol,
            notional=buying_power.quantize(Decimal("0.01"), rounding=ROUND_DOWN),
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
        )
        try:
            return self.client.submit_order(request)
        except Exception as exc:
            raise BrokerError(f"Buy order for {symbol} failed.") from exc

    def sell_stock(self, symbol: str) -> Any | None:
        symbol = _normalize_symbol(symbol)
        try:
            position = self.client.get_open_position(symbol)
        except Exception as exc:
            if "position" in str(exc).lower() or "404" in str(exc):
                return None
            raise BrokerError(f"Could not find the position for {symbol}.") from exc

        quantity = Decimal(str(position.qty))
        if quantity <= 0:
            return None
        request = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        try:
            return self.client.submit_order(request)
        except Exception as exc:
            raise BrokerError(f"Sell order for {symbol} failed.") from exc


def _normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized or not normalized.isalpha():
        raise BrokerError("A valid stock symbol is required.")
    return normalized
