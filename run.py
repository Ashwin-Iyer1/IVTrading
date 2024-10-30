from Volatility import get_historical_volatility
from Script import getOptions, getOptionBreakeven, initAcc, getAffordableStocks, buyAsset
import datetime
import random

def main():
    initAcc()
    possibleStocks = getAffordableStocks(10000)
    date1Month = (datetime.datetime.now() + datetime.timedelta(days=30)).date()
    ListofOptions = []

    for stock in possibleStocks:
        StockPrice = stock[1]
        for i in (getOptions(stock[0], date1Month)['option_contracts']):
            pct = getOptionBreakeven(i['strike_price'], i['close_price'], StockPrice)
            if(pct > 0.04 and pct < 0.075):
                ListofOptions.append([i['underlying_symbol'], i['symbol'], pct])
    #use a dictionary to store the stock name as the key and the list of options as the value
    #use the stock name as the key to get the list of options

    dictofOptions = {}
    buying_list = []
    for option in ListofOptions:
        if option[0] not in dictofOptions:
            dictofOptions[option[0]] = []
        dictofOptions[option[0]].append(option[1])
    for stock in dictofOptions:
        histIV = get_historical_volatility(stock, 252)
        impIV = get_historical_volatility(stock, 5)
        if((impIV - histIV) / histIV < -0.3):
            buying_list.append(dictofOptions[stock][0])
    random.shuffle(buying_list)
    print("Buying option: " + buying_list[0])
    buyAsset(buying_list[0], 1)






main()