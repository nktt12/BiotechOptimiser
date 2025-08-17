import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Test with a few major pharma companies first
pharma_tickers = ['PFE', 'JNJ', 'MRK', 'ABBV', 'BMY']

# Download stock data to make sure everything works
for ticker in pharma_tickers:
    stock = yf.download(ticker, start='2020-01-01', end='2024-12-31')
    print(f"{ticker}: {len(stock)} trading days downloaded")