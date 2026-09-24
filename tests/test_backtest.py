import pandas as pd
from pytest import approx

from fredrick_trading_bot.backtest import run_backtest, run_buy_and_hold_benchmark


def prices(rows: list[tuple[str, float, float]]) -> pd.DataFrame:
    index = pd.to_datetime([row[0] for row in rows])
    return pd.DataFrame(
        {"Open": [row[1] for row in rows], "Close": [row[2] for row in rows]},
        index=index,
    )


def test_backtest_buys_at_open_and_sells_at_close():
    result = run_backtest(
        {"AAA": prices([("2024-01-02", 100, 110), ("2024-01-03", 110, 99)])},
        starting_cash=1_000,
        seed=1,
    )

    assert len(result.trades) == 2
    assert result.ending_cash == 990
    assert result.total_return_pct == approx(-1)
    assert result.max_drawdown_pct == approx(10)


def test_backtest_seed_makes_selection_reproducible():
    histories = {
        "AAA": prices([("2024-01-02", 100, 110)]),
        "BBB": prices([("2024-01-02", 100, 90)]),
    }

    first = run_backtest(histories, seed=7)
    second = run_backtest(histories, seed=7)

    assert first.trades == second.trades


def test_benchmark_buys_first_open_and_holds_to_last_close():
    result = run_buy_and_hold_benchmark(
        "^GSPC",
        prices([("2024-01-02", 100, 105), ("2024-01-03", 110, 120)]),
        starting_cash=1_000,
    )

    assert result.ending_cash == 1_200
    assert result.total_return_pct == approx(20)