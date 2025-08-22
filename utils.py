# utils.py - Enhanced with new drug launch support
"""Utility functions for enhanced patent cliff optimizer with new drug launch tracking"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import feedparser
from transformers import pipeline
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

def get_unique_tickers(target_drugs: Dict, new_launches: Dict = None) -> List[str]:
    """Extract unique ticker symbols from target drugs and optionally new launches"""
    tickers = list(set([drug_info['ticker'] for drug_info in target_drugs.values()]))
    
    if new_launches:
        launch_tickers = list(set([drug_info['ticker'] for drug_info in new_launches.values()]))
        tickers = list(set(tickers + launch_tickers))
    
    return tickers
def sentiment_analysis(name:str, ticker: str) -> Tuple[float, int]:
    pipe = pipeline("text-classification", model="ProsusAI/finbert")
    rss_url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
    feed = feedparser.parse(rss_url)

    total_score = 0
    number_of_articles = 0
    for i,entry in enumerate(feed.entries):
        if name.lower() not in entry.summary.lower():
            continue
        sentiment = pipe(entry.summary)[0]
        if sentiment['label'] == 'positive':
            total_score += sentiment['score']
            number_of_articles += 1
        elif sentiment['label'] == 'negative':
            total_score -= sentiment['score']
            number_of_articles += 1
    return total_score/number_of_articles if number_of_articles > 0 else 0



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

def get_drug_launch_events(new_launches: Dict, start_date: str, end_date: str) -> List[Dict]:
    """
    Get chronologically ordered list of new drug launch events within date range
    """
    launch_events = []
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    
    for drug_name, drug_info in new_launches.items():
        try:
            launch_date = pd.Timestamp(drug_info['launch_date'])
            
            # Only include launches within the backtest period
            if start_ts <= launch_date <= end_ts:
                launch_events.append({
                    'drug_name': drug_name,
                    'launch_date': launch_date,
                    'company': drug_info['company'],
                    'ticker': drug_info['ticker'],
                    'revenue_billions': drug_info['revenue_billions'],
                    'peak_sales_estimate': drug_info['peak_sales_estimate'],
                    'indication': drug_info.get('indication', 'Unknown'),
                    'status': drug_info.get('status', 'standard')
                })
        except:
            continue
    
    # Sort by launch date
    launch_events.sort(key=lambda x: x['launch_date'])
    
    return launch_events

def calculate_launch_success_score(drug_info: Dict, current_date: datetime = None) -> float:
    """
    Calculate a success score for a new drug launch based on various factors
    Score ranges from 0.0 to 2.0, with 1.0 being average
    """
    if current_date is None:
        current_date = datetime.now()
    
    score = 1.0  # Base score
    
    try:
        # Revenue achievement factor
        current_revenue = drug_info.get('revenue_billions', 0)
        peak_estimate = drug_info.get('peak_sales_estimate', 5.0)
        
        if peak_estimate > 0:
            revenue_achievement = min(1.5, current_revenue / peak_estimate)
            score *= (0.5 + revenue_achievement)  # Scale between 0.5 and 2.0
        
        # Status factor
        status_multipliers = {
            'blockbuster': 1.4,
            'growing_blockbuster': 1.3,
            'expanding_blockbuster': 1.35,
            'oncology_blockbuster': 1.2,
            'pandemic_blockbuster': 0.9  # Lower due to sustainability concerns
        }
        status_mult = status_multipliers.get(drug_info.get('status', 'standard'), 1.0)
        score *= status_mult
        
        # Time since launch factor
        launch_date = pd.Timestamp(drug_info['launch_date'])
        current_ts = pd.Timestamp(current_date)
        months_since_launch = (current_ts - launch_date).days / 30.44
        
        # Optimal performance window is 6-24 months post-launch
        if months_since_launch < 6:
            time_factor = 0.7 + (months_since_launch / 6) * 0.3  # Ramp up
        elif months_since_launch <= 24:
            time_factor = 1.0  # Peak performance window
        else:
            # Gradual decline after 2 years
            time_factor = max(0.6, 1.0 - ((months_since_launch - 24) / 36) * 0.4)
        
        score *= time_factor
        
        # Revenue size factor - larger revenues get slight boost
        if current_revenue >= 10.0:
            score *= 1.1
        elif current_revenue >= 5.0:
            score *= 1.05
        
    except Exception as e:
        # If any calculation fails, return neutral score
        score = 1.0
    
    return max(0.1, min(2.0, score))  # Clamp between 0.1 and 2.0

def analyze_launch_portfolio_impact(launch_tracking: Dict, stock_data: pd.DataFrame) -> Dict:
    """
    Analyze the portfolio impact of new drug launches
    """
    if not launch_tracking:
        return {}
    
    analysis = {
        'total_launches_tracked': len(launch_tracking),
        'successful_launches': 0,
        'average_weight': 0,
        'total_contribution': 0,
        'launch_details': []
    }
    
    total_weights = []
    
    for launch_name, tracking_data in launch_tracking.items():
        weights = [w[1] for w in tracking_data['weights_history']]
        avg_weight = np.mean(weights) if weights else 0
        max_weight = max(weights) if weights else 0
        
        total_weights.extend(weights)
        
        # Consider successful if average weight > 1%
        if avg_weight > 0.01:
            analysis['successful_launches'] += 1
        
        analysis['launch_details'].append({
            'name': launch_name,
            'first_inclusion': tracking_data['first_inclusion_date'],
            'average_weight': avg_weight,
            'peak_weight': max_weight,
            'weight_trend': 'increasing' if len(weights) > 1 and weights[-1] > weights[0] else 'stable'
        })
    
    if total_weights:
        analysis['average_weight'] = np.mean(total_weights)
        analysis['total_contribution'] = sum(total_weights)
    
    # Sort launch details by impact
    analysis['launch_details'].sort(key=lambda x: x['average_weight'], reverse=True)
    
    return analysis

def get_launch_calendar(new_launches: Dict, year: int = None) -> pd.DataFrame:
    """
    Create a calendar view of drug launches for a specific year or all years
    """
    launch_data = []
    
    for drug_name, drug_info in new_launches.items():
        try:
            launch_date = pd.Timestamp(drug_info['launch_date'])
            
            if year is None or launch_date.year == year:
                launch_data.append({
                    'Drug': drug_name,
                    'Company': drug_info['company'],
                    'Ticker': drug_info['ticker'],
                    'Launch Date': launch_date,
                    'Month': launch_date.strftime('%B'),
                    'Year': launch_date.year,
                    'Revenue ($B)': drug_info['revenue_billions'],
                    'Peak Est ($B)': drug_info['peak_sales_estimate'],
                    'Indication': drug_info.get('indication', 'Unknown'),
                    'Status': drug_info.get('status', 'standard')
                })
        except:
            continue
    
    if not launch_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(launch_data)
    df = df.sort_values('Launch Date')
    
    return df

def calculate_portfolio_attribution(weight_history: List[Dict], stock_data: pd.DataFrame, 
                                  new_launches: Dict) -> Dict:
    """
    Calculate performance attribution between existing drugs and new launches
    """
    if not weight_history or stock_data.empty:
        return {}
    
    # Get new launch tickers
    new_launch_tickers = set([info['ticker'] for info in new_launches.values()])
    
    attribution = {
        'new_launch_contribution': 0,
        'existing_drug_contribution': 0,
        'total_periods': len(weight_history),
        'new_launch_periods': 0
    }
    
    for i in range(1, len(weight_history)):
        current_weights = weight_history[i]['weights']
        prev_date = weight_history[i-1]['date'] 
        curr_date = weight_history[i]['date']
        
        # Calculate period return for each ticker
        for ticker, weight in current_weights.items():
            if weight > 0:
                try:
                    # Get stock return for this period
                    if len(stock_data.columns.names) > 1:
                        if ('Close', ticker) in stock_data.columns:
                            prev_price = stock_data[('Close', ticker)].asof(prev_date)
                            curr_price = stock_data[('Close', ticker)].asof(curr_date)
                        else:
                            continue
                    else:
                        if ticker in stock_data.columns:
                            prev_price = stock_data[ticker].asof(prev_date)
                            curr_price = stock_data[ticker].asof(curr_date)
                        else:
                            continue
                    
                    if pd.notna(prev_price) and pd.notna(curr_price) and prev_price > 0:
                        stock_return = (curr_price - prev_price) / prev_price
                        contribution = weight * stock_return
                        
                        if ticker in new_launch_tickers:
                            attribution['new_launch_contribution'] += contribution
                            if contribution != 0:
                                attribution['new_launch_periods'] += 1
                        else:
                            attribution['existing_drug_contribution'] += contribution
                            
                except:
                    continue
    
    return attribution