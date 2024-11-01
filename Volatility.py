from alpaca.data.requests import StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient
from py_vollib.black_scholes.implied_volatility import implied_volatility
from alpaca.data.timeframe import TimeFrame
from dateutil import parser
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
import datetime
from stockControl import getOptionsPrice
load_dotenv()

Alpaca_API_KEY = os.getenv("Alpaca_API_KEY")
Alpaca_SECRET_KEY = os.getenv("Alpaca_SECRET_KEY")

historical_client = StockHistoricalDataClient(Alpaca_API_KEY, Alpaca_SECRET_KEY)

def get_implied_volatility(stock_price, option_symbol, option_type="c"):
    """
    Calculate the implied volatility for a given option.
    """
    option_data = getOptionsPrice(option_symbol)  # Ensure this returns necessary data

    # Use mid price as the option price
    option_price = float(option_data["close_price"])

    strike = float(option_data["strike_price"])
    expiration = parser.parse(option_data["expiration_date"])
    today = datetime.datetime.now()

    # Time to expiration in years
    T = (expiration - today).days / 365.25
    if T <= 0:
        raise ValueError("Option has expired.")

    # Assume a risk-free rate (e.g., 1%)
    r = 0.01

    # Calculate implied volatility
    try:
        iv = implied_volatility(option_price, stock_price, strike, T, r, option_type)
        return iv
    except Exception as e:
        print(f"Error calculating implied volatility: {e}")
        return None


def get_historical_volatility(symbol, window):
    end_date = pd.Timestamp.today(tz="America/New_York")
    #subtract 1 day to get the last trading day
    end_date = end_date - pd.Timedelta(days=1)
    start_date = end_date - pd.Timedelta(days=window * 1.5)  # Approximation to get enough trading days

    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=start_date.isoformat(),
        end=end_date.isoformat()
    )

    bars = historical_client.get_stock_bars(request_params)

    # Convert to DataFrame
    df = bars.df.loc[symbol]
    df = df.sort_index()

    # Ensure we have enough data
    if len(df) < window:
        raise ValueError(f"Not enough data to calculate {window}-day volatility.")

    # Use the last 'window' days
    df = df.tail(window)

    # Calculate logarithmic returns
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df = df.dropna()

    # Calculate standard deviation of returns
    daily_std = df["log_return"].std()

    # Annualize the volatility
    historical_volatility = daily_std * np.sqrt(252)

    return historical_volatility


