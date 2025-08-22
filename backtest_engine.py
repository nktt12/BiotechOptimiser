# backtest_engine.py
"""
Patent Cliff Strategy Backtesting Engine - Updated to use consolidated config
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

from config import BACKTEST_TARGET_DRUGS, BACKTEST_CONFIG, BACKTEST_RISK_PARAMETERS
from utils import (get_trading_dates, calculate_transaction_costs, apply_position_limits,
                   safe_divide, get_latest_revenues)

class PatentCliffBacktester:
    """
    Backtests the patent cliff avoidance strategy using known patent expiry dates
    """
    
    def __init__(self, start_date='2020-01-01', end_date='2023-06-31'):
        self.start_date = start_date
        self.end_date = end_date
        self.rebalance_dates = None
        self.stock_data = None
        self.benchmark_data = None
        self.portfolio_history = []
        self.performance_metrics = {}
        self.drug_performance = {}
        
    def load_historical_data(self):
        """Load stock price data and benchmark"""
        print(f"Loading data from {self.start_date} to {self.end_date}...")
        
        # Get unique tickers from backtest target drugs
        tickers = list(set([drug['ticker'] for drug in BACKTEST_TARGET_DRUGS.values()]))
        
        print(f"Target drugs for backtest: {len(BACKTEST_TARGET_DRUGS)}")
        expired_count = sum(1 for drug in BACKTEST_TARGET_DRUGS.values() if drug.get('status') == 'expired_in_period')
        protected_count = sum(1 for drug in BACKTEST_TARGET_DRUGS.values() if drug.get('status') == 'still_protected')
        print(f"  - Drugs that expired 2020-2024: {expired_count}")
        print(f"  - Drugs still protected: {protected_count}")
        
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
        Uses known patent expiry dates from backtest configuration
        """
        
        weights = {}
        current_timestamp = pd.Timestamp(current_date)
        
        for drug_name, drug_info in BACKTEST_TARGET_DRUGS.items():
            ticker = drug_info['ticker']
            
            # Parse patent expiry date
            try:
                patent_expiry = pd.Timestamp(drug_info['patent_expiry'])
            except:
                print(f"Warning: Could not parse patent expiry for {drug_name}")
                continue
            
            # Calculate years to expiry
            days_to_expiry = (patent_expiry - current_timestamp).days
            years_to_expiry = days_to_expiry / 365.25
            
            # Calculate risk-adjusted weight
            weight = self.calculate_risk_weight(
                ticker=ticker,
                drug_name=drug_name,
                drug_revenue=drug_info['revenue_billions'],
                years_to_expiry=years_to_expiry,
                current_date=current_date,
                drug_status=drug_info.get('status', 'unknown')
            )
            
            if weight > 0:
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
    
    def calculate_risk_weight(self, ticker: str, drug_name: str, drug_revenue: float, 
                            years_to_expiry: float, current_date: datetime, drug_status: str) -> float:
        """Calculate risk-adjusted weight for a company/drug"""
        
        # If drug has already expired, give it zero weight
        if years_to_expiry <= 0 or drug_status == 'expired_in_period':
            return BACKTEST_RISK_PARAMETERS.get('expired_drug_weight', 0.0)
        
        # Time decay factor - reduce weight as expiry approaches
        cliff_horizon = BACKTEST_RISK_PARAMETERS.get('cliff_horizon_years', 2.0)
        risk_decay = BACKTEST_RISK_PARAMETERS.get('risk_decay_factor', 0.5)
        
        if years_to_expiry <= 0.25:  # Less than 3 months
            time_factor = 0.05
        elif years_to_expiry <= 0.5:  # Less than 6 months
            time_factor = 0.1
        elif years_to_expiry <= 1.0:  # Less than 1 year
            time_factor = 0.2
        elif years_to_expiry <= cliff_horizon:  # Within cliff horizon
            # Gradual decay within cliff horizon
            decay_progress = (cliff_horizon - years_to_expiry) / cliff_horizon
            time_factor = 1.0 - (decay_progress * risk_decay)
            time_factor = max(0.2, time_factor)
        else:
            time_factor = 1.0  # Full weight if well beyond cliff horizon
        
        # Revenue size factor - larger revenue drugs get higher base weight
        revenue_factor = min(1.0, drug_revenue / 10.0)  # Scale by $10B revenue
        
        # Status bonus - drugs still protected get bonus
        status_factor = 1.2 if drug_status == 'still_protected' else 1.0
        
        # Combined weight
        weight = time_factor * revenue_factor * status_factor
        
        return max(0.001, weight)  # Minimum weight to avoid zero positions
    
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
                    # Handle both single ticker and multi-ticker data structures
                    if len(self.stock_data.columns.names) > 1:
                        # Multi-ticker format: ('Close', 'TICKER')
                        if ('Close', ticker) in self.stock_data.columns:
                            prev_price = self.stock_data[('Close', ticker)].iloc[i-1]
                            curr_price = self.stock_data[('Close', ticker)].iloc[i]
                        else:
                            continue
                    else:
                        # Single ticker or flat format
                        if ticker in self.stock_data.columns:
                            prev_price = self.stock_data[ticker].iloc[i-1]
                            curr_price = self.stock_data[ticker].iloc[i]
                        elif 'Close' in self.stock_data.columns:
                            prev_price = self.stock_data['Close'].iloc[i-1]
                            curr_price = self.stock_data['Close'].iloc[i]
                        else:
                            continue
                    
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
        
        # Analyze drug-specific performance
        self.analyze_drug_performance()
        
        return self.portfolio_history
    
    def analyze_drug_performance(self):
        """Analyze performance attribution by drug status"""
        
        # Separate performance by drug status
        expired_drugs = {k: v for k, v in BACKTEST_TARGET_DRUGS.items() if v.get('status') == 'expired_in_period'}
        protected_drugs = {k: v for k, v in BACKTEST_TARGET_DRUGS.items() if v.get('status') == 'still_protected'}
        
        expired_tickers = list(set([drug['ticker'] for drug in expired_drugs.values()]))
        protected_tickers = list(set([drug['ticker'] for drug in protected_drugs.values()]))
        
        # Calculate average performance for each group
        performance_analysis = {
            'expired_drugs': {
                'count': len(expired_drugs),
                'tickers': expired_tickers,
                'avg_revenue': np.mean([drug['revenue_billions'] for drug in expired_drugs.values()]),
            },
            'protected_drugs': {
                'count': len(protected_drugs),
                'tickers': protected_tickers,
                'avg_revenue': np.mean([drug['revenue_billions'] for drug in protected_drugs.values()]),
            }
        }
        
        # Calculate stock performance for each group
        if hasattr(self, 'stock_data') and len(self.stock_data) > 0:
            for group_name, group_data in performance_analysis.items():
                tickers = group_data['tickers']
                returns = []
                
                for ticker in tickers:
                    prices = None
                    
                    # Handle different data structures
                    if len(self.stock_data.columns.names) > 1:
                        # Multi-ticker format: ('Close', 'TICKER')
                        if ('Close', ticker) in self.stock_data.columns:
                            prices = self.stock_data[('Close', ticker)].dropna()
                    else:
                        # Single ticker or flat format
                        if ticker in self.stock_data.columns:
                            prices = self.stock_data[ticker].dropna()
                        elif 'Close' in self.stock_data.columns and len(tickers) == 1:
                            prices = self.stock_data['Close'].dropna()
                    
                    if prices is not None and len(prices) > 1:
                        total_return = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]
                        returns.append(total_return)
                
                if returns:
                    group_data['avg_return'] = np.mean(returns)
                    group_data['return_std'] = np.std(returns)
                else:
                    group_data['avg_return'] = 0
                    group_data['return_std'] = 0
        
        self.drug_performance = performance_analysis
    
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
        
        # Fix benchmark returns calculation
        benchmark_values = np.array(benchmark_values).flatten()  # Ensure 1D array
        if len(benchmark_values) > 1:
            benchmark_returns = np.diff(benchmark_values) / benchmark_values[:-1]
            benchmark_vol = np.std(benchmark_returns) * np.sqrt(252)
        else:
            benchmark_vol = 0.0
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        portfolio_sharpe = (annual_portfolio_return - risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
        benchmark_sharpe = (annual_benchmark_return - risk_free_rate) / benchmark_vol if benchmark_vol > 0 else 0
        
        # Maximum drawdown
        portfolio_peak = np.maximum.accumulate(portfolio_values)
        portfolio_drawdown = (portfolio_values - portfolio_peak) / portfolio_peak
        max_drawdown = np.min(portfolio_drawdown)
        
        # Win rate
        win_rate = np.sum(np.array(daily_returns) > 0) / len(daily_returns) if len(daily_returns) > 0 else 0
        
        self.performance_metrics = {
            'Total Transaction Costs': f"${self.portfolio_history['total_transaction_costs']:,.0f}",
            'Final Portfolio Value': f"${portfolio_values[-1]:,.0f}",
            'Final Benchmark Value': f"${benchmark_values[-1]:,.0f}"
        }
    
    def plot_results(self):
        """Create comprehensive visualization of backtest results"""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        dates = self.portfolio_history['dates']
        portfolio_values = self.portfolio_history['portfolio_values']
        benchmark_values = self.portfolio_history['benchmark_values']
        
        # Plot 1: Portfolio vs Benchmark Performance
        ax1 = axes[0, 0]
        ax1.plot(dates, portfolio_values, label='Patent Cliff Avoidance Strategy', linewidth=2, color='blue')
        ax1.plot(dates, benchmark_values, label='S&P 500 Benchmark', linewidth=2, color='gray')
        ax1.set_title('Portfolio Performance vs Benchmark (2020-2024)', fontweight='bold', fontsize=12)
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Plot 2: Drug Performance by Status
        ax2 = axes[0, 1]
        if hasattr(self, 'drug_performance'):
            expired_return = self.drug_performance['expired_drugs'].get('avg_return', 0)
            protected_return = self.drug_performance['protected_drugs'].get('avg_return', 0)
            
            bars = ax2.bar(['Drugs w/ Patent Cliffs\n(2020-2024)', 'Protected Drugs\n(No Cliffs)'], 
                          [expired_return * 100, protected_return * 100],
                          color=['red', 'green'], alpha=0.7)
            ax2.set_title('Average Stock Performance by Patent Status', fontweight='bold', fontsize=12)
            ax2.set_ylabel('Total Return (%)')
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Plot 3: Rolling Returns
        ax3 = axes[1, 0]
        portfolio_returns = np.array(self.portfolio_history['daily_returns'])
        rolling_returns = pd.Series(portfolio_returns).rolling(window=63).mean() * 252  # 3-month rolling annualized
        ax3.plot(dates[62:], rolling_returns[62:], label='3-Month Rolling Return', color='blue')
        ax3.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax3.set_title('Rolling Annualized Returns', fontweight='bold', fontsize=12)
        ax3.set_ylabel('Annualized Return')
        ax3.grid(True, alpha=0.3)
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0%}'))
        
        # Plot 4: Weight Evolution
        ax4 = axes[1, 1]
        weight_dates = [w['date'] for w in self.portfolio_history['weight_history']]
        
        # Get top tickers by average weight
        all_weights = {}
        for w in self.portfolio_history['weight_history']:
            for ticker, weight in w['weights'].items():
                if ticker not in all_weights:
                    all_weights[ticker] = []
                all_weights[ticker].append(weight)
        
        # Calculate average weights and show top 5
        avg_weights = {ticker: np.mean(weights) for ticker, weights in all_weights.items()}
        top_tickers = sorted(avg_weights.items(), key=lambda x: x[1], reverse=True)[:5]
        
        colors = ['blue', 'green', 'red', 'purple', 'orange']
        for i, (ticker, _) in enumerate(top_tickers):
            weights = []
            for w in self.portfolio_history['weight_history']:
                weights.append(w['weights'].get(ticker, 0) * 100)  # Convert to percentage
            ax4.plot(weight_dates, weights, label=ticker, marker='o', markersize=3, color=colors[i])
        
        ax4.set_title('Portfolio Weights Over Time (Top 5 Holdings)', fontweight='bold', fontsize=12)
        ax4.set_ylabel('Weight (%)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}%'))
        
        plt.tight_layout()
        plt.show()
    
    def print_performance_summary(self):
        """Print detailed performance summary"""
        
        print("\n" + "="*70)
        print("PATENT CLIFF AVOIDANCE STRATEGY BACKTEST RESULTS (2020-2024)")
        print("="*70)
        
        for metric, value in self.performance_metrics.items():
            print(f"{metric:<35} {value}")
        
        print("\n" + "="*70)
        print("DRUG PERFORMANCE ANALYSIS")
        print("="*70)
        
        if hasattr(self, 'drug_performance'):
            for group_name, group_data in self.drug_performance.items():
                group_title = "DRUGS WITH PATENT CLIFFS (2020-2024)" if group_name == 'expired_drugs' else "PROTECTED DRUGS (NO CLIFFS)"
                print(f"\n{group_title}:")
                print(f"  Number of drugs: {group_data['count']}")
                print(f"  Average revenue: ${group_data['avg_revenue']:.1f}B")
                if 'avg_return' in group_data:
                    print(f"  Average stock return: {group_data['avg_return']:.2%}")
                    print(f"  Return volatility: {group_data.get('return_std', 0):.2%}")
                print(f"  Tickers: {', '.join(group_data['tickers'])}")
        
        print("\n" + "="*70)
        print("PATENT CLIFF TIMELINE (Target Drugs)")
        print("="*70)
        
        cliff_events = []
        for drug_name, drug_info in BACKTEST_TARGET_DRUGS.items():
            try:
                cliff_date = pd.Timestamp(drug_info['patent_expiry'])
                cliff_events.append({
                    'drug': drug_name,
                    'company': drug_info['company'],
                    'ticker': drug_info['ticker'],
                    'revenue': drug_info['revenue_billions'],
                    'expiry': cliff_date,
                    'status': drug_info.get('status', 'unknown')
                })
            except:
                continue
        
        # Sort by expiry date
        cliff_events.sort(key=lambda x: x['expiry'])
        
        print("Chronological order of patent expiries:")
        for event in cliff_events:
            status_marker = "🔴" if event['status'] == 'expired_in_period' else "🟢"
            print(f"{status_marker} {event['expiry'].strftime('%Y-%m-%d')}: {event['drug']} ({event['ticker']}) - ${event['revenue']:.1f}B revenue")
        
        print(f"\n🔴 = Expired during backtest period (2020-2024)")
        print(f"🟢 = Still protected beyond 2024")

def main():
    """Main execution function"""
    
    print("Patent Cliff Strategy Backtester - Using Consolidated Config")
    print("="*60)
    print("Testing patent cliff avoidance using historical data (2020-2024)")
    print(f"Using {len(BACKTEST_TARGET_DRUGS)} target drugs with known patent cliff dates")
    
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