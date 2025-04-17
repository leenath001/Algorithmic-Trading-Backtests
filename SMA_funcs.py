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

# Backtest function (ensure rules for bt and trade are the same, using same data)
def SMA_backtest(ticker,window,year,type): 

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
    data = yf.download(ticker, period='7d', interval = '5m',progress=False)
    SMA = data['Close'].rolling(window).mean().shift(1)
    open = data[['Open']]
    close = data[['Close']]
    SMA = SMA.iloc[window-1:]
    if type == 'ov':
        delta = SMA - close                         # Truth vector, close - SMA -> mean reversion, SMA - close -> overvaluation capture 
        delta = delta.apply(is_pos)
    elif type == 'mr':
        delta = close - SMA                         # Truth vector, close - SMA -> mean reversion, SMA - close -> overvaluation capture 
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
    title = '{} per SMA'.format(window)
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

    risk_free = .0422 # adjust as needed
    # alpha of strategy vs specific asset

    text = '\n'.join((
        '                  ',
        'Trading Periods : {}'.format(len(comb)),
        'P&L : ${}'.format((comb.iloc[len(comb)-1,4]- alo).round(2)),
        'Growth : {}%'.format(pctg.round(2)),
        'Buy/Hold Growth : {}%'.format(bhpctg.round(2)),
        '                  '
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

# Trading function 
#   for ov - we should change sell to SMA + 1.01 or 1.02, instead of waiting for SMA to catch up with current price, we try to sell at peak 
#   ideally we want to track value by calling ib brokerage to find account/equity value instead of using proxy, giving innaccurate #s
def SMA_tradingfunc(ticker,window,type):
    
    P = 0
    actionvec = ['N']
    curr_pr = yf.Ticker(ticker)
    curr_pr = curr_pr.fast_info['last_price']
    valuevec = [curr_pr]
    bhvec = [curr_pr] 
    timevec = [pd.Timestamp.now(tz='US/Eastern')]
    bh = 1
    entry = 1
    newhold = 1

    ## setting up ib connection (id 1)
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=1)

    ## loop to download data, run thru, take signals and act/trade on them 
    while True:
        try:

            # data collection loop (check every 25s)
            data = yf.download(ticker, period='1d', interval='1m',progress=False)
            if data.index.tz is None:
                data.index = data.index.tz_localize('UTC')
            data.index = data.index.tz_convert('US/Eastern')

            # loop to handle exception if data empty/not long enough
            if data.empty or len(data) < window + 2:
                print("Not enough data yet...")
                time.sleep(20)
                continue

            # compute SMA
            SMA = data['Open'].rolling(window).mean()
            if type == 'mr':
                delta = data['Open'] - SMA # data - SMA => mean reversion
                delta = delta.apply(is_pos)
            elif type == 'ov':
                delta = SMA - data['Open'] # SMA - data => capturing overvaluation,
                delta = delta.apply(is_pos)
        
            # dataframe
            comb = pd.concat([data['Open'].round(2),SMA.round(2),delta],axis = 1)
            comb = comb.iloc[-10:,:]
            comb.columns = ['Open','SMA','Signal']
            print()
            print(comb)
        
            # signal logic
            d1 = comb.iloc[-1,2]
            d2 = comb.iloc[-2,2]

            curr_pr = yf.Ticker(ticker)
            curr_pr = curr_pr.fast_info['last_price']
            bh = yf.Ticker(ticker).fast_info['last_price']

            if P == 0 and d1 == False and d2 == True: #buy 
                P = 1
                contract = Stock(ticker, 'SMART', 'USD')
                order = MarketOrder('BUY', 10)
                trade = ib.placeOrder(contract, order)
                entry = curr_pr
                actionvec = np.append(actionvec,'B')
                valuevec = np.append(valuevec,valuevec[-1]) 
                timevec.append(data.index[-1])
                bhvec = np.append(bhvec,bh)
                print('Buying')
                time.sleep(5)
                print("Order Status:", trade.orderStatus.status)

            elif P == 1 and d1 == False: # and d2 == False or P == 1 and d1 == False and d2 == True: # hold, account for slippage
                if actionvec[-1] == 'B':
                    valuevec = np.append(valuevec,valuevec[-1] * curr_pr/entry) 
                    timevec.append(data.index[-1])
                    newhold = curr_pr
                elif actionvec[-1] == 'H':
                    valuevec = np.append(valuevec,valuevec[-1] * curr_pr/newhold)
                    timevec.append(data.index[-1])
                    newhold = curr_pr
                actionvec = np.append(actionvec,'H')
                bhvec = np.append(bhvec,bh)
                print('Holding')
                time.sleep(5)

            elif P == 1 and d1 == True: #and d2 == False or P == 1 and d1 == d2 == True: # sell @ open
                P = 0
                contract = Stock(ticker, 'SMART', 'USD')
                order = MarketOrder('SELL', 10)
                trade = ib.placeOrder(contract, order)
                if actionvec[-1] == 'B':
                    valuevec = np.append(valuevec,valuevec[-1] * curr_pr/entry) 
                elif actionvec[-1] == 'H':
                    valuevec = np.append(valuevec,valuevec[-1] * curr_pr/newhold) 
                timevec.append(data.index[-1])
                actionvec = np.append(actionvec,'S')
                bhvec = np.append(bhvec,bh)
                print('Selling')
                time.sleep(5)
                print("Order Status:", trade.orderStatus.status)

            elif P == 0 and d1 == True or P == 0 and d1 == d2 == False: # and d2 == True or P == 0 and d1 == True and d2 == False or P == 0 and d1 == False and d2 == False: # do nothing
                actionvec = np.append(actionvec,'N')
                valuevec = np.append(valuevec,valuevec[-1]) 
                timevec.append(data.index[-1])
                bhvec = np.append(bhvec,bh)
                print('No Action')
                time.sleep(5)
            
            time.sleep(15)

        except KeyboardInterrupt:

            if P == 1: 
                curr_pr = yf.Ticker(ticker)
                curr_pr = curr_pr.fast_info['last_price']
                contract = Stock(ticker, 'SMART', 'USD')
                order = MarketOrder('SELL', 10)
                trade = ib.placeOrder(contract, order)
                if actionvec[-1] == 'B':
                    valuevec = np.append(valuevec,valuevec[-1] * curr_pr/entry) 
                elif actionvec[-1] == 'H':
                    valuevec = np.append(valuevec,valuevec[-1] * curr_pr/newhold) 
                timevec.append(data.index[-1])
                actionvec = np.append(actionvec,'S')
                bhvec = np.append(bhvec,curr_pr)
                
            print("  Stopped by user.")
            break

        except Exception as e:
            print("Error:", e)
            time.sleep(20)
    
    # beta of strategy vs specific asset movement
    beta = np.cov(valuevec,bhvec)/np.var(bhvec)
    beta = beta[0,1]

    # values returned
    actionvec = pd.DataFrame(actionvec,columns=['Actions'])
    valuevec = pd.DataFrame(valuevec,columns=['Values'])
    bhvec = pd.DataFrame(bhvec,columns=['Buy/Hold'])
    ret = pd.concat([actionvec,valuevec.round(2),bhvec.round(2)],axis = 1)
    ret.index = pd.to_datetime(timevec)
    ret.index.name = 'Timestamp'

    pctg = (ret.iloc[len(ret)-1,1]-ret.iloc[0,1])/ret.iloc[0,1] * 100
    bhpctg = (ret.iloc[len(ret)-1,2]-ret.iloc[0,2])/ret.iloc[0,2] * 100

    risk_free = .0422 # adjust as needed
    # alpha of strategy vs specific asset
    alpha = pctg - [risk_free + beta * (bhpctg - risk_free)]
    alpha = alpha[0]

    text = '\n'.join((
        '                  ',
        'Asset & Strategy : {}, {}'.format(ticker,type),
        'Trading Periods : {}'.format(len(ret)),
        #'P&L : ${}'.format((ret.iloc[len(ret)-1,1]- ret.iloc[0,1]).round(2)),
        'Growth : {}%'.format(pctg.round(2)),
        'Buy/Hold Growth : {}%'.format(bhpctg.round(2)),
        'Beta (asset-relative) : {}'.format(beta.round(2)),
        'Alpha (asset-relative) : {}%'.format(np.round(alpha*100,2)),
        '                  '
    ))

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
    plt.title("Strategy vs Buy & Hold : {} (S0 = {})".format(ticker,np.round(curr_pr,2)))
    plt.show()

    return ret,text
