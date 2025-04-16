import RSI_functions as RSI
import yfinance as yf

# terminal func to run while in clamshell, ensure amphetaime is on

# macair
# caffeinate -i python3 "/Users/leenath/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Code/Algos/RSI_execution.py"

# macmini
# caffeinate -i python3 "/Users/nlee/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Code/Algos/RSI_execution.py"

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

#x = RSI.RSI_breakout_backtest('RKLB',12,2025)
# (UAMY,8)

x = RSI.RSI_tradingfunc('SPY',9)
print()
print(x[0])
print(x[1])