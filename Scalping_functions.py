import yfinance as yf
import pandas as pd
import numpy as np
import Indicators as I
import matplotlib.pyplot as plt
import warnings
from ib_insync import *
import time
import pytz 

# options for displaying data
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
np.set_printoptions(suppress=True, formatter={'float': '{:.2f}'.format})
warnings.filterwarnings("ignore")

# Boolean indicator function
def is_pos(n):
    return n > 0

def Scalping_tradingfunc(ticker):

    # data initialization
    curr_pr = yf.Ticker(ticker)
    curr_pr = curr_pr.fast_info['last_price']
        
    # set up IB connection out of loop (id 2)
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=3)

    # dataframe initialization
    actionvec = ['N']
    valuevec = [curr_pr]
    buyholdvec = [curr_pr]
    timevec = [pd.Timestamp.now(tz='US/Eastern')]
    truths = ['NA']

    # trading variables
    P = 0
    S1 = 1 
    S2 = curr_pr
    entry = 1
    newhold = 1

    while True: 
        try:
            # loading data 
            curr = yf.Ticker(ticker)
            curr = curr.fast_info['last_price']
            curr = np.round(curr,2)
            S1 = S2
            S2 = curr
            truth = is_pos(S2-S1)

            # position logic, update all df's within each loop
            if P == 0 and truth == True: #buy
                P = 1
                contract = Stock(ticker, 'SMART', 'USD')
                order = MarketOrder('BUY', 10)
                trade = ib.placeOrder(contract, order)
                entry = curr
                actionvec = np.append(actionvec,'B')
                valuevec = np.append(valuevec,valuevec[-1]) 
                timevec = np.append(timevec,pd.Timestamp.now(tz='US/Eastern'))
                bhvec = np.append(bhvec,curr)
                truths = np.append(truths,truth)
                print('Buying @ {}'.format(curr))
                time.sleep(1)
                print("Order Status:", trade.orderStatus.status)

            elif P == 1 and truth == True: #hold
                if actionvec[-1] == 'B':
                    valuevec = np.append(valuevec,valuevec[-1] * curr/entry) 
                    newhold = curr
                elif actionvec[-1] == 'H':
                    valuevec = np.append(valuevec,valuevec[-1] * curr/newhold)
                    newhold = curr
                timevec = np.append(timevec,pd.Timestamp.now(tz='US/Eastern'))
                actionvec = np.append(actionvec,'H')
                bhvec = np.append(bhvec,curr)
                truths = np.append(truths,truth)
                print('Holding')
                time.sleep(1)

            elif P == 1 and truth == False: #sell
                contract = Stock(ticker, 'SMART', 'USD')
                order = MarketOrder('SELL', 10)
                trade = ib.placeOrder(contract, order)
                P = 0
                if actionvec[-1] == 'B':
                    valuevec = np.append(valuevec,valuevec[-1] * curr/entry) 
                elif actionvec[-1] == 'H':
                    valuevec = np.append(valuevec,valuevec[-1] * curr/newhold)
                timevec = np.append(timevec,pd.Timestamp.now(tz='US/Eastern'))
                actionvec = np.append(actionvec,'S')
                bhvec = np.append(bhvec,curr)
                truths = np.append(truths,truth) 
                print('Selling @ {}'.format(curr))
                time.sleep(1)
                print("Order Status:", trade.orderStatus.status)

            elif P == 0 and truth == False: # nothing
                timevec = np.append(timevec,pd.Timestamp.now(tz='US/Eastern'))
                actionvec = np.append(actionvec,'N')
                bhvec = np.append(bhvec,curr)
                truths = np.append(truths,truth)
                valuevec = np.append(valuevec,valuevec[-1])
                time.sleep(1)
                print('No Action')

            time.sleep(4)

        # keyboard stop exception
        except KeyboardInterrupt:

            if P == 1: 
                contract = Stock(ticker, 'SMART', 'USD')
                order = MarketOrder('SELL', 10)
                trade = ib.placeOrder(contract, order)
                curr = yf.Ticker(ticker)
                curr = curr.fast_info['last_price']
                curr = np.round(curr,2)
                if actionvec[-1] == 'B':
                    valuevec = np.append(valuevec,valuevec[-1] * curr/entry) 
                elif actionvec[-1] == 'H':
                    valuevec = np.append(valuevec,valuevec[-1] * curr/newhold) 
                timevec = np.append(timevec,pd.Timestamp.now(tz='US/Eastern'))
                actionvec = np.append(actionvec,'N')
                bhvec = np.append(bhvec,curr)
                truths = np.append(truths,"NA")
                
            print(" Stopped by user.")
            break

        # error exception
        except Exception as e:
            print("Error:", e)
            time.sleep(6)

    # trading strats/summary, np -> pd dataframe construction
    beta = np.cov(valuevec,bhvec)/np.var(bhvec)
    beta = beta[0,1]

    actionvec = pd.DataFrame(actionvec,columns=['Actions'])
    valuevec = pd.DataFrame(valuevec,columns=['Values'])
    bhvec = pd.DataFrame(bhvec,columns=['Buy/Hold'])
    truths = pd.DataFrame(truths,columns=['T/F'])
    ret = pd.concat([truths,actionvec,valuevec.round(2),bhvec.round(2)],axis = 1)
    ret.index = pd.to_datetime(timevec)
    ret.index.name = 'Timestamp'

    pctg = (ret.iloc[len(ret)-1,2]-ret.iloc[0,2])/ret.iloc[0,2] * 100
    bhpctg = (ret.iloc[len(ret)-1,3]-ret.iloc[0,3])/ret.iloc[0,3] * 100

    risk_free = .0422 # adjust as needed
    alpha = pctg - [risk_free + beta * (bhpctg - risk_free)]
    alpha = alpha[0]

    text = '\n'.join((
        '                  ',
        'Asset : {}'.format(ticker),
        'Trading Periods : {}'.format(len(ret)),
        #'P&L : ${}'.format((ret.iloc[len(ret)-1,1]- ret.iloc[0,1]).round(2)),
        'Growth : {}%'.format(pctg.round(2)),
        'Buy/Hold Growth : {}%'.format(bhpctg.round(2)),
        'Beta (asset-relative) : {}'.format(beta.round(2)),
        'Alpha (asset-relative) : {}%'.format(np.round(alpha*100,2)),
        '                  '
    ))

    # plotting functions 
    plt.figure()
    plt.plot(ret.index,ret.loc[:,"Values"],label = 'Strategy',color = 'green')
    plt.plot(ret.index,ret.loc[:,'Buy/Hold'],label = "Close",color = 'orange')
    plt.xlabel("Timestamp")

    '''
    buy_dates = ret[ret["Actions"] == "B"].index

    for date in buy_dates:
        plt.scatter(x=date, y=ret.loc[date, 'Values'], color='lime', marker='v', s=7,zorder= 2)

    sell_dates = ret[ret["Actions"] == "S"].index

    for date in sell_dates:
        plt.scatter(x=date, y=ret.loc[date, 'Values'], color='red', marker='v', s=7,zorder= 2)
    '''

    plt.ylabel("Value")
    plt.xticks(rotation=30)
    plt.legend()
    plt.title("Strategy vs Buy & Hold : {} (S = {})".format(ticker,ret.iloc[0,3].round(2)))
    plt.show()

    return ret, text
