import Data_Funcs as df
import yfinance as yf
import pandas as pd
import numpy as np
import Indicators as I
import matplotlib.pyplot as plt

## Test how SMA strategy performs against buy/hold

# options for displaying data
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
np.set_printoptions(suppress=True, formatter={'float': '{:.2f}'.format})

# Boolean function creation
def is_pos(n):
    return n > 0

def SMA_backtest(ticker,SMA_window): 

    # Backtest for Simple Moving Average Strategy. SMA_window gives period for rolling average to be calculated 
    # Buy conditions: Buy first instance of SMA > equity price. Hold for all other instances following.
    # Sell conditions: Sell first instance of SMA < equity price. Do nothing for all other instances following. 
    
    # SMA period
    window = SMA_window

    # getting equity data, SMA data, and Boolean data (used to define when entry threshold crossed)
    data = yf.download(ticker, period='1y', interval='1d')
    SMA = data['Close'].rolling(window).mean()
    tst = len(SMA) - (window)
    equity = data['Close']
    SMA = SMA.iloc[window-1:]
    delta = SMA - equity
    delta = delta.apply(is_pos)
    delta = pd.DataFrame(delta)

    # True -> SMA > equity, buy/hold. False -> equity > SMA, do nothing/sell

    # Running backtest
    P = 0 # Boolean. 0 -> no position, 1 -> long positon
    alo = 100 # initial allocation
    valuevec = alo * np.ones(len(equity)) # stores bt historical values
    buyhold = alo * np.ones(len(equity)) # values of buy/hold 
    actionvec = np.empty(len(equity),object)

    # condition to run 
    for i in range(1,len(equity)):
        delta1 = delta.iloc[i,0]
        delta2 = delta.iloc[i-1,0]
        buyhold[i] = buyhold[i-1] * (1 +  (equity.iloc[i,0] - equity.iloc[i-1,0])/equity.iloc[i-1,0])
    
        if P == 0 and delta1 == False and delta2 == True: #buy
            P = 1
            valuevec[i] = valuevec[i-1] * (1 +  (equity.iloc[i,0] - equity.iloc[i-1,0])/equity.iloc[i-1,0])
            actionvec[i] = 'B'

        elif P == 1 and delta1 == False and delta2 == False: # hold
            valuevec[i] = valuevec[i-1] * (1 +  (equity.iloc[i,0] - equity.iloc[i-1,0])/equity.iloc[i-1,0])
            actionvec[i] = 'H'

        elif P == 1 and delta1 == True and delta2 == False: # sell
            P = 0 
            valuevec[i] = valuevec[i-1]
            actionvec[i] = 'S'

        elif P == 0 and delta1 == True and delta2 == True: # do nothing
            valuevec[i] = valuevec[i-1]
            actionvec[i] = 'NA'

    # creating dataframe for comparison of strategy
    buyhold = pd.DataFrame(buyhold, index = equity.index)
    buyhold = buyhold.rename(columns={buyhold.columns[0]: 'Buy/Hold'})
    valuevec = pd.DataFrame(valuevec, index = equity.index)
    actionvec = pd.DataFrame(actionvec, index = equity.index)
    actionvec = actionvec.rename(columns={actionvec.columns[0]: 'Action'})
    valuevec = valuevec.rename(columns={valuevec.columns[0]: 'Strat Val'})
    equity = equity.rename(columns={equity.columns[0]: 'Close Prices'})
    SMA = SMA.rename(columns={SMA.columns[0]: '{}d SMA'.format(window)})
    delta = delta.rename(columns={delta.columns[0]: 'isPos'})
    comb = pd.concat([equity, SMA, delta,actionvec, valuevec,buyhold], axis=1)
    print()
    print(comb.iloc[window-1:,:])  

    plt.figure()
    plt.plot(comb.index,valuevec,label = 'Strategy')
    plt.plot(comb.index,buyhold,label = 'Buy/Hold')
    plt.plot(comb.index,comb.loc[:,'Close Prices'],label = '{} Close Prices'.format(ticker))
    plt.plot(comb.index,comb.loc[:,'5d SMA'],label = '{}d SMA'.format(window))
    plt.xlabel("Timestamp")
    plt.ylabel("Value")
    plt.xticks(rotation=30)
    plt.legend()
    plt.title("SMA strategy vs Buy & Hold : {}".format(ticker))
    plt.show()
