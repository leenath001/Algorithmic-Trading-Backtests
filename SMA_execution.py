import SMA_functions as SMA_functions
import yfinance as yf

# terminal func to run while in clamshell, ensure amphetaime is on

# caffeinate -i python3 "{filepath}"

#x = SMA.SMA_backtest('TSLA',4,2025,'ov')
# (TSLA,9)

x = SMA_functions.SMA_tradingfunc('SPY',4,'mr')

history = x[0]
stats = x[1]

print()
print(history)
print(stats)
