from Volatility import get_historical_volatility
from stockControl import getOptions, getOptionBreakeven, initAcc, getAffordableStocks, buyAsset
import datetime
import random

def main():
    initAcc()
    possibleStocks = getAffordableStocks(10000) #Get all stocks that are less than $100 (option contraacts are 100x of a stock)
    date1Month = (datetime.datetime.now() + datetime.timedelta(days=30)).date() #Get the date 1 month from now
    ListofOptions = []

    for stock in possibleStocks:
        StockPrice = stock[1] #Get the stock price
        for i in (getOptions(stock[0], date1Month)['option_contracts']): #Get all options for the stock in 1 month or more
            pct = getOptionBreakeven(i['strike_price'], i['close_price'], StockPrice) #Get the breakeven percentage
            if(pct > 0.04 and pct < 0.075): #If the breakeven percentage is between 4% and 7.5%
                ListofOptions.append([i['underlying_symbol'], i['symbol'], pct]) #Add the stock name, option symbol, and breakeven percentage to the list

    dictofOptions = {} #Dictionary to store the options so we only pull the stock price once per stock name
    buying_list = []
    for option in ListofOptions: 
        if option[0] not in dictofOptions:
            dictofOptions[option[0]] = [] #Add the stock name to the dictionary
        dictofOptions[option[0]].append(option[1]) #Add the option symbol to the stock name in the dictionary
    for stock in dictofOptions: 
        histIV = get_historical_volatility(stock, 252) #Get the historical volatility of the stock
        impIV = get_historical_volatility(stock, 5) #Get the implied volatility of the stock (past 5 days of volatility)
        if((impIV - histIV) / histIV < -0.3): #If the implied volatility is 30% less than the historical volatility
            buying_list.append(dictofOptions[stock][0]) 
    random.shuffle(buying_list)
    print("Buying option: " + buying_list[0])
    buyAsset(buying_list[0], 1) #Buy the option






main()