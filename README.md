# Fredrick Inspired Trading Bot

A small Python bot for a simple daily strategy: select one tradable US stock, invest available Alpaca buying power, and sell the position later that market day.

The initial implementation is paper-trading only. `DRY_RUN=true` is the default and prevents order submission.

## Setup

1. Install Python 3.11 or newer.
2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the project:

   ```powershell
   python -m pip install -e ".[dev]"
   ```

4. Copy `.env.example` to `.env` and add an Alpaca paper account key and secret.
5. Leave `ALPACA_PAPER=true` and `DRY_RUN=true` while testing.

## Commands

Select a stock for today's session:

```powershell
python -m fredrick_trading_bot.main --buy
```

Sell the selected position:

```powershell
python -m fredrick_trading_bot.main --sell
```

Run an offline historical simulation. This command never contacts Alpaca and never submits an order:

```powershell
python -m fredrick_trading_bot.main --backtest --symbols AAPL MSFT AMZN GOOGL NVDA --start 2020-01-01 --end 2025-01-01 --cash 10000 --seed 42
```

The default `--benchmark ^GSPC` compares the result with a buy-and-hold S&P 500 price index
simulation over the same dates. The benchmark does not include dividends; use a total-return
benchmark for a more complete investment comparison.

The backtester selects one symbol with the supplied random seed for each date where data is available,
buys at that day's open, and sells at that day's close. It reports ending cash, total return, winning
trades, and maximum drawdown.

Historical results are not a forecast. A manually supplied symbol list creates survivorship bias, and
the simple simulation does not include commissions, bid/ask spread, slippage, liquidity limits, taxes,
partial fills, delisted stocks, or the delay between submitting and filling a real order.

The local state file prevents duplicate buys and sells after a restart. The scheduler uses Alpaca's market calendar and New York market time when it is wired into an unattended runner.

## Safety

This project does not enable live trading. Do not remove that restriction without reviewing order sizing, partial fills, API outages, slippage, market gaps, and emergency liquidation procedures. Market orders can execute at prices materially different from the last displayed quote.

The strategy is intentionally experimental and does not provide investment advice or a guarantee of profit.
