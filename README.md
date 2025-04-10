# Tools for algorithmic trading strategies 

## SMA.SMA_backtest(ticker,window,year)
*  ALL ACTIONS OCCUR AT OPEN
*  window gives period for rolling average to be calculated, year calls period of data wanted for backtest
*  Buy condition: Buy first instance of SMA < equity price. Hold for all other instances following.
*  Sell condition: Sell first instance of SMA > equity price. Do nothing for all other instances following.

## SMA.SMA_tradingfunc(ticker,window,type)
*  function for employing SMA strategy using interactive brokers (IB) gateway
*  'mr' => mean reversion strat, aims to capture a securities movement back towards mean
*  'ov; => overvaluation capture strat, aims to capture valuation above mean. Works better with shorter dated window (3-5)
*  window gives period for rolling average to be calculated
*  can change interval through which function operates (eg. 1min or 1day, see lines 31-40, 159)
*  function runs a while True loop. end with Ctrl + c

## RSI_breakout_bt.RSI_breakout(ticker,window,year)
*  ALL ACTIONS OCCUR AT OPEN
*  window gives period for RSI to be calculated, year calls period of data wanted for backtest
*  Buy condition: Buy first instance that RSI < 70. Hold for all other instances following.
*  Sell conditon: Sell first instance that RSI > 70. Do nothing for all other instances following.

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

Currently working on scalping, continual put, pair trading strats (along with implementation)
