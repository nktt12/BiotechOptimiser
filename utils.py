# utils.py
"""Utility functions for patent cliff optimizer"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

def load_orange_book_data(data_paths: Dict[str, str]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the three Orange Book data files"""
    
    # Load products data
    products = pd.read_csv(data_paths['products'], sep='~', encoding='latin-1')
    
    # Load patent data  
    patents = pd.read_csv(data_paths['patents'], sep='~', encoding='latin-1')
    
    # Load exclusivity data
    exclusivity = pd.read_csv(data_paths['exclusivity'], sep='~', encoding='latin-1')
    
    return products, patents, exclusivity

def get_unique_tickers(target_drugs: Dict) -> List[str]:
    """Extract unique ticker symbols from target drugs dictionary"""
    return list(set([drug_info['ticker'] for drug_info in target_drugs.values()]))

def download_stock_data(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """Download stock data for multiple tickers"""
    try:
        stock_data = yf.download(tickers, start=start_date, end=end_date, progress=False)
        print(f"Stock data downloaded successfully for {len(tickers)} tickers!")
        return stock_data
    except Exception as e:
        print(f"Error downloading stock data: {e}")
        return pd.DataFrame()

def get_latest_revenues(tickers: List[str]) -> Dict[str, Optional[float]]:
    """Fetch latest total revenues for companies"""
    revenues = {}
    
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            financials = t.financials
            
            if "Total Revenue" in financials.index:
                latest_revenue = financials.loc["Total Revenue"].iloc[0]
                revenues[ticker] = latest_revenue / 1e9  # convert to billions
            else:
                revenues[ticker] = None
                
        except Exception as e:
            print(f"Could not fetch revenue for {ticker}: {e}")
            revenues[ticker] = None
            
    return revenues

def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily returns from price data"""
    return prices.pct_change().dropna()

def calculate_volatility(returns: pd.DataFrame, window: int = 252) -> pd.Series:
    """Calculate annualized volatility"""
    return returns.rolling(window=window).std() * np.sqrt(252)
    #only 252 days in trading year

def get_trading_dates(start_date: str, end_date: str, frequency: str = 'quarterly') -> List[datetime]:
    """Generate rebalancing dates based on frequency"""
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    dates = []
    current = start
    
    if frequency == 'monthly':
        while current <= end:
            dates.append(current)
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
                
    elif frequency == 'quarterly':
        while current <= end:
            dates.append(current)
            # Move to next quarter
            if current.month <= 3:
                current = current.replace(month=6)
            elif current.month <= 6:
                current = current.replace(month=9)
            elif current.month <= 9:
                current = current.replace(month=12)
            else:
                current = current.replace(year=current.year + 1, month=3)
                
    elif frequency == 'annually':
        while current <= end:
            dates.append(current)
            current = current.replace(year=current.year + 1)
    
    return dates

def apply_position_limits(weights: pd.Series, min_weight: float = 0, max_weight: float = 0.90) -> pd.Series:
    """Apply minimum and maximum position limits to portfolio weights"""
    
    # Apply limits
    weights = weights.clip(lower=min_weight, upper=max_weight)
    
    # Renormalize to sum to 1
    if weights.sum() > 0:
        weights = weights / weights.sum()
    
    return weights

def calculate_transaction_costs(old_weights: pd.Series, new_weights: pd.Series, 
                              cost_rate: float = 0.001) -> float:
    """Calculate transaction costs based on portfolio turnover"""
    
    # Align indices
    all_tickers = old_weights.index.union(new_weights.index)
    old_weights = old_weights.reindex(all_tickers, fill_value=0)
    new_weights = new_weights.reindex(all_tickers, fill_value=0)
    
    # Calculate turnover (sum of absolute changes)
    turnover = np.abs(new_weights - old_weights).sum()
    
    return turnover * cost_rate

def format_performance_metrics(metrics: Dict) -> str:
    """Format performance metrics for display"""
    
    output = []
    output.append("=" * 50)
    output.append("PERFORMANCE METRICS")
    output.append("=" * 50)
    
    for key, value in metrics.items():
        if isinstance(value, float):
            if 'return' in key.lower() or 'ratio' in key.lower():
                output.append(f"{key:.<30} {value:.4f}")
            elif 'volatility' in key.lower() or 'drawdown' in key.lower():
                output.append(f"{key:.<30} {value:.2%}")
            else:
                output.append(f"{key:.<30} {value:.2f}")
        else:
            output.append(f"{key:.<30} {value}")
    
    return "\n".join(output)

def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, returning default if denominator is zero"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default