def simple_moving_average(ticker,period):
    ## moving average function based on close data
    import warnings
    warnings.filterwarnings("ignore")
    import numpy as np
    import Data_Funcs as df
    import pandas as pd

    def form_b(num):
        return f"{num:.2f}"

    data = df.equity_data(ticker, period)
    close = data.loc[:,'Close']
    PMA = np.sum(close)/(period + 1)
    PMA = PMA.iat[0]

    return form_b(PMA)
    
def equity_corr(ticker1,ticker2,period):
    import Data_Funcs as df
    import pandas as pd
    import numpy as np

    pd.set_option('display.max_rows', None)  
    pd.set_option('display.max_columns', None)

    equityone = df.equity_data(ticker1,period)
    equitytwo = df.equity_data(ticker2,period)
    equityone = equityone["Close"]
    equitytwo = equitytwo["Close"]

    combined_df = equityone.join(equitytwo, lsuffix = ticker1,rsuffix = ticker2)
    corr_matrix = combined_df.corr()

    return corr_matrix

def Put_Call_ratio(ticker):
    import yfinance as yf
    import Data_Funcs as df
    import pandas as pd
    import warnings
    import numpy

    warnings.filterwarnings("ignore")
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    # getting most recent expiry date   
    stoxx = yf.Ticker(ticker)
    expirations = stoxx.options

    for dates in expirations: 
        expiry = dates

        # getting chain
        option_chain = stoxx.option_chain(expiry)
        calls = option_chain.calls
        x =  calls[['strike','volume']]
        x1 = x[['volume']]
       
        puts = option_chain.puts
        y = puts[['strike','volume',]]
        y1 = y[['volume']]

        # closest to money strike, OTM. 
        S = df.equity_bidask(ticker) # tkr price
        S = S[1]
        xmod = calls[['strike']]-S
        ymod = puts[['strike']]-S
        C_first_positive = (calls['strike'] - S).gt(0).idxmax()
        P_first_positive = (puts['strike'] - S).gt(0).idxmax() - 1 

    # puts/calls, >1 -> p > c -> bearish, <1 -> p < c -> bullish

        # implementing formula P_vol/C_vol
        Cvol = x1.iloc[C_first_positive]
        Pvol = y1.iloc[P_first_positive]
        Cvol = Cvol.to_numpy()
        Pvol = Pvol.to_numpy()

        ratio = Pvol/Cvol
        ratio = ratio[0]

        str = "{} Put to Call Ratio : {}".format(dates,ratio)
        print(str)

def RSI(ticker):
    
    import yfinance as yf
    import pandas as pd
    import numpy as np
    import Indicators as I
    import matplotlib.pyplot as plt
    import warnings

    def is_pos(n):
        return n > 0

    # options for displaying data
    warnings.filterwarnings("ignore")

# getting ticker data
    data = yf.download(ticker, period='1mo', interval='1d')
    open = data[["Open"]]
    close = data[["Close"]]
    percents = (close.values - open.values)/open.values
    percents = pd.DataFrame(percents, index = open.index, columns=["% Change"])
    truths = percents.apply(is_pos)
    truths = truths.rename(columns={'% Change': 'isPos'})
 
    # want to calculate rsi for period of 14 days (SEE NOTES)

    # NEED TO CHANGE ST WE HAVE VEC OF RSI FOR EACH DAY
    recent_percents = percents.iloc[-15:-1,0]
    recent_truths = truths.iloc[-15:-1,0]

    possum = 0
    negsum = 0
    poscount = 0
    negcount = 0

    for i in range(len(recent_truths)):
    
        if recent_truths.iloc[i] == True:
            possum += recent_percents.iloc[i]
            poscount += 1

        elif recent_truths.iloc[i] == False:
            negsum += recent_percents.iloc[i]
            negcount += 1

    avgain = possum/poscount
    avloss = negsum/negcount

    # RSI is calculated for yesterday, for comparison today. 
    RSI = 100 - 100/(1 - (avgain/avloss))
    
    return RSI






