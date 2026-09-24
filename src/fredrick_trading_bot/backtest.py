"""Offline historical simulation of the daily random-stock strategy."""

import random
from dataclasses import dataclass
from datetime import date
from typing import Iterable

import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class BacktestTrade:
    trading_date: date
    symbol: str
    buy_price: float
    sell_price: float
    starting_cash: float
    ending_cash: float

    @property
    def return_pct(self) -> float:
        return (self.ending_cash / self.starting_cash - 1) * 100


@dataclass(frozen=True)
class BacktestResult:
    starting_cash: float
    ending_cash: float
    trades: tuple[BacktestTrade, ...]
    max_drawdown_pct: float

    @property
    def total_return_pct(self) -> float:
        return (self.ending_cash / self.starting_cash - 1) * 100

    @property
    def winning_trades(self) -> int:
        return sum(trade.ending_cash > trade.starting_cash for trade in self.trades)


@dataclass(frozen=True)
class BenchmarkResult:
    symbol: str
    starting_cash: float
    ending_cash: float
    max_drawdown_pct: float

    @property
    def total_return_pct(self) -> float:
        return (self.ending_cash / self.starting_cash - 1) * 100


def download_history(
    symbols: Iterable[str], start: str, end: str
) -> dict[str, pd.DataFrame]:
    """Download daily OHLC data without contacting Alpaca or placing orders."""
    normalized = sorted({symbol.strip().upper() for symbol in symbols if symbol.strip()})
    if not normalized:
        raise ValueError("At least one stock symbol is required.")
    downloaded = yf.download(
        normalized,
        start=start,
        end=end,
        auto_adjust=False,
        group_by="ticker",
        progress=False,
        threads=False,
    )
    if downloaded.empty:
        raise ValueError("No historical data was returned for the requested symbols.")

    histories: dict[str, pd.DataFrame] = {}
    for symbol in normalized:
        try:
            history = downloaded[symbol] if len(normalized) > 1 else downloaded
        except KeyError:
            continue
        if isinstance(history.columns, pd.MultiIndex):
            try:
                history = history.xs(symbol, axis=1, level=-1)
            except KeyError:
                history = history.xs(symbol, axis=1, level=0)
        history = history.dropna(subset=["Open", "Close"])
        if not history.empty:
            histories[symbol] = history
    if not histories:
        raise ValueError("No usable historical open/close data was returned.")
    return histories


def run_backtest(
    histories: dict[str, pd.DataFrame],
    starting_cash: float = 10_000.0,
    seed: int = 42,
) -> BacktestResult:
    """Select one available symbol per day, buy at open, and sell at close."""
    if starting_cash <= 0:
        raise ValueError("starting_cash must be greater than zero.")
    if not histories:
        raise ValueError("At least one historical price series is required.")

    dates = sorted(set().union(*(history.index for history in histories.values())))
    rng = random.Random(seed)
    cash = starting_cash
    peak = cash
    max_drawdown_pct = 0.0
    trades: list[BacktestTrade] = []

    for timestamp in dates:
        available: list[tuple[str, float, float]] = []
        for symbol, history in histories.items():
            if timestamp not in history.index:
                continue
            row = history.loc[timestamp]
            open_price = float(row["Open"])
            close_price = float(row["Close"])
            if open_price > 0 and close_price > 0:
                available.append((symbol, open_price, close_price))
        if not available:
            continue

        symbol, buy_price, sell_price = rng.choice(available)
        starting_day_cash = cash
        shares = cash / buy_price
        cash = shares * sell_price
        trades.append(
            BacktestTrade(
                trading_date=timestamp.date(),
                symbol=symbol,
                buy_price=buy_price,
                sell_price=sell_price,
                starting_cash=starting_day_cash,
                ending_cash=cash,
            )
        )
        peak = max(peak, cash)
        max_drawdown_pct = max(max_drawdown_pct, (peak - cash) / peak * 100)

    return BacktestResult(
        starting_cash=starting_cash,
        ending_cash=cash,
        trades=tuple(trades),
        max_drawdown_pct=max_drawdown_pct,
    )


def run_buy_and_hold_benchmark(
    symbol: str, history: pd.DataFrame, starting_cash: float
) -> BenchmarkResult:
    """Simulate buying a benchmark at its first open and holding through its last close."""
    prices = history.dropna(subset=["Open", "Close"])
    if prices.empty or starting_cash <= 0:
        raise ValueError("Benchmark data and starting_cash must be valid.")

    first_open = float(prices.iloc[0]["Open"])
    last_close = float(prices.iloc[-1]["Close"])
    if first_open <= 0 or last_close <= 0:
        raise ValueError("Benchmark prices must be greater than zero.")

    equity = starting_cash * prices["Close"].astype(float) / first_open
    running_peak = equity.cummax()
    drawdown_pct = ((running_peak - equity) / running_peak * 100).max()
    return BenchmarkResult(
        symbol=symbol,
        starting_cash=starting_cash,
        ending_cash=starting_cash * last_close / first_open,
        max_drawdown_pct=float(drawdown_pct),
    )