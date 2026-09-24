"""Command-line entry point for the paper-trading bot."""

import argparse
import logging
from datetime import date

from .backtest import download_history, run_backtest, run_buy_and_hold_benchmark
from .broker import AlpacaBroker
from .config import Settings
from .strategy import DailyStrategy, StateStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Fredrick's daily paper-trading strategy.")
    parser.add_argument("--buy", action="store_true", help="Select and buy for today's session.")
    parser.add_argument("--sell", action="store_true", help="Sell today's selected position.")
    parser.add_argument(
        "--backtest", action="store_true", help="Run an offline historical simulation."
    )
    parser.add_argument(
        "--symbols", nargs="+", help="Symbols to use for the historical simulation."
    )
    parser.add_argument("--start", default="2020-01-01", help="Backtest start date, YYYY-MM-DD.")
    parser.add_argument("--end", default="2025-01-01", help="Backtest end date, YYYY-MM-DD.")
    parser.add_argument("--cash", type=float, default=10_000.0, help="Starting backtest cash.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument(
        "--benchmark", default="^GSPC", help="Benchmark symbol; ^GSPC represents the S&P 500 index."
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.backtest:
        if not args.symbols:
            parser.error("--backtest requires at least one --symbols value")
        result = run_backtest(
            download_history(args.symbols, args.start, args.end),
            starting_cash=args.cash,
            seed=args.seed,
        )
        benchmark_history = download_history([args.benchmark], args.start, args.end)[args.benchmark]
        benchmark = run_buy_and_hold_benchmark(args.benchmark, benchmark_history, args.cash)
        logging.info("Trades: %d", len(result.trades))
        logging.info("Ending cash: $%.2f", result.ending_cash)
        logging.info("Total return: %.2f%%", result.total_return_pct)
        logging.info("Winning trades: %d", result.winning_trades)
        logging.info("Max drawdown: %.2f%%", result.max_drawdown_pct)
        logging.info("%s ending cash: $%.2f", benchmark.symbol, benchmark.ending_cash)
        logging.info("%s total return: %.2f%%", benchmark.symbol, benchmark.total_return_pct)
        logging.info("%s max drawdown: %.2f%%", benchmark.symbol, benchmark.max_drawdown_pct)
        logging.info("Return difference versus %s: %.2f percentage points", benchmark.symbol,
                     result.total_return_pct - benchmark.total_return_pct)
        return

    settings = Settings.from_environment()
    broker = AlpacaBroker(settings.api_key, settings.secret_key, paper=settings.paper)
    strategy = DailyStrategy(
        broker=broker,
        store=StateStore(settings.state_file),
        dry_run=settings.dry_run,
    )
    trading_date = date.today().isoformat()

    if args.sell:
        state = strategy.sell_for_day(trading_date)
        logging.info("Sell completed for %s", state.symbol)
    else:
        state = strategy.buy_for_day(trading_date)
        logging.info("Selected %s", state.symbol)
        if settings.dry_run:
            logging.info("DRY_RUN=true; no order was submitted")


if __name__ == "__main__":
    main()
