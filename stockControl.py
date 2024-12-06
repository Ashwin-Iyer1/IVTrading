from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import requests
import os
from dotenv import load_dotenv
load_dotenv()

Alpaca_API_KEY = os.getenv("Alpaca_API_KEY")
Alpaca_SECRET_KEY = os.getenv("Alpaca_SECRET_KEY")


headers = {
    "APCA-API-KEY-ID": Alpaca_API_KEY,
    "APCA-API-SECRET-KEY": Alpaca_SECRET_KEY
}

trading_client = TradingClient(Alpaca_API_KEY, Alpaca_SECRET_KEY, paper=True)

def initAcc():
    global account
    account = trading_client.get_account()

def get_liquid():
    return account.buying_power


def margin():
    balance_change = float(account.equity) - float(account.last_equity)
    print(f'Today\'s portfolio balance change: ${balance_change}')


def sellAsset(symbol, qty):
    market_sell_data = MarketOrderRequest(
                        symbol=symbol,
                        qty=qty,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.GTC
                        )
    submit(market_sell_data)

def buyAsset(symbol, qty):
    market_order_data = MarketOrderRequest(
                        symbol=symbol,
                        qty=qty,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.DAY
                        )
    submit(market_order_data)

def getStockPrice(symbol):
    url = f'https://data.alpaca.markets/v2/stocks/{symbol}/trades/latest'
    response = requests.get(url, headers=headers)
    return response.json()['trade']['p']


def getActiveStocks():
    url = 'https://data.alpaca.markets/v1beta1/screener/stocks/most-actives?by=volume&top=25'
    response = requests.get(url, headers=headers)
    return response.json()

def getOptionsPrice(symbol):
    url = f'https://paper-api.alpaca.markets/v2/options/contracts/{symbol}'

    response = requests.get(url, headers=headers)
    return response.json()

def getOptions(symbol, expiration_date):
    url = f'https://paper-api.alpaca.markets/v2/options/contracts?underlying_symbols={symbol}&status=active&expiration_date_gte={expiration_date}&type=call'
    response = requests.get(url, headers=headers)
    return response.json()

def submit(type):
    trading_client.submit_order(order_data=type)

def getallassets():
    assets = trading_client.get_all_assets()
    return assets

    

def buy_multiple_eql_amts(stocks, amt, Platform):
    listofbuys = []
    listofPrices = []
    counter = 0
    stockPrices = []
    for stock in stocks:
        stockprice = getStockPrice(stock)
        stockPrices.append(stockprice)
        listofPrices.append(float(amt) / stockprice)
    print(listofPrices)
    for stock in stocks:
        try:
            buyAsset(stock, round(listofPrices[counter], 1))
            #print only up to 1 decimal place for amt / stockprice
            listofbuys.append(f'{listofPrices[counter]:.2f} shares of {stock} at {stockPrices[counter]}')
            counter += 1
        except Exception as e:
            if "asset not found" in str(e) or "is not active" in str(e):
                print(f"Skipping {stock} due to error: {e}")
                continue
            else:
                raise e
    print('Using ' + Platform + " bought " + str(listofbuys))

    return listofbuys


def getAffordableStocks(amt):
    global listOfAffordableStocks
    listOfAffordableStocks = []
    stocks = getActiveStocks()['most_actives']
    for stock in stocks:
        stockPrice = getStockPrice(stock['symbol'])
        if stockPrice*100 < amt:
            listOfAffordableStocks.append([stock['symbol'], stockPrice])
    return listOfAffordableStocks

def getOptionBreakeven(strike_price, close_price, stock_price):
    if(strike_price == None or close_price == None or stock_price == None):
        return -1
    jumpAmt = (float(strike_price) + float(close_price) - float(stock_price)) / float(stock_price) #pct change for stock price to reach breakeven (little wrong)
    return jumpAmt