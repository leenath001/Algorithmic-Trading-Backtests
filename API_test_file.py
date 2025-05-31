## want to test Interactive Brokers quotes (need to pay)
# Use IB quotes (30/m + commission) OR Polygon (200 flat)
# Also consider using finnhub API to replace yfinance

from ib_insync import *

# Connect to IB Gateway or TWS (4001 Live 4002 Paper)
'''
ib = IB()
ib.connect('127.0.0.1', 4001, clientId=1)

# Define the contract
contract = Stock('SPY', 'SMART', 'USD')

# Request market data
market_data = ib.reqMktData(contract, snapshot= True)

ib.sleep(5)
print()
print(market_data.bid)
'''

## consider Polygon.io API
"""
from polygon import RESTClient

ticker = 'SPY'
client = RESTClient(api_key="0KEpzIsVw9y0r7RSIpFDL5djXoEqBPRg")

for a in client.list_aggs(ticker=ticker, multiplier=1, timespan="day", from_="2025-01-01", to="2025-01-07", limit=50000):
    print()
    print(a)
"""

'''
# Get Last Quote
quote = client.get_last_trade(ticker=ticker)
print(quote)
'''

## testing binance REST API
'''
import requests

def get_binance_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    p = float(data['price'])
    return p 

price = get_binance_price("BTCUSDT")
print(f"Current BTC price: {price} USD")
'''

## Testing finnhub API

import requests
import time

# Replace with your Finnhub API key

# historical data -> access with paid sub
'''
API_KEY = 'cvbgdl9r01qob7udfm1gcvbgdl9r01qob7udfm20'

def get_historical_data(symbol, resolution, start_date, end_date):
    # Convert dates to UNIX timestamps
    from_timestamp = int(time.mktime(time.strptime(start_date, '%Y-%m-%d')))
    to_timestamp = int(time.mktime(time.strptime(end_date, '%Y-%m-%d')))

    url = 'https://finnhub.io/api/v1/stock/candle'
    params = {
        'symbol': symbol,
        'resolution': resolution,  # 1, 5, 15, 30, 60, D, W, M
        'from': from_timestamp,
        'to': to_timestamp,
        'token': API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get('s') != 'ok':
        print("Error fetching data:", data)
        return None

    return data

AAPL = get_historical_data('AAPL', resolution='D',start_date='2023-01-01', end_date='2023-12-31')
print(AAPL)'''

# live quote
import finnhub
import Indicators as I 

finnhub_client = finnhub.Client(api_key="cvbgdl9r01qob7udfm1gcvbgdl9r01qob7udfm20")
data = finnhub_client.quote('SPY')
curr = data['c']
delta = data['d']
deltapct = data['dp']
dayhigh = data['h']
daylow = data['l']
open = data['o']
prevclose = data['pc']
unixtime = data['t']

corr = I.equity_corr('NVDA',"AAPL",1260) # 5y

print(curr)