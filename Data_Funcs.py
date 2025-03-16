def opt_data(ticker, type):

    import yfinance as yf
    import pandas as pd

    stoxx = yf.Ticker(ticker)
    expirations = stoxx.options
    for ind,dates in enumerate(expirations):
        print(ind,":",dates)
    choice = int(input('Which date? : '))
    expiry = expirations[choice]
    option_chain = stoxx.option_chain(expiry)
    if type == 'call':
        calls = option_chain.calls
        return expiry, calls[['strike','lastPrice','openInterest','impliedVolatility']]
    elif type == 'put':
        puts = option_chain.puts
        return expiry, puts[['strike', 'lastPrice','openInterest', 'impliedVolatility']]
        
def equity_data(ticker,period):
    
    import yfinance as yf
    import numpy as np
    import datetime

    today = datetime.date.today()
    specified_date = np.busday_offset(today,-period,roll = 'backward')
    today_str = str(today)
    specdate_str = str(specified_date)

    historical_data = yf.download(ticker,specdate_str,today_str)  # data for the last year
    return historical_data

def equity_bidask(ticker):

    import yfinance as yf

    equity = yf.Ticker(ticker)
    bid = equity.info['bid']
    ask = equity.info['ask']

    ba = 'Bid : {}, Ask : {}'.format(bid,ask)

    return ba, bid, ask

def opt_data_IVchain(ticker):

    # function gives us option data for OTM calls/puts, up and down chain for plotting of vol smile/surface
    
    import yfinance as yf
    import pandas as pd
    import numpy as np
    import Data_Funcs as df
    import matplotlib.pyplot as plt

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    # user chooses relevant date of chain, now we have both call and put data 
    stoxx = yf.Ticker(ticker)
    expirations = stoxx.options
    for ind,dates in enumerate(expirations):
        print(ind,":",dates)
    choice = int(input('Which date? : '))
    expiry = expirations[choice]
    option_chain = stoxx.option_chain(expiry)
    calls = option_chain.calls[['strike','lastPrice','openInterest','impliedVolatility']]
    puts = option_chain.puts[['strike','lastPrice','openInterest','impliedVolatility']]

    # grabbing current fair price of underlying
    ba = df.equity_bidask(ticker)
    S = (ba[1] + ba[2])/2 

    # building x by 2 array for data 
    norows = max(len(calls),len(puts))
    volframeputs = pd.DataFrame()
    volframecalls = pd.DataFrame()
    MASVF = pd.DataFrame()

    # find indexes of calls/puts that we call up to
    putstrikesadj = puts.loc[:,'strike'] - S
    callstrikesadj = calls.loc[:,'strike'] - S

    def find_first_positive(column):
            positive_values = column[column > 0]
            if not positive_values.empty:
                return positive_values.index[0]
      
        
    x = find_first_positive(callstrikesadj)
    y = find_first_positive(putstrikesadj) - 1

    # want to populate volframe with IV data
    volframeputs = puts.loc[0:y,:]
    volframecalls = calls.loc[x:,:]
    MASVF = volframeputs._append(volframecalls)
    MASVF.index = range(len(MASVF))

    return MASVF
