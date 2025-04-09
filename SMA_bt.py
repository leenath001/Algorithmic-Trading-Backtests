import Data_Funcs as df
import yfinance as yf
import pandas as pd
import numpy as np
import Indicators as I
import matplotlib.pyplot as plt
import warnings

## Test how SMA strategy performs against buy/hold

# options for displaying data
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
np.set_printoptions(suppress=True, formatter={'float': '{:.2f}'.format})
warnings.filterwarnings("ignore")

# Boolean function creation
def is_pos(n):
    return n > 0

# Check for data leakage
def SMA_backtest(ticker,window,year): 

    warnings.filterwarnings("ignore")

    # Backtest for Simple Moving Average Strategy. SMA_window gives period for rolling average to be calculated 
    # Buy conditions: Buy first instance of SMA > equity price. Hold for all other instances following.
    # Sell conditions: Sell first instance of SMA < equity price. Do nothing for all other instances following. 

    ''' INVERVAL PARAMETERS
    "1m" Max 7 days, only for recent data
    "2m" Max 60 days
    "5m" Max 60 days
    "15m" Max 60 days
    "30m" Max 60 days
    "60m" Max 730 days (~2 years)
    "90m" Max 60 days
    "1d"
    '''

    # getting equity data, SMA data, and Boolean data (used to define when entry threshold crossed)
    data = yf.download(ticker, period='30d', interval='1d')
    SMA = data['Close'].rolling(window).mean().shift(1)
    open = data[['Open']]
    close = data[['Close']]
    SMA = SMA.iloc[window-1:]
    delta = SMA - close                         # Truth vector, close - SMA -> mean reversion, SMA - close -> overvaluation capture 
    delta = delta.apply(is_pos)
    delta = pd.DataFrame(delta[window-1:])
    SMA = pd.DataFrame(SMA)
    open = open[window-1:]
    close = close[window-1:]                    # slicing data from periods where SMA not calucluated
    CminO = close.values-open.values
    comb = pd.concat([open.round(2),close.round(2)],axis = 1)

    # Running backtest
    P = 0                                       # Boolean. 0 -> no position, 1 -> long positon
    alo = comb.iloc[0,0]                        # initial allocation, should change to # of stocks 
    valuevec = alo * np.ones(len(SMA))          # stores bt historical values
    actionvec = np.empty(len(SMA),object)

    for i in range(2,len(SMA)):
        delta1 = delta.iloc[i-1,0]
        delta2 = delta.iloc[i-2,0]

        if P == 0 and delta1 == False and delta2 == True: #buy @ open
            P = 1
            valuevec[i] = valuevec[i-1] * (1 +  (CminO[i])/open.iloc[i,0])
            actionvec[i] = 'B'

        elif P == 1 and delta1 == False and delta2 == False: # hold, account for slippage
            valuevec[i] = valuevec[i-1] * (1 +  (CminO[i])/open.iloc[i,0]) * (1 + (open.iloc[i,0] - close.iloc[i-1,0])/close.iloc[i-1,0])
            actionvec[i] = 'H'

        elif P == 1 and delta1 == True and delta2 == False or P == 1 and (1 + (close.iloc[i-1,0]-open.iloc[i-1,0])/open.iloc[i-1,0]) <=.99:
            P = 0 
            valuevec[i] = valuevec[i-1] * (1 + (open.iloc[i,0]-close.iloc[i-1,0])/close.iloc[i-1,0])
            actionvec[i] = 'S'

        elif P == 0 and delta1 == True and delta2 == True: # do nothing
            valuevec[i] = valuevec[i-1]
            actionvec[i] = 'N'

    # creating dataframe for comparison of strategy
    title = '{}d SMA'.format(window)
    valuevec = pd.DataFrame(valuevec, index = open.index, columns=["Strat Val"])
    actionvec = pd.DataFrame(actionvec, index = open.index,columns=["Action"])
    SMA = SMA.rename(columns={'TSLA':"SMA"})
    comb = pd.concat([comb,SMA.round(2),actionvec,valuevec.round(2)], axis=1)

    #print()
    #print(comb)

    plt.figure()
    plt.plot(comb.index,comb.loc[:,"Strat Val"],label = 'Strategy',color = 'green')
    plt.plot(comb.index,close.loc[:,'Close'],label = "Close",color = 'orange')
    plt.plot(SMA.index,SMA.iloc[:,0],label = title,color = 'black',alpha = .3,linestyle = 'dashed')
    plt.xlabel("Timestamp")

    buy_dates = comb[comb["Action"] == "B"].index

    for date in buy_dates:
        #plt.axvline(x = shifted_date,color='green')
        #plt.scatter(x=date, y=close.loc[date], color='lime', marker='x', s=7,zorder= 2)
        plt.scatter(x=date, y=comb.loc[date, 'Strat Val'], color='lime', marker='v', s=7,zorder= 2)

    sell_dates = comb[comb["Action"] == "S"].index

    for date in sell_dates:
        #plt.axvline(x = shifted_date,color='red')
        #plt.scatter(x=date, y=close.loc[date] , color='red', marker='s', s=7,zorder= 2)
        plt.scatter(x=date, y=comb.loc[date, 'Strat Val'], color='red', marker='v', s=7,zorder= 2)

    plt.ylabel("Value")
    plt.xticks(rotation=30)
    plt.legend()
    plt.title("SMA strategy vs Buy & Hold : {} (S0 = {})".format(ticker,alo))
    plt.show()

    pctg = (comb.iloc[len(comb)-1,4]-alo)/alo * 100
    bhpctg = (comb.iloc[len(comb)-1,1]-comb.iloc[0,0])/comb.iloc[0,0] * 100

    text = '\n'.join((
        'Trading Days : {}'.format(len(comb)),
        'P&L : ${}'.format((comb.iloc[len(comb)-1,4]- alo).round(2)),
        'Growth : {}%'.format(pctg.round(2)),
        'Buy/Hold Growth : {}%'.format(bhpctg.round(2))
    ))

    def slice_by_year(df):
    # Create a dictionary of DataFrames split by year
        year_slices = {
            year: group for year, group in df.groupby(df.index.year)
    }
        return year_slices

    yearly_data = slice_by_year(comb)

    if year == 'all':
        return comb,text
    else:
        return yearly_data[year],text
