import SMA_functions as SMA_functions
import yfinance as yf

# terminal func to run while in clamshell, ensure amphetaime is on

# caffeinate -i python3 "/Users/leenath/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Code/Algos/main.py"

#  caffeinate -i python3 "/Users/nlee/Desktop/Code/Algos/main.py"

# Other strats : continual put, scalp, pair trading, arbitrage? 

''' INVERVAL PARAMETERS
    "1m" Max 7 days, only for recent data
    "2m" Max 60 days
    "5m" Max 60 days
    "15m" Max 60 days
    "30m" Max 60 days
    "60m" Max 730 days (~2 years)
    "90m" Max 60 days
    "1d" '''

#x = SMA.SMA_backtest('TSLA',4,2025,'ov')
# (TSLA,9)

x = SMA_functions.SMA_tradingfunc('SPY',4,'mr')
print()
print(x[0])
print(x[1])