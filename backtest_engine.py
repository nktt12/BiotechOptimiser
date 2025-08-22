# backtest_engine.py - Enhanced with new drug launch feature
"""
Patent Cliff Strategy Backtesting Engine - Enhanced with New Drug Launch Feature
Tests how the strategy would have performed from 2020-2024 using actual patent expiry data
and incorporating promising new drug launches during the period
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

from config import BACKTEST_TARGET_DRUGS, BACKTEST_CONFIG, BACKTEST_RISK_PARAMETERS, NEW_DRUG_LAUNCHES
from utils import (get_trading_dates, calculate_transaction_costs, apply_position_limits,
                   safe_divide, get_latest_revenues)

class EnhancedPatentCliffBacktester:
    """
    Enhanced backtester that includes new drug launches during the backtest period
    """
    
    def __init__(self, start_date='2020-01-01', end_date='2024-12-31'):
        self.start_date = start_date
        self.end_date = end_date
        self.rebalance_dates = None
        self.stock_data = None
        self.benchmark_data = None
        self.portfolio_history = []
        self.performance_metrics = {}
        self.drug_performance = {}
        self.launch_tracking = {}
        self.available_drugs = {}  # Drugs available at each point in time
        
    def load_historical_data(self):
        """Load stock price data and benchmark"""
        print(f"Loading data from {self.start_date} to {self.end_date}...")
        
        # Get unique tickers from both existing and new launch drugs
        existing_tickers = list(set([drug['ticker'] for drug in BACKTEST_TARGET_DRUGS.values()]))
        new_launch_tickers = list(set([drug['ticker'] for drug in NEW_DRUG_LAUNCHES.values()]))
        all_tickers = list(set(existing_tickers + new_launch_tickers))
        
        print(f"Existing backtest drugs: {len(BACKTEST_TARGET_DRUGS)}")
        print(f"New drug launches to track: {len(NEW_DRUG_LAUNCHES)}")
        print(f"Total unique tickers: {len(all_tickers)}")
        
        # Download stock data
        try:
            self.stock_data = yf.download(all_tickers, start=self.start_date, end=self.end_date)
            print(f"✓ Stock data loaded for {len(all_tickers)} tickers")
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
    
    def get_available_drugs_at_date(self, current_date: datetime) -> Dict:
        """
        Get all drugs available for investment at a specific date
        Includes existing drugs and newly launched drugs that have passed evaluation window
        """
        available = {}
        current_timestamp = pd.Timestamp(current_date)
        
        # Add existing drugs (always available)
        for drug_name, drug_info in BACKTEST_TARGET_DRUGS.items():
            available[drug_name] = {**drug_info, 'type': 'existing'}
        
        # Add new launches if they've passed the evaluation window
        if BACKTEST_CONFIG.get('include_new_launches', True):
            evaluation_days = BACKTEST_CONFIG.get('launch_evaluation_window', 30)
            
            for drug_name, drug_info in NEW_DRUG_LAUNCHES.items():
                try:
                    launch_date = pd.Timestamp(drug_info['launch_date'])
                    evaluation_date = launch_date + pd.Timedelta(days=evaluation_days)
                    
                    # Include drug if current date is after evaluation period
                    if current_timestamp >= evaluation_date:
                        available[f"{drug_name}_NEW"] = {
                            **drug_info, 
                            'type': 'new_launch',
                            'launch_date': drug_info['launch_date'],
                            'days_since_launch': (current_timestamp - launch_date).days
                        }
                except:
                    continue
        
        return available
    
    def calculate_new_launch_momentum(self, drug_info: Dict, current_date: datetime) -> float:
        """
        Calculate momentum score for newly launched drugs based on:
        - Time since launch
        - Peak sales potential
        - Current performance indicators
        """
        if drug_info['type'] != 'new_launch':
            return 1.0
        
        try:
            launch_date = pd.Timestamp(drug_info['launch_date'])
            current_timestamp = pd.Timestamp(current_date)
            days_since_launch = (current_timestamp - launch_date).days
            
            # Time momentum - peaks around 1-2 years post launch
            if days_since_launch < 365:  # First year - building momentum
                time_momentum = 0.5 + (days_since_launch / 365) * 0.5
            elif days_since_launch < 730:  # Second year - peak momentum
                time_momentum = 1.0 + ((730 - days_since_launch) / 365) * 0.3
            else:  # After 2 years - stable but lower momentum
                time_momentum = 0.8
            
            # Revenue potential momentum
            peak_sales = drug_info.get('peak_sales_estimate', 5.0)
            current_revenue = drug_info.get('revenue_billions', 0.1)
            growth_potential = min(2.0, peak_sales / max(0.1, current_revenue))
            
            # Status momentum
            status_multiplier = {
                'blockbuster': 1.3,
                'growing_blockbuster': 1.2,
                'pandemic_blockbuster': 1.1,  # Lower due to sustainability concerns
                'expanding_blockbuster': 1.25,
                'oncology_blockbuster': 1.15
            }.get(drug_info.get('status', 'standard'), 1.0)
            
            combined_momentum = time_momentum * min(1.5, growth_potential ** 0.5) * status_multiplier
            
            return min(2.0, combined_momentum)  # Cap at 2x momentum
            
        except:
            return 1.0
    
    def get_patent_cliff_weights(self, current_date: datetime) -> pd.Series:
        """
        Calculate portfolio weights including both existing drugs and new launches
        """
        weights = {}
        current_timestamp = pd.Timestamp(current_date)
        
        # Get all available drugs at this date
        available_drugs = self.get_available_drugs_at_date(current_date)
        
        for drug_name, drug_info in available_drugs.items():
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
            
            # Calculate base risk-adjusted weight
            weight = self.calculate_risk_weight(
                ticker=ticker,
                drug_name=drug_name,
                drug_revenue=drug_info['revenue_billions'],
                years_to_expiry=years_to_expiry,
                current_date=current_date,
                drug_status=drug_info.get('status', 'unknown'),
                drug_info=drug_info
            )
            
            # Apply new launch momentum if applicable
            if drug_info['type'] == 'new_launch':
                momentum = self.calculate_new_launch_momentum(drug_info, current_date)
                launch_boost = BACKTEST_CONFIG.get('new_launch_boost', 1.2)
                weight = weight * momentum * launch_boost
                
                # Track launch performance
                if drug_name not in self.launch_tracking:
                    self.launch_tracking[drug_name] = {
                        'first_inclusion_date': current_date,
                        'weights_history': [],
                        'momentum_history': []
                    }
                self.launch_tracking[drug_name]['weights_history'].append((current_date, weight))
                self.launch_tracking[drug_name]['momentum_history'].append((current_date, momentum))
            
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
                            years_to_expiry: float, current_date: datetime, drug_status: str,
                            drug_info: Dict) -> float:
        """Enhanced risk weight calculation including new launch considerations"""
        
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
        
        # Enhanced status factor for new launches
        if drug_info['type'] == 'new_launch':
            status_factor = {
                'blockbuster': 1.3,
                'growing_blockbuster': 1.25,
                'pandemic_blockbuster': 1.1,
                'expanding_blockbuster': 1.2,
                'oncology_blockbuster': 1.15
            }.get(drug_status, 1.1)  # Default boost for new launches
        else:
            status_factor = 1.2 if drug_status == 'still_protected' else 1.0
        
        # New launch specific factors
        if drug_info['type'] == 'new_launch':
            # Peak sales potential factor
            peak_sales = drug_info.get('peak_sales_estimate', 5.0)
            current_revenue = max(0.1, drug_revenue)  # Avoid division by zero
            growth_potential = min(1.5, peak_sales / current_revenue * 0.2)  # Scale factor
            
            # Launch recency factor (higher weight for recent successful launches)
            try:
                launch_date = pd.Timestamp(drug_info['launch_date'])
                current_timestamp = pd.Timestamp(current_date)
                days_since_launch = (current_timestamp - launch_date).days
                
                if days_since_launch < 365:  # First year
                    recency_factor = 1.1
                elif days_since_launch < 730:  # Second year
                    recency_factor = 1.0
                else:  # Beyond 2 years
                    recency_factor = 0.9
            except:
                recency_factor = 1.0
                growth_potential = 1.0
            
            status_factor = status_factor * growth_potential * recency_factor
        
        # Combined weight
        weight = time_factor * revenue_factor * status_factor
        
        return max(0.001, weight)  # Minimum weight to avoid zero positions
    
    def rebalance_portfolio(self, rebalance_date: datetime, 
                          current_weights: pd.Series) -> Tuple[pd.Series, float]:
        """Rebalance portfolio to target weights"""
        
        # Get target weights for this date (includes new launches)
        target_weights = self.get_patent_cliff_weights(rebalance_date)
        
        # Calculate transaction costs
        transaction_cost = calculate_transaction_costs(
            current_weights, 
            target_weights, 
            BACKTEST_CONFIG['transaction_cost']
        )
        
        return target_weights, transaction_cost
    
    def run_backtest(self) -> Dict:
        """Run the enhanced backtest simulation with new drug launches"""
        
        print("Starting enhanced backtest simulation (including new drug launches)...")
        
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
        
        print("Running daily simulation with new launch tracking...")
        
        for i, date in enumerate(trading_days):
            
            # Check if this is a rebalancing date
            is_rebalance_date = any(abs((date.date() - rd.date()).days) < 3 
                                  for rd in self.rebalance_dates)
            
            if is_rebalance_date or i == 0:
                # Rebalance portfolio (includes checking for new launches)
                new_weights, txn_cost = self.rebalance_portfolio(date, current_weights)
                current_weights = new_weights
                total_transaction_costs += txn_cost * portfolio_value
                
                # Track available drugs at this date
                available_drugs = self.get_available_drugs_at_date(date)
                new_launches_available = [name for name, info in available_drugs.items() 
                                        if info['type'] == 'new_launch']
                
                weight_history.append({
                    'date': date,
                    'weights': current_weights.copy(),
                    'transaction_cost': txn_cost,
                    'new_launches_available': len(new_launches_available),
                    'new_launch_names': new_launches_available[:3]  # Top 3 for space
                })
                
                if i % 50 == 0:  # Progress update
                    print(f"  Processed {i}/{len(trading_days)} days... " + 
                          f"New launches available: {len(new_launches_available)}")
            
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
            'total_transaction_costs': total_transaction_costs,
            'launch_tracking': self.launch_tracking
        }
        
        print("✓ Enhanced backtest simulation complete!")
        
        # Calculate performance metrics
        self.calculate_performance_metrics()
        
        # Analyze drug-specific performance including launches
        self.analyze_drug_performance()
        
        return self.portfolio_history
    
    def analyze_drug_performance(self):
        """Enhanced analysis including new drug launch performance"""
        
        # Separate performance by drug type and status
        expired_drugs = {k: v for k, v in BACKTEST_TARGET_DRUGS.items() 
                        if v.get('status') == 'expired_in_period'}
        protected_drugs = {k: v for k, v in BACKTEST_TARGET_DRUGS.items() 
                          if v.get('status') == 'still_protected'}
        new_launches = NEW_DRUG_LAUNCHES
        
        expired_tickers = list(set([drug['ticker'] for drug in expired_drugs.values()]))
        protected_tickers = list(set([drug['ticker'] for drug in protected_drugs.values()]))
        launch_tickers = list(set([drug['ticker'] for drug in new_launches.values()]))
        
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
            },
            'new_launches': {
                'count': len(new_launches),
                'tickers': launch_tickers,
                'avg_revenue': np.mean([drug['revenue_billions'] for drug in new_launches.values()]),
                'avg_peak_sales': np.mean([drug['peak_sales_estimate'] for drug in new_launches.values()])
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
            'Final Benchmark Value': f"${benchmark_values[-1]:,.0f}",
            'Total Portfolio Return': f"{total_portfolio_return:.2%}",
            'Portfolio Volatility': f"{portfolio_vol:.2%}",
            'Benchmark Volatility': f"{benchmark_vol:.2%}",
            'Portfolio Sharpe Ratio': f"{portfolio_sharpe:.3f}",
            'Maximum Drawdown': f"{max_drawdown:.2%}",
            'Win Rate': f"{win_rate:.1%}",
            'New Launches Tracked': len(self.launch_tracking),
        }
    
    def plot_results(self):
        """Create comprehensive visualization including new launch impact"""
        
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        
        dates = self.portfolio_history['dates']
        portfolio_values = self.portfolio_history['portfolio_values']
        benchmark_values = self.portfolio_history['benchmark_values']
        
        # Plot 1: Portfolio vs Benchmark Performance
        ax1 = axes[0, 0]
        ax1.plot(dates, portfolio_values, label='Patent Cliff + New Launch Strategy', 
                linewidth=2, color='blue')
        ax1.plot(dates, benchmark_values, label='S&P 500 Benchmark', 
                linewidth=2, color='gray')
        ax1.set_title('Enhanced Strategy Performance vs Benchmark', fontweight='bold', fontsize=12)
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Plot 2: Drug Performance by Category
        ax2 = axes[0, 1]
        if hasattr(self, 'drug_performance'):
            categories = []
            returns = []
            
            for category, data in self.drug_performance.items():
                category_name = {
                    'expired_drugs': 'Patent Cliff\nExpired',
                    'protected_drugs': 'Still\nProtected', 
                    'new_launches': 'New Drug\nLaunches'
                }.get(category, category)
                
                categories.append(category_name)
                returns.append(data.get('avg_return', 0) * 100)
            
            colors = ['red', 'green', 'purple']
            bars = ax2.bar(categories, returns, color=colors, alpha=0.7)
            ax2.set_title('Average Stock Performance by Category', fontweight='bold', fontsize=12)
            ax2.set_ylabel('Total Return (%)')
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Plot 3: New Launch Timeline
        ax3 = axes[0, 2]
        launch_dates = []
        launch_revenues = []
        launch_names = []
        
        for name, info in NEW_DRUG_LAUNCHES.items():
            try:
                launch_date = pd.Timestamp(info['launch_date'])
                if pd.Timestamp(self.start_date) <= launch_date <= pd.Timestamp(self.end_date):
                    launch_dates.append(launch_date)
                    launch_revenues.append(info['revenue_billions'])
                    launch_names.append(name.split('_')[0])  # Simplify names
            except:
                continue
        
        if launch_dates:
            scatter = ax3.scatter(launch_dates, launch_revenues, 
                                s=[r*20 for r in launch_revenues], 
                                alpha=0.6, c=launch_revenues, cmap='viridis')
            
            for i, name in enumerate(launch_names[:5]):  # Label top 5
                ax3.annotate(name, (launch_dates[i], launch_revenues[i]),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, alpha=0.8)
            
            ax3.set_title('New Drug Launch Timeline', fontweight='bold', fontsize=12)
            ax3.set_ylabel('Current Revenue ($B)')
            ax3.grid(True, alpha=0.3)
            plt.colorbar(scatter, ax=ax3, label='Revenue ($B)')
        
        # Plot 4: Rolling Returns
        ax4 = axes[1, 0]
        portfolio_returns = np.array(self.portfolio_history['daily_returns'])
        rolling_returns = pd.Series(portfolio_returns).rolling(window=63).mean() * 252
        ax4.plot(dates[62:], rolling_returns[62:], label='3-Month Rolling Return', color='blue')
        ax4.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax4.set_title('Rolling Annualized Returns', fontweight='bold', fontsize=12)
        ax4.set_ylabel('Annualized Return')
        ax4.grid(True, alpha=0.3)
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0%}'))
        
        # Plot 5: New Launch Weight Evolution
        ax5 = axes[1, 1]
        if self.launch_tracking:
            for launch_name, tracking_data in list(self.launch_tracking.items())[:3]:  # Top 3
                weight_dates = [w[0] for w in tracking_data['weights_history']]
                weights = [w[1]*100 for w in tracking_data['weights_history']]  # Convert to %
                ax5.plot(weight_dates, weights, label=launch_name.split('_')[0], 
                        marker='o', markersize=3)
            
            ax5.set_title('New Launch Portfolio Weights', fontweight='bold', fontsize=12)
            ax5.set_ylabel('Weight (%)')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
            ax5.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))
        
        # Plot 6: Company Concentration Evolution
        ax6 = axes[1, 2]
        weight_dates = [w['date'] for w in self.portfolio_history['weight_history']]
        
        # Get top companies by average weight over time
        all_company_weights = {}
        for w in self.portfolio_history['weight_history']:
            for ticker, weight in w['weights'].items():
                if ticker not in all_company_weights:
                    all_company_weights[ticker] = []
                all_company_weights[ticker].append(weight)
        
        # Calculate average weights and show top 4
        avg_weights = {ticker: np.mean(weights) for ticker, weights in all_company_weights.items()}
        top_companies = sorted(avg_weights.items(), key=lambda x: x[1], reverse=True)[:4]
        
        colors = ['blue', 'green', 'red', 'purple']
        for i, (ticker, _) in enumerate(top_companies):
            weights = []
            for w in self.portfolio_history['weight_history']:
                weights.append(w['weights'].get(ticker, 0) * 100)
            ax6.plot(weight_dates, weights, label=ticker, marker='o', 
                    markersize=2, color=colors[i])
        
        ax6.set_title('Top Company Weights Over Time', fontweight='bold', fontsize=12)
        ax6.set_ylabel('Weight (%)')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        ax6.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}%'))
        
        plt.tight_layout()
        plt.show()
    
    def print_performance_summary(self):
        """Print detailed performance summary including new launch analysis"""
        
        print("\n" + "="*80)
        print("ENHANCED PATENT CLIFF STRATEGY BACKTEST RESULTS (2020-2024)")
        print("Strategy: Patent Cliff Avoidance + New Drug Launch Opportunities")
        print("="*80)
        
        for metric, value in self.performance_metrics.items():
            print(f"{metric:<35} {value}")
        
        print("\n" + "="*80)
        print("DRUG PERFORMANCE ANALYSIS BY CATEGORY")
        print("="*80)
        
        if hasattr(self, 'drug_performance'):
            for group_name, group_data in self.drug_performance.items():
                if group_name == 'expired_drugs':
                    group_title = "DRUGS WITH PATENT CLIFFS (2020-2024)"
                elif group_name == 'protected_drugs':
                    group_title = "PROTECTED DRUGS (NO CLIFFS)"
                else:
                    group_title = "NEW DRUG LAUNCHES (2020-2024)"
                
                print(f"\n{group_title}:")
                print(f"  Number of drugs: {group_data['count']}")
                print(f"  Average revenue: ${group_data['avg_revenue']:.1f}B")
                if 'avg_peak_sales' in group_data:
                    print(f"  Average peak sales estimate: ${group_data['avg_peak_sales']:.1f}B")
                if 'avg_return' in group_data:
                    print(f"  Average stock return: {group_data['avg_return']:.2%}")
                    print(f"  Return volatility: {group_data.get('return_std', 0):.2%}")
                print(f"  Tickers: {', '.join(group_data['tickers'][:5])}...")  # Show first 5
        
        print("\n" + "="*80)
        print("NEW DRUG LAUNCH TRACKING RESULTS")
        print("="*80)
        
        if self.launch_tracking:
            print(f"Successfully tracked {len(self.launch_tracking)} new drug launches:")
            
            # Sort by average weight (impact)
            launch_impact = []
            for launch_name, tracking_data in self.launch_tracking.items():
                weights = [w[1] for w in tracking_data['weights_history']]
                avg_weight = np.mean(weights) if weights else 0
                launch_impact.append((launch_name, avg_weight, tracking_data))
            
            launch_impact.sort(key=lambda x: x[1], reverse=True)
            
            for launch_name, avg_weight, tracking_data in launch_impact[:10]:  # Top 10
                first_date = tracking_data['first_inclusion_date'].strftime('%Y-%m-%d')
                max_weight = max([w[1] for w in tracking_data['weights_history']], default=0)
                
                # Get original launch info
                original_name = launch_name.replace('_NEW', '')
                launch_info = NEW_DRUG_LAUNCHES.get(original_name, {})
                
                print(f"\n  • {launch_name}:")
                print(f"    Company: {launch_info.get('company', 'Unknown')}")
                print(f"    Launch Date: {launch_info.get('launch_date', 'Unknown')}")
                print(f"    First Inclusion: {first_date}")
                print(f"    Average Weight: {avg_weight:.3%}")
                print(f"    Peak Weight: {max_weight:.3%}")
                print(f"    Current Revenue: ${launch_info.get('revenue_billions', 0):.1f}B")
                print(f"    Peak Estimate: ${launch_info.get('peak_sales_estimate', 0):.1f}B")
        else:
            print("No new drug launches were tracked during the backtest period.")
        
        print("\n" + "="*80)
        print("PATENT CLIFF TIMELINE (All Tracked Drugs)")
        print("="*80)
        
        # Combine all drugs and sort by expiry
        all_drugs = []
        
        # Add existing drugs
        for drug_name, drug_info in BACKTEST_TARGET_DRUGS.items():
            try:
                cliff_date = pd.Timestamp(drug_info['patent_expiry'])
                all_drugs.append({
                    'drug': drug_name,
                    'company': drug_info['company'],
                    'ticker': drug_info['ticker'],
                    'revenue': drug_info['revenue_billions'],
                    'expiry': cliff_date,
                    'status': drug_info.get('status', 'unknown'),
                    'type': 'existing'
                })
            except:
                continue
        
        # Add new launches
        for drug_name, drug_info in NEW_DRUG_LAUNCHES.items():
            try:
                cliff_date = pd.Timestamp(drug_info['patent_expiry'])
                all_drugs.append({
                    'drug': drug_name,
                    'company': drug_info['company'],
                    'ticker': drug_info['ticker'],
                    'revenue': drug_info['revenue_billions'],
                    'expiry': cliff_date,
                    'status': 'new_launch',
                    'type': 'new_launch',
                    'launch_date': drug_info['launch_date']
                })
            except:
                continue
        
        # Sort by expiry date
        all_drugs.sort(key=lambda x: x['expiry'])
        
        print("Chronological order of patent expiries (first 20):")
        for i, drug in enumerate(all_drugs[:20]):
            if drug['type'] == 'existing':
                status_marker = "🔴" if drug['status'] == 'expired_in_period' else "🟢"
            else:
                status_marker = "🆕"
            
            expiry_str = drug['expiry'].strftime('%Y-%m-%d')
            print(f"{status_marker} {expiry_str}: {drug['drug'][:20]} ({drug['ticker']}) - ${drug['revenue']:.1f}B")
        
        print(f"\n🔴 = Expired during backtest period (2020-2024)")
        print(f"🟢 = Still protected beyond 2024") 
        print(f"🆕 = New drug launches (2020-2024)")
        
        print(f"\nTotal drugs tracked: {len(all_drugs)}")
        print(f"  - Existing drugs: {len([d for d in all_drugs if d['type'] == 'existing'])}")
        print(f"  - New launches: {len([d for d in all_drugs if d['type'] == 'new_launch'])}")

def main():
    """Main execution function for enhanced backtester"""
    
    print("Enhanced Patent Cliff Strategy Backtester")
    print("="*60)
    print("Features: Patent Cliff Avoidance + New Drug Launch Opportunities")
    print(f"Testing period: {BACKTEST_CONFIG['start_date']} to {BACKTEST_CONFIG['end_date']}")
    print(f"Existing drugs: {len(BACKTEST_TARGET_DRUGS)}")
    print(f"New launches to track: {len(NEW_DRUG_LAUNCHES)}")
    
    # Initialize enhanced backtester
    backtester = EnhancedPatentCliffBacktester(
        start_date=BACKTEST_CONFIG['start_date'],
        end_date=BACKTEST_CONFIG['end_date']
    )
    
    # Load data
    if not backtester.load_historical_data():
        print("Failed to load data. Exiting...")
        return None
    
    # Run enhanced backtest
    results = backtester.run_backtest()
    
    # Display results
    backtester.print_performance_summary()
    backtester.plot_results()
    
    return backtester

if __name__ == "__main__":
    backtester = main()