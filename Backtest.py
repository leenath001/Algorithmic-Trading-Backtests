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

# Boolean function creation
def is_pos(n):
    return n > 0

# Check for data leakage
def SMA_backtest(ticker,window): 

    # options for displaying data
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    warnings.filterwarnings("ignore")
    pd.set_option('display.float_format', '{:.2f}'.format)

    # Boolean function creation
    def is_pos(n):
        return n > 0

    # Backtest for Simple Moving Average Strategy. SMA_window gives period for rolling average to be calculated 
    # Buy conditions: Buy first instance of SMA > equity price. Hold for all other instances following.
    # Sell conditions: Sell first instance of SMA < equity price. Do nothing for all other instances following. 

    # getting equity data, SMA data, and Boolean data (used to define when entry threshold crossed)
    data = yf.download(ticker, period='3y', interval='1d')
    SMA = data['Close'].rolling(window).mean().shift(1)
    open = data[['Open']]
    close = data[['Close']]
    SMA = SMA.iloc[window-1:]
    delta = SMA - close                        # Truth vector
    delta = delta.apply(is_pos)
    delta = pd.DataFrame(delta[window-1:])
    open = open[window-1:]
    close = close[window-1:]                    # slicing data from periods where SMA not calucluated
    CminO = close.values-open.values

    # Running backtest
    P = 0                                       # Boolean. 0 -> no position, 1 -> long positon
    alo = open.iloc[0]                          # initial allocation, should change to # of stocks 
    alo = alo[0]
    valuevec = alo * np.ones(len(SMA))          # stores bt historical values
    buyhold = alo * np.ones(len(SMA))           # values of buy/hold 
    actionvec = np.empty(len(SMA),object)

    # what about insead of going all the way back we do open, close for comparison
    # current period and last period 

    # condition to run 
    for i in range(2,len(SMA)):
        delta1 = delta.iloc[i-1,0]
        delta2 = delta.iloc[i-2,0]
        buyhold[i] = buyhold[i-1] * (1 +  (CminO[i])/open.iloc[i,0])

        if P == 0 and delta1 == False and delta2 == True: #buy
            P = 1
            valuevec[i] = valuevec[i-1] * (1 +  (CminO[i])/open.iloc[i,0])
            actionvec[i] = 'B'

        elif P == 1 and delta1 == False and delta2 == False: # hold
            valuevec[i] = valuevec[i-1] * (1 +  (CminO[i])/open.iloc[i,0])
            actionvec[i] = 'H'

        elif P == 1 and delta1 == True and delta2 == False: # sell
            P = 0 
            valuevec[i] = valuevec[i-1] * (1 + (open.iloc[i,0]-close.iloc[i-1,0])/close.iloc[i-1,0])
            actionvec[i] = 'S'

        elif P == 0 and delta1 == True and delta2 == True: # do nothing
            valuevec[i] = valuevec[i-1]
            actionvec[i] = 'N'

    # creating dataframe for comparison of strategy
    title = '{}d SMA'.format(window)
    buyhold = pd.DataFrame(buyhold, index = open.index)
    buyhold = buyhold.rename(columns={buyhold.columns[0]: 'Buy/Hold'})
    valuevec = pd.DataFrame(valuevec, index = open.index)
    valuevec = valuevec.rename(columns={valuevec.columns[0]: 'Strat Val'})
    actionvec = pd.DataFrame(actionvec, index = open.index)
    actionvec = actionvec.rename(columns={actionvec.columns[0]: 'Action'})
    open = pd.DataFrame(open, index = open.index)
    close = pd.DataFrame(close, index = open.index)
    open = open.rename(columns={open.columns[0]: 'Open'})
    close = close.rename(columns={close.columns[0]: 'Close'})
    SMA = SMA.rename(columns={SMA.columns[0]: title})
    comb = pd.concat([open,close, SMA,actionvec, valuevec,buyhold], axis=1)
    comb = comb.iloc[window-1:,:]
    print()
    print(comb)  

    plt.figure()
    plt.plot(comb.index,comb.loc[:,"Strat Val"],label = 'Strategy')
    #plt.plot(comb.index,comb.loc[:,"Buy/Hold"],label = 'Buy/Hold')
    plt.plot(close.index,close,label = "Close",color = 'orange')
    plt.plot(comb.index,comb.loc[:,title],label = title,color = 'black')
    plt.xlabel("Timestamp")

    buy_dates = comb[actionvec["Action"] == "B"].index

    for date in buy_dates:
        shifted_date = comb.index[comb.index.get_loc(date) - 1]  # Shift back by 2
        plt.scatter(x=shifted_date, y=comb.loc[date, title], color='green', marker='v', s=10)
        plt.scatter(x=shifted_date, y=comb.loc[date, 'Strat Val'] + 2, color='green', marker='v', s=10)

    sell_dates = actionvec[actionvec["Action"] == "S"].index

    for date in sell_dates:
        shifted_date = comb.index[comb.index.get_loc(date) - 1]  # Shift back by 2
        plt.scatter(x=shifted_date, y=comb.loc[date, title] , color='red', marker='v', s=10)
        plt.scatter(x=shifted_date, y=comb.loc[date, 'Strat Val'] +2, color='red', marker='v', s=10)

    plt.ylabel("Value")
    plt.xticks(rotation=30)
    plt.legend()
    plt.title("SMA strategy vs Buy & Hold : {}".format(ticker))
    plt.show()


