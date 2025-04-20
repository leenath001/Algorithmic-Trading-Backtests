# Tools for algorithmic trading strategies 

See strategy-specific repositiries for trading functions and backtesting functions.

## Indicators.simple_moving_average(ticker,period)
*  Takes inputs ticker (str) and a period (no of days) to return a simple moving average over the specified period. 

## Indicators.equity_corr(ticker1,ticker2,period)
* Takes 2 tickers and period - outputs correlation between two equities specified.
* Working to get this to take a list of tickers and output a corr matrix for all. 
    
## Indicators.Put_Call_ratio(ticker)
*  Returns ratio of puts/calls traded on most active contracts
*  Uses first OTM put and call volume to calculate ratio
*  Ratio > 1 implies expected bearish move -> traders buying more puts than calls
*  Ratio < 1 implies expected bullish move -> traders buying more calls than puts

## Indicators.RSI(ticker)
*  Returns RSI score at open based on previous 14 trading sessions.
*  Typically, RSI < 30 -> oversold, RSI < 70 -> overbought
