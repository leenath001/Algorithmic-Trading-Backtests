import Scalping_functions as SC
import yfinance as yf

# terminal func to run while in clamshell, ensure amphetaime is on

# macair
# caffeinate -i python3 "/Users/leenath/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Code/Algos/Scapling_execution.py"

# macmini
# caffeinate -i python3 "/Users/leenath/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Code/Algos/Scapling_execution.py"

# Other strats : continual put, pair trading, arbitrage? 

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

x = SC.Scalping_tradingfunc('QQQ')
print()
print(x[0])
print(x[1])