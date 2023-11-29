from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf
import scipy.stats

# Calculate date range
_current_date = datetime.now()
_one_year_before_now = _current_date - timedelta(days=365)


def ticker_info(tickers_series: pd.Series) -> yf.tickers.Tickers:
    """
    Get Ticker objects for a series of tickers.

    :param tickers_series: A pandas Series containing equity tickers.
    :return: Tickers object containing ticker information.
    """
    sorted_tickers_list = [ticker.replace("BRKB", "BRK-B") for ticker in tickers_series.to_list()]
    return yf.Tickers(sorted_tickers_list)


def price_history(tickers_series: pd.Series, interval: str) -> pd.DataFrame:
    """
    Retrieve historical closing prices for a series of tickers within a specified time interval.

    :param tickers_series: A pandas Series of tickers for which to retrieve historical data.
    :param interval: The time interval for the historical data. Allowed values are "1m", "2m", "5m", "15m",
                     "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo".
    :return: A DataFrame containing historical closing prices for the specified tickers.
    :raise ValueError: If the provided interval is not in the list of allowed intervals.
    """
    # Validate interval
    allowed_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
    if interval not in allowed_intervals:
        raise ValueError(f"Invalid interval '{interval}'. Allowed intervals are: {', '.join(allowed_intervals)}")

    # Get ticker information
    tickers = ticker_info(tickers_series)

    # Retrieve historical data
    historical_stock_price = tickers.history(
        interval=interval,
        period="ytd"
    )

    # Extract closing prices
    closing_prices = historical_stock_price.loc[:, ('Close', slice(None))]

    return closing_prices
