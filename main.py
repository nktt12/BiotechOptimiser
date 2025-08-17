import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Test with a few major pharma companies first
pharma_tickers = ['PFE', 'JNJ', 'MRK', 'ABBV', 'BMY']

# Download stock data to make sure everything works
for ticker in pharma_tickers:
    stock = yf.download(ticker, start='2020-01-01', end='2024-12-31')
    print(f"{ticker}: {len(stock)} trading days downloaded")

def load_orange_book_data():
    """Load the three Orange Book data files"""
    
    # Load products data
    products = pd.read_csv('data/products.txt', sep='~', encoding='latin-1')
    
    # Load patent data  
    patents = pd.read_csv('data/patent.txt', sep='~', encoding='latin-1')
    
    # Load exclusivity data
    exclusivity = pd.read_csv('data/exclusivity.txt', sep='~', encoding='latin-1')
    
    return products, patents, exclusivity

#Test data loading
if __name__ == "__main__":
    products, patents, exclusivity = load_orange_book_data()
    
    print(f"Products: {len(products)} rows")
    print(f"Patents: {len(patents)} rows") 
    print(f"Exclusivity: {len(exclusivity)} rows")