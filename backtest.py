# backtest.py
"""Backtesting module for patent cliff optimizer"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

from config import TARGET_DRUGS, BACKTEST_CONFIG, RISK_PARAMETERS
from utils import (get_trading_dates, apply_position_limits, calculate_transaction_costs, 
                   calculate_returns, format_performance_metrics, safe_divide)
from main_analysis import PatentCliffAnalyzer

class PatentCliffBacktester:
    """Backtesting engine for patent cliff optimization strategy"""
    
    def __init__(self, config: Dict = None):
        self.config = config or BACKTEST_CONFIG
        self.analyzer = PatentCliffAnalyzer()
        self.results = {}
        
    def prepare_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Prepare stock price data and benchmark for backtesting"""
        
        print("Preparing backtesting data...")
        
        # Load analysis data (this gives us current weights)
        self.analyzer.load_data()
        analysis_results = self.analyzer.run_full_analysis()
        
        # Get stock price data for backtest period
        tickers = list(analysis_results['portfolio_weights']['ticker'].unique())
        
        # Add benchmark ticker
        all_tickers = tickers + [self.config['benchmark_ticker']]
        
        stock_data = yf.download(
            all_tickers,
            start=self.config['start_date'],
            end=self.config['end_date'],
            progress=False
        )
        
        # Download benchmark separately if needed
        benchmark_data = yf.download(
            self.config['benchmark_ticker'],
            start=self.config['start_date'],
            end=self.config['end_date'],
            progress=False
        )['Adj Close']
        
        return stock_data, benchmark_data, analysis_results
    
    def calculate_portfolio_weights_historical(self, date: datetime, 
                                             analysis_results: Dict) -> pd.Series:
        """Calculate portfolio weights for a given historical date"""
        
        # For this simplified version, we'll use the current analysis weights
        # In a more sophisticated version, you'd recalculate based on historical data
        portfolio_weights = analysis_results['portfolio_weights']
        
        weights_series = portfolio_weights.set_index('ticker')['normalized_portfolio_weight']
        
        # Apply any time-based adjustments here if needed
        # For example, you might want to reduce weights as we get closer to patent cliffs
        
        return weights_series
    
    def simulate_portfolio(self, stock_data: pd.DataFrame, 
                          analysis_results: Dict) -> pd.DataFrame:
        """Simulate portfolio performance over time"""
        
        print("Running portfolio simulation...")
        
        # Get rebalancing dates
        rebalance_dates = get_trading_dates(
            self.config['start_date'],
            self.config['end_date'],
            self.config['rebalance_frequency']
        )
        
        # Initialize tracking variables
        portfolio_values = []
        portfolio_weights_history = []
        transaction_costs_history = []
        
        initial_capital = self.config['initial_capital']
        current_capital = initial_capital
        current_weights = pd.Series(dtype=float)
        
        # Get price data (use Adj Close)
        if ('Adj Close',) in stock_data.columns.names:
            prices = stock_data['Adj Close']
        else:
            prices = stock_data
        
        # Ensure we have data for our tickers
        available_tickers = [t for t in analysis_results['portfolio_weights']['ticker'] 
                           if t in prices.columns]
        prices = prices[available_tickers]
        
        # Simulate day by day
        for date in prices.index:
            
            # Check if it's a rebalancing date
            is_rebalance_date = any(
                abs((date.date() - rd.date()).days) <= 5 for rd in rebalance_dates
            )
            
            if is_rebalance_date or current_weights.empty:
                # Calculate new target weights
                target_weights = self.calculate_portfolio_weights_historical(
                    date, analysis_results
                )
                
                # Filter to available tickers
                target_weights = target_weights.reindex(available_tickers, fill_value=0)
                target_weights = target_weights[target_weights > 0]
                
                if not target_weights.empty:
                    # Normalize weights
                    target_weights = target_weights / target_weights.sum()
                    
                    # Calculate transaction costs
                    transaction_cost = calculate_transaction_costs(
                        current_weights, target_weights, self.config['transaction_cost']
                    )
                    
                    # Apply transaction costs
                    current_capital *= (1 - transaction_cost)
                    transaction_costs_history.append({
                        'date': date,
                        'cost': transaction_cost,
                        'cost_dollars': current_capital * transaction_cost
                    })
                    
                    # Update weights
                    current_weights = target_weights
                    
            # Calculate daily portfolio return
            if not current_weights.empty and len(current_weights) > 0:
                # Get returns for this day
                prev_date_idx = prices.index.get_loc(date) - 1
                if prev_date_idx >= 0:
                    prev_prices = prices.iloc[prev_date_idx][current_weights.index]
                    curr_prices = prices.loc[date][current_weights.index]
                    
                    # Calculate returns
                    daily_returns = (curr_prices - prev_prices) / prev_prices
                    daily_returns = daily_returns.fillna(0)
                    
                    # Calculate portfolio return
                    portfolio_return = (current_weights * daily_returns).sum()
                    current_capital *= (1 + portfolio_return)
            
            # Record portfolio value
            portfolio_values.append({
                'date': date,
                'portfolio_value': current_capital,
                'weights': current_weights.copy() if not current_weights.empty else pd.Series(dtype=float)
            })
        
        return pd.DataFrame(portfolio_values), transaction_costs_history
    
    def calculate_performance_metrics(self, portfolio_df: pd.DataFrame, 
                                    benchmark_data: pd.DataFrame) -> Dict:
        """Calculate comprehensive performance metrics"""
        
        print("Calculating performance metrics...")
        
        # Align dates
        portfolio_df = portfolio_df.set_index('date')
        benchmark_data = benchmark_data.reindex(portfolio_df.index, method='ffill')
        
        # Calculate returns
        portfolio_returns = portfolio_df['portfolio_value'].pct_change().dropna()
        benchmark_returns = benchmark_data.pct_change().dropna()
        
        # Align return series
        common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
        portfolio_returns = portfolio_returns.reindex(common_dates)
        benchmark_returns = benchmark_returns.reindex(common_dates)
        
        # Basic performance metrics
        total_portfolio_return = (portfolio_df['portfolio_value'].iloc[-1] / 
                                 portfolio_df['portfolio_value'].iloc[0]) - 1
        total_benchmark_return = (benchmark_data.iloc[-1] / benchmark_data.iloc[0]) - 1
        
        # Annualized returns
        years = len(portfolio_returns) / 252
        ann_portfolio_return = (1 + total_portfolio_return) ** (1/years) - 1
        ann_benchmark_return = (1 + total_benchmark_return) ** (1/years) - 1
        
        # Volatility
        portfolio_vol = portfolio_returns.std() * np.sqrt(252)
        benchmark_vol = benchmark_returns.std() * np.sqrt(252)
        
        # Sharpe ratio (assuming risk-free rate = 2%)
        rf_rate = 0.02
        portfolio_sharpe = safe_divide(ann_portfolio_return - rf_rate, portfolio_vol)
        benchmark_sharpe = safe_divide(ann_benchmark_return - rf_rate, benchmark_vol)
        
        # Maximum drawdown
        portfolio_cumulative = (1 + portfolio_returns).cumprod()
        portfolio_dd = (portfolio_cumulative / portfolio_cumulative.expanding().max() - 1)
        max_drawdown = portfolio_dd.min()
        
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        benchmark_dd = (benchmark_cumulative / benchmark_cumulative.expanding().max() - 1)
        benchmark_max_dd = benchmark_dd.min()
        
        # Beta and Alpha
        covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
        benchmark_variance = np.var(benchmark_returns)
        beta = safe_divide(covariance, benchmark_variance, 1.0)
        alpha = ann_portfolio_return - (rf_rate + beta * (ann_benchmark_return - rf_rate))
        
        # Information ratio
        active_returns = portfolio_returns - benchmark_returns
        tracking_error = active_returns.std() * np.sqrt(252)
        information_ratio = safe_divide(active_returns.mean() * 252, tracking_error)
        
        # Win rate
        win_rate = (portfolio_returns > 0).mean()
        
        return {
            'Total Return (Strategy)': total_portfolio_return,
            'Total Return (Benchmark)': total_benchmark_return,
            'Annualized Return (Strategy)': ann_portfolio_return,
            'Annualized Return (Benchmark)': ann_benchmark_return,
            'Volatility (Strategy)': portfolio_vol,
            'Volatility (Benchmark)': benchmark_vol,
            'Sharpe Ratio (Strategy)': portfolio_sharpe,
            'Sharpe Ratio (Benchmark)': benchmark_sharpe,
            'Maximum Drawdown (Strategy)': max_drawdown,
            'Maximum Drawdown (Benchmark)': benchmark_max_dd,
            'Beta': beta,
            'Alpha': alpha,
            'Information Ratio': information_ratio,
            'Tracking Error': tracking_error,
            'Win Rate': win_rate,
            'Excess Return': ann_portfolio_return - ann_benchmark_return
        }
    
    def plot_backtest_results(self, portfolio_df: pd.DataFrame, 
                            benchmark_data: pd.DataFrame, 
                            metrics: Dict):
        """Create comprehensive backtest visualization"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Cumulative returns
        portfolio_df = portfolio_df.set_index('date')
        portfolio_normalized = portfolio_df['portfolio_value'] / portfolio_df['portfolio_value'].iloc[0]
        benchmark_normalized = benchmark_data / benchmark_data.iloc[0]
        
        ax1.plot(portfolio_normalized.index, portfolio_normalized, 
                label='Patent Cliff Strategy', linewidth=2, color='blue')
        ax1.plot(benchmark_normalized.index, benchmark_normalized, 
                label=f'{self.config["benchmark_ticker"]} Benchmark', 
                linewidth=2, color='red', alpha=0.7)
        
        ax1.set_title('Cumulative Performance', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Normalized Value')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Rolling Sharpe ratio
        portfolio_returns = portfolio_df['portfolio_value'].pct_change().dropna()
        rolling_sharpe = (portfolio_returns.rolling(60).mean() / 
                         portfolio_returns.rolling(60).std()) * np.sqrt(252)
        
        ax2.plot(rolling_sharpe.index, rolling_sharpe, color='green', linewidth=2)
        ax2.axhline(y=1.0, color='gray', linestyle='--', alpha=0.7)
        ax2.set_title('Rolling 60-Day Sharpe Ratio', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Sharpe Ratio')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Drawdown
        portfolio_cumulative = (1 + portfolio_returns).cumprod()
        drawdown = (portfolio_cumulative / portfolio_cumulative.expanding().max() - 1) * 100
        
        ax3.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
        ax3.plot(drawdown.index, drawdown, color='red', linewidth=1)
        ax3.set_title('Portfolio Drawdown', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Drawdown (%)')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Performance metrics comparison
        metrics_to_plot = [
            'Annualized Return (Strategy)',
            'Annualized Return (Benchmark)',
            'Volatility (Strategy)', 
            'Volatility (Benchmark)',
            'Sharpe Ratio (Strategy)',
            'Sharpe Ratio (Benchmark)'
        ]
        
        values = [metrics[m] for m in metrics_to_plot]
        colors = ['blue', 'red', 'blue', 'red', 'blue', 'red']
        
        bars = ax4.bar(range(len(values)), values, color=colors, alpha=0.7)
        ax4.set_xticks(range(len(values)))
        ax4.set_xticklabels([m.replace(' (Strategy)', '').replace(' (Benchmark)', '') 
                            for m in metrics_to_plot], rotation=45, ha='right')
        ax4.set_title('Performance Metrics Comparison', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.3f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.show()
    
    def run_backtest(self) -> Dict:
        """Run complete backtesting pipeline"""
        
        print("Starting Patent Cliff Strategy Backtest")
        print("=" * 50)
        print(f"Period: {self.config['start_date']} to {self.config['end_date']}")
        print(f"Initial Capital: ${self.config['initial_capital']:,}")
        print(f"Rebalancing: {self.config['rebalance_frequency']}")
        print(f"Benchmark: {self.config['benchmark_ticker']}")
        
        # Prepare data
        stock_data, benchmark_data, analysis_results = self.prepare_data()
        
        # Run simulation
        portfolio_df, transaction_costs = self.simulate_portfolio(stock_data, analysis_results)
        
        # Calculate performance metrics
        metrics = self.calculate_performance_metrics(portfolio_df, benchmark_data)
        
        # Display results
        print("\n" + format_performance_metrics(metrics))
        
        # Calculate total transaction costs
        total_transaction_costs = sum([tc['cost_dollars'] for tc in transaction_costs])
        print(f"\nTotal Transaction Costs: ${total_transaction_costs:,.2f}")
        print(f"Transaction Cost Impact: {total_transaction_costs/self.config['initial_capital']:.2%}")
        
        # Create visualizations
        print("\nGenerating backtest visualizations...")
        self.plot_backtest_results(portfolio_df, benchmark_data, metrics)
        
        # Store results
        self.results = {
            'portfolio_performance': portfolio_df,
            'benchmark_performance': benchmark_data,
            'metrics': metrics,
            'transaction_costs': transaction_costs,
            'analysis_results': analysis_results
        }
        
        return self.results

def main():
    """Main execution function for backtesting"""
    
    # Initialize backtester
    backtester = PatentCliffBacktester()
    
    # Run backtest
    results = backtester.run_backtest()
    
    return results

if __name__ == "__main__":
    results = main()