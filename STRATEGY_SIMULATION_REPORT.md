# Strategy Simulation Report

## Executive summary

The strategy was tested with an initial balance of EUR 1,000 and daily reinvestment. It selected one stock from AAPL, MSFT, AMZN, GOOGL, and NVDA, bought at that day's open, and sold at that day's close.

The frictionless backtest looked profitable, but that result did not survive ordinary trading costs. With a conservative allowance for spread and slippage, every tested run lost money over the five-year period. The current strategy should not be treated as a reliable way to grow real savings.

## What was tested

- Historical period: 1 January 2020 to 1 January 2025
- Trading days: 1,258
- Starting balance: EUR 1,000
- Reinvestment: the full account balance was used again on each trading day
- Stock universe: AAPL, MSFT, AMZN, GOOGL, and NVDA
- Runs: 10 different random seeds
- Benchmark: buy-and-hold S&P 500 price index over the same period

The random seeds changed which stock was selected each day. They did not represent ten independent future market periods, so the results are useful for showing sensitivity to stock selection but cannot establish a real-world probability of profit.

## Frictionless results

Without commissions, spread, or slippage, all ten runs ended above the initial EUR 1,000:

| Seed | Ending balance | Return |
| ---: | ---: | ---: |
| 1 | EUR 2,139.30 | 113.93% |
| 2 | EUR 3,542.70 | 254.27% |
| 3 | EUR 3,099.64 | 209.96% |
| 4 | EUR 2,035.49 | 103.55% |
| 5 | EUR 2,209.88 | 120.99% |
| 6 | EUR 1,276.04 | 27.60% |
| 7 | EUR 1,936.92 | 93.69% |
| 8 | EUR 2,157.16 | 115.72% |
| 9 | EUR 1,613.09 | 61.31% |
| 10 | EUR 1,111.35 | 11.14% |

The frictionless sample had an average ending balance of EUR 2,111.22. Seven of the ten runs beat the S&P 500 price-index benchmark, which ended at approximately EUR 1,812.71 on the same starting balance.

These figures are not realistic expected returns. The strategy makes a round trip every trading day, so even small costs compound across more than one thousand trades.

## Cost-adjusted results

The main cost-adjusted simulation used:

- 0.10% slippage or spread on entry
- 0.10% slippage or spread on exit
- 0.01% additional fee on each side
- No broker commission

Under those assumptions, the results were:

| Seed | Ending balance | Net return |
| ---: | ---: | ---: |
| 1 | EUR 134.38 | -86.56% |
| 2 | EUR 222.53 | -77.75% |
| 3 | EUR 194.70 | -80.53% |
| 4 | EUR 127.85 | -87.21% |
| 5 | EUR 138.81 | -86.12% |
| 6 | EUR 80.15 | -91.98% |
| 7 | EUR 121.66 | -87.83% |
| 8 | EUR 135.50 | -86.45% |
| 9 | EUR 101.32 | -89.87% |
| 10 | EUR 69.81 | -93.02% |

No run was profitable after costs. The average ending balance was EUR 132.67 after five years.

### Sensitivity to trading costs

| Slippage per side | Profitable runs | Average ending balance |
| ---: | ---: | ---: |
| 0.000% | 8/10 | EUR 1,642.32 |
| 0.025% | 2/10 | EUR 875.56 |
| 0.050% | 0/10 | EUR 466.78 |
| 0.100% | 0/10 | EUR 132.67 |

The sharp change shows that the apparent edge is too small to cover the cost of trading every day.

## Limitations

This was a historical simulation, not a forecast or investment recommendation. It has several important limitations:

- The stock list contains today's successful companies and introduces survivorship bias.
- The test assumes an order can be bought at the opening price and sold at the closing price.
- It does not model market gaps, partial fills, order rejection, or liquidity limits.
- Taxes depend on the investor's country and account, so they were not included.
- EUR/USD currency movements were not included even though the securities are US-listed.
- The benchmark used the S&P 500 price index and did not include dividends.
- Ten random seeds are not enough to estimate the probability of future profit.

## Conclusion

The strategy appeared profitable only when trading costs were ignored. Once modest spread, slippage, and fees were included, it lost money in every tested run and eroded most of the starting balance over five years. More testing could refine the estimate, but the current evidence does not support putting real money into this strategy.