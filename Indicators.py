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
    expiry = expirations[0]

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
    C_first_positive = xmod.apply(lambda x: x[x > 0].index.min()) # first pos ind
    P_first_positive = ymod.apply(lambda x: x[x > 0].index.min()) - 1 # last neg ind

    # puts/calls, >1 -> p > c -> bearish, <1 -> p < c -> bullish

    # implementing formula P_vol/C_vol
    Cvol = x1.iloc[C_first_positive]
    Pvol = y1.iloc[P_first_positive]
    Cvol = Cvol.to_numpy()
    Pvol = Pvol.to_numpy()

    ratio = Pvol/Cvol
    ratio = ratio[0]

    return ratio[0]



