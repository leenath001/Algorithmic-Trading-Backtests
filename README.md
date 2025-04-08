# Tools for algorithmic trading strategies 

## Indicators.simple_moving_average(ticker,period)
*  Takes inputs ticker (str) and a period (no of days) to return a simple moving average over the specified period. 

## Indicators.equity_corr(ticker1,ticker2,period)
* Takes 2 tickers and period - outputs correlation between two equities specified.
* Working to get this to take a list of tickers and output a corr matrix for all. 

## SMA_Backtest.SMA_backtest(ticker,window)
*  ALL ACTIONS OCCUR AT OPEN
*  window gives period for rolling average to be calculated 
*  Buy condition: Buy first instance of SMA < equity price. Hold for all other instances following.
*  Sell condition: Sell first instance of SMA > equity price. Do nothing for all other instances following.

## RSI_breakout_bt.RSI_breakout(ticker,window)
*  ALL ACTIONS OCCUR AT OPEN
*  window gives period for RSI to be calculated
*  Buy condition: Buy first instance that RSI < 70. Hold for all other instances following.
*  Sell conditon: Sell first instance that RSI > 70. Do nothing for all other instances following.
*  (ticker = TSLA, window = 9) beats buy/hold
    
## Indicators.Put_Call_ratio(ticker)
*  Returns ratio of puts/calls traded on most active contracts
*  Uses first OTM put and call volume to calculate ratio
*  Ratio > 1 implies expected bearish move -> traders buying more puts than calls
*  Ratio < 1 implies expected bullish move -> traders buying more calls than puts
*  (ticker = UAMY, window = 8) beats buy/hold

## Indicators.RSI(ticker)
*  Returns RSI score at open based on previous 14 trading sessions.
*  Typically, RSI < 30 -> oversold, RSI < 70 -> overbought

Currently working on scalping, continual put, pair trading strats (along with implementation)
