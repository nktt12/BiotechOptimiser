# backtest_engine.py
"""
Patent Cliff Strategy Backtesting Engine
Tests how the strategy would have performed from 2020-2024 using actual patent expiry data
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

from config import TARGET_DRUGS, BACKTEST_CONFIG, RISK_PARAMETERS
from utils import (get_trading_dates, calculate_transaction_costs, apply_position_limits,
                   safe_divide, get_latest_revenues)

class PatentCliffBacktester:
    """
    Backtests the patent cliff avoidance strategy
    """
    
    def __init__(self, start_date='2020-01-01', end_date='2024-12-31'):
        self.start_date = start_date
        self.end_date = end_date
        self.rebalance_dates = None
        self.stock_data = None
        self.benchmark_data = None
        self.portfolio_history = []
        self.performance_metrics = {}
        
    def load_historical_data(self):
        """Load stock price data, benchmark, and your 2019 Orange Book snapshot"""
        print(f"Loading data from {self.start_date} to {self.end_date}...")
        
        # Load your 2019 Orange Book snapshot
        print("Loading 2019 Orange Book snapshot...")
        try:
            # Update these paths to point to your 2019 Orange Book files
            ORANGE_BOOK_2019_PATHS = {
                'products': 'C:\Users\Nikhi\Desktop\BiotechOptimiser\BiotechOptimiser\historical_patent_data\2019-09-01\products.txt',  # Update this path
                'patents': 'C:\Users\Nikhi\Desktop\BiotechOptimiser\BiotechOptimiser\historical_patent_data\2019-09-01\patent.txt',     # Update this path
                'exclusivity': 'C:\Users\Nikhi\Desktop\BiotechOptimiser\BiotechOptimiser\historical_patent_data\2019-09-01\exclusivity.txt'  # Update this path
            }
            
            # Load the 2019 Orange Book data
            self.orange_book_products = pd.read_csv(
                ORANGE_BOOK_2019_PATHS['products'], 
                sep='~', 
                encoding='latin-1'
            )
            self.orange_book_patents = pd.read_csv(
                ORANGE_BOOK_2019_PATHS['patents'], 
                sep='~', 
                encoding='latin-1'
            )
            self.orange_book_exclusivity = pd.read_csv(
                ORANGE_BOOK_2019_PATHS['exclusivity'], 
                sep='~', 
                encoding='latin-1'
            )
            
            print(f"✓ Loaded Orange Book data:")
            print(f"  - {len(self.orange_book_products)} products")
            print(f"  - {len(self.orange_book_patents)} patents") 
            print(f"  - {len(self.orange_book_exclusivity)} exclusivity records")
            
        except Exception as e:
            print(f"✗ Error loading Orange Book data: {e}")
            print("Please update the file paths in ORANGE_BOOK_2019_PATHS")
            return False
        
        # Get unique tickers from target drugs
        tickers = list(set([drug['ticker'] for drug in TARGET_DRUGS.values()]))
        
        # Download stock data
        try:
            self.stock_data = yf.download(tickers, start=self.start_date, end=self.end_date)
            print(f"✓ Stock data loaded for {len(tickers)} tickers")
        except Exception as e:
            print(f"✗ Error loading stock data: {e}")
            return False
            
        # Download benchmark data (SPY)
        try:
            self.benchmark_data = yf.download('SPY', start=self.start_date, end=self.end_date)['Close']
            print("✓ Benchmark data loaded")
        except Exception as e:
            print(f"✗ Error loading benchmark: {e}")
            return False
            
        return True
    
    def get_patent_cliff_weights(self, current_date: datetime) -> pd.Series:
        """
        Calculate portfolio weights based on patent cliff risk at a specific date
        This is where you'd integrate your actual 2020-2024 patent expiry data
        """
        
        weights = {}
        
        for drug_name, drug_info in TARGET_DRUGS.items():
            ticker = drug_info['ticker']
            
            # Get actual patent expiry from your 2019 Orange Book snapshot
            patent_expiry = self.get_patent_expiry_from_orange_book(drug_name, current_date)
            
            if patent_expiry is None:
                continue
                
            # Calculate years to expiry
            days_to_expiry = (patent_expiry - current_date).days
            years_to_expiry = days_to_expiry / 365.25
            
            # Skip if patent has already expired or expires very soon
            if years_to_expiry < RISK_PARAMETERS['min_time_to_cliff']:
                continue
                
            # Calculate risk-adjusted weight
            weight = self.calculate_risk_weight(
                ticker=ticker,
                drug_revenue=drug_info['revenue_billions'],
                years_to_expiry=years_to_expiry,
                current_date=current_date
            )
            
            if ticker in weights:
                weights[ticker] += weight
            else:
                weights[ticker] = weight
        
        # Convert to Series and normalize
        weights_series = pd.Series(weights)
        if len(weights_series) > 0 and weights_series.sum() > 0:
            weights_series = weights_series / weights_series.sum()
            # Apply position limits
            weights_series = apply_position_limits(
                weights_series, 
                BACKTEST_CONFIG['min_weight'], 
                BACKTEST_CONFIG['max_weight']
            )
        
        return weights_series
    
    def get_patent_expiry_from_orange_book(self, drug_name: str, current_date: datetime) -> datetime:
        """
        Get actual patent expiry from your 2019 Orange Book snapshot
        """
        if not hasattr(self, 'orange_book_products') or not hasattr(self, 'orange_book_patents'):
            return None
            
        # Find the drug in products (case-insensitive search)
        drug_products = self.orange_book_products[
            self.orange_book_products['Trade_Name'].str.upper().str.contains(
                drug_name.upper(), na=False
            )
        ]
        
        if drug_products.empty:
            return None
        
        # Get NDA numbers for this drug
        nda_numbers = drug_products['Appl_No'].unique()
        
        # Find all patents for these NDAs
        drug_patents = self.orange_book_patents[
            self.orange_book_patents['Appl_No'].isin(nda_numbers)
        ].copy()
        
        if drug_patents.empty:
            return None
            
        # Convert patent expiry dates
        drug_patents['Patent_Expire_Date_Text'] = pd.to_datetime(
            drug_patents['Patent_Expire_Date_Text'], errors='coerce'
        )
        
        # Filter out invalid dates and patents that expired before current_date
        valid_patents = drug_patents[
            (drug_patents['Patent_Expire_Date_Text'].notna()) & 
            (drug_patents['Patent_Expire_Date_Text'] > current_date)
        ]
        
        if valid_patents.empty:
            return None
            
        # Return the LATEST expiry date (last patent to expire)
        latest_expiry = valid_patents['Patent_Expire_Date_Text'].max()
        return latest_expiry
    
    def calculate_risk_weight(self, ticker: str, drug_revenue: float, 
                            years_to_expiry: float, current_date: datetime) -> float:
        """Calculate risk-adjusted weight for a company/drug"""
        
        # Time decay factor - reduce weight as expiry approaches
        if years_to_expiry <= 1:
            time_factor = 0.1  # Very low weight if expiring within 1 year
        elif years_to_expiry <= 2:
            time_factor = 0.3  # Low weight if expiring within 2 years
        elif years_to_expiry <= 3:
            time_factor = 0.6  # Medium weight if expiring within 3 years
        else:
            time_factor = 1.0  # Full weight if expiring in 3+ years
        
        # Revenue size factor - larger revenue drugs get higher base weight
        revenue_factor = min(1.0, drug_revenue / 5.0)  # Scale by $5B revenue
        
        # Combined weight
        weight = time_factor * revenue_factor
        
        return max(0.01, weight)  # Minimum weight to avoid zero positions
    
    def rebalance_portfolio(self, rebalance_date: datetime, 
                          current_weights: pd.Series) -> Tuple[pd.Series, float]:
        """Rebalance portfolio to target weights"""
        
        # Get target weights for this date
        target_weights = self.get_patent_cliff_weights(rebalance_date)
        
        # Calculate transaction costs
        transaction_cost = calculate_transaction_costs(
            current_weights, 
            target_weights, 
            BACKTEST_CONFIG['transaction_cost']
        )
        
        return target_weights, transaction_cost
    
    def run_backtest(self) -> Dict:
        """Run the full backtest simulation"""
        
        print("Starting backtest simulation...")
        
        # Generate rebalancing dates
        self.rebalance_dates = get_trading_dates(
            self.start_date, 
            self.end_date, 
            BACKTEST_CONFIG['rebalance_frequency']
        )
        print(f"✓ Generated {len(self.rebalance_dates)} rebalancing dates")
        
        # Initialize portfolio
        initial_capital = BACKTEST_CONFIG['initial_capital']
        portfolio_value = initial_capital
        current_weights = pd.Series(dtype=float)
        total_transaction_costs = 0
        
        # Get all trading days
        trading_days = self.stock_data.index
        
        # Track performance
        daily_returns = []
        portfolio_values = []
        benchmark_values = []
        weight_history = []
        
        # Initialize benchmark
        initial_benchmark = self.benchmark_data.iloc[0]
        
        print("Running daily simulation...")
        
        for i, date in enumerate(trading_days):
            
            # Check if this is a rebalancing date
            is_rebalance_date = any(abs((date.date() - rd.date()).days) < 3 
                                  for rd in self.rebalance_dates)
            
            if is_rebalance_date or i == 0:
                # Rebalance portfolio
                new_weights, txn_cost = self.rebalance_portfolio(date, current_weights)
                current_weights = new_weights
                total_transaction_costs += txn_cost * portfolio_value
                
                weight_history.append({
                    'date': date,
                    'weights': current_weights.copy(),
                    'transaction_cost': txn_cost
                })
                
                if i % 50 == 0:  # Progress update
                    print(f"  Processed {i}/{len(trading_days)} days...")
            
            # Calculate portfolio return for this day
            if len(current_weights) > 0 and i > 0:
                # Get returns for stocks in portfolio
                portfolio_return = 0
                for ticker, weight in current_weights.items():
                    if ('Close', ticker) in self.stock_data.columns:
                        prev_price = self.stock_data[('Close', ticker)].iloc[i-1]
                        curr_price = self.stock_data[('Close', ticker)].iloc[i]
                        if pd.notna(prev_price) and pd.notna(curr_price) and prev_price != 0:
                            stock_return = (curr_price - prev_price) / prev_price
                            portfolio_return += weight * stock_return
                
                # Update portfolio value
                portfolio_value *= (1 + portfolio_return)
                daily_returns.append(portfolio_return)
            else:
                daily_returns.append(0)
            
            portfolio_values.append(portfolio_value)
            
            # Track benchmark
            benchmark_value = (self.benchmark_data.iloc[i] / initial_benchmark) * initial_capital
            benchmark_values.append(benchmark_value)
        
        # Store results
        self.portfolio_history = {
            'dates': trading_days,
            'portfolio_values': portfolio_values,
            'benchmark_values': benchmark_values,
            'daily_returns': daily_returns,
            'weight_history': weight_history,
            'total_transaction_costs': total_transaction_costs
        }
        
        print("✓ Backtest simulation complete!")
        
        # Calculate performance metrics
        self.calculate_performance_metrics()
        
        return self.portfolio_history
    
    def calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics"""
        
        portfolio_values = np.array(self.portfolio_history['portfolio_values'])
        benchmark_values = np.array(self.portfolio_history['benchmark_values'])
        daily_returns = np.array(self.portfolio_history['daily_returns'])
        
        # Basic returns
        total_portfolio_return = (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0]
        total_benchmark_return = (benchmark_values[-1] - benchmark_values[0]) / benchmark_values[0]
        
        # Annualized returns
        years = len(portfolio_values) / 252
        annual_portfolio_return = (1 + total_portfolio_return) ** (1/years) - 1
        annual_benchmark_return = (1 + total_benchmark_return) ** (1/years) - 1
        
        # Volatility
        portfolio_vol = np.std(daily_returns) * np.sqrt(252)
        benchmark_returns = np.diff(benchmark_values) / benchmark_values[:-1]
        benchmark_vol = np.std(benchmark_returns) * np.sqrt(252)
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        portfolio_sharpe = (annual_portfolio_return - risk_free_rate) / portfolio_vol
        benchmark_sharpe = (annual_benchmark_return - risk_free_rate) / benchmark_vol
        
        # Maximum drawdown
        portfolio_peak = np.maximum.accumulate(portfolio_values)
        portfolio_drawdown = (portfolio_values - portfolio_peak) / portfolio_peak
        max_drawdown = np.min(portfolio_drawdown)
        
        # Win rate
        win_rate = np.sum(np.array(daily_returns) > 0) / len(daily_returns)
        
        self.performance_metrics = {
            'Total Portfolio Return': f"{total_portfolio_return:.2%}",
            'Total Benchmark Return': f"{total_benchmark_return:.2%}",
            'Excess Return': f"{total_portfolio_return - total_benchmark_return:.2%}",
            'Annual Portfolio Return': f"{annual_portfolio_return:.2%}",
            'Annual Benchmark Return': f"{annual_benchmark_return:.2%}",
            'Portfolio Volatility': f"{portfolio_vol:.2%}",
            'Benchmark Volatility': f"{benchmark_vol:.2%}",
            'Portfolio Sharpe Ratio': f"{portfolio_sharpe:.3f}",
            'Benchmark Sharpe Ratio': f"{benchmark_sharpe:.3f}",
            'Maximum Drawdown': f"{max_drawdown:.2%}",
            'Win Rate': f"{win_rate:.2%}",
            'Total Transaction Costs': f"${self.portfolio_history['total_transaction_costs']:,.0f}",
            'Final Portfolio Value': f"${portfolio_values[-1]:,.0f}",
            'Final Benchmark Value': f"${benchmark_values[-1]:,.0f}"
        }
    
    def plot_results(self):
        """Create comprehensive visualization of backtest results"""
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        dates = self.portfolio_history['dates']
        portfolio_values = self.portfolio_history['portfolio_values']
        benchmark_values = self.portfolio_history['benchmark_values']
        
        # Plot 1: Portfolio vs Benchmark Performance
        ax1 = axes[0, 0]
        ax1.plot(dates, portfolio_values, label='Patent Cliff Strategy', linewidth=2)
        ax1.plot(dates, benchmark_values, label='S&P 500 Benchmark', linewidth=2)
        ax1.set_title('Portfolio Performance vs Benchmark')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Rolling Returns
        ax2 = axes[0, 1]
        portfolio_returns = np.array(self.portfolio_history['daily_returns'])
        rolling_returns = pd.Series(portfolio_returns).rolling(window=63).mean() * 252  # 3-month rolling annualized
        ax2.plot(dates[62:], rolling_returns[62:], label='3-Month Rolling Return')
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax2.set_title('Rolling Annualized Returns')
        ax2.set_ylabel('Return')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Drawdown
        ax3 = axes[1, 0]
        portfolio_peak = np.maximum.accumulate(portfolio_values)
        drawdown = (np.array(portfolio_values) - portfolio_peak) / portfolio_peak * 100
        ax3.fill_between(dates, drawdown, 0, alpha=0.3, color='red')
        ax3.plot(dates, drawdown, color='red')
        ax3.set_title('Portfolio Drawdown')
        ax3.set_ylabel('Drawdown (%)')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Weight Evolution
        ax4 = axes[1, 1]
        weight_dates = [w['date'] for w in self.portfolio_history['weight_history']]
        
        # Get top 5 most frequently held stocks
        all_tickers = set()
        for w in self.portfolio_history['weight_history']:
            all_tickers.update(w['weights'].index)
        
        for ticker in list(all_tickers)[:5]:  # Show top 5 for clarity
            weights = []
            for w in self.portfolio_history['weight_history']:
                weights.append(w['weights'].get(ticker, 0))
            ax4.plot(weight_dates, weights, label=ticker, marker='o', markersize=3)
        
        ax4.set_title('Portfolio Weights Over Time')
        ax4.set_ylabel('Weight (%)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def print_performance_summary(self):
        """Print detailed performance summary"""
        
        print("\n" + "="*60)
        print("PATENT CLIFF STRATEGY BACKTEST RESULTS")
        print("="*60)
        
        for metric, value in self.performance_metrics.items():
            print(f"{metric:<30} {value}")
        
        print("\n" + "="*60)
        print("REBALANCING SUMMARY")
        print("="*60)
        
        print(f"Rebalancing frequency: {BACKTEST_CONFIG['rebalance_frequency']}")
        print(f"Number of rebalances: {len(self.portfolio_history['weight_history'])}")
        print(f"Average transaction cost per rebalance: ${self.portfolio_history['total_transaction_costs']/len(self.portfolio_history['weight_history']):,.0f}")
        
        # Show some example rebalancing dates and weights
        print("\nSample Rebalancing Events:")
        for i in range(0, min(5, len(self.portfolio_history['weight_history'])), 1):
            rebalance = self.portfolio_history['weight_history'][i]
            print(f"\n{rebalance['date'].strftime('%Y-%m-%d')}:")
            top_weights = rebalance['weights'].nlargest(3)
            for ticker, weight in top_weights.items():
                print(f"  {ticker}: {weight:.1%}")

def main():
    """Main execution function"""
    
    print("Patent Cliff Strategy Backtester")
    print("="*50)
    
    # Initialize backtester
    backtester = PatentCliffBacktester(
        start_date=BACKTEST_CONFIG['start_date'],
        end_date=BACKTEST_CONFIG['end_date']
    )
    
    # Load data
    if not backtester.load_historical_data():
        print("Failed to load data. Exiting...")
        return None
    
    # Run backtest
    results = backtester.run_backtest()
    
    # Display results
    backtester.print_performance_summary()
    backtester.plot_results()
    
    return backtester

if __name__ == "__main__":
    backtester = main()