# backtest.py
"""Complete backtesting module for patent cliff optimizer with historical patent data"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import warnings
import os
warnings.filterwarnings('ignore')

from config import TARGET_DRUGS, BACKTEST_CONFIG, RISK_PARAMETERS
from utils import (get_trading_dates, apply_position_limits, calculate_transaction_costs, 
                   calculate_returns, format_performance_metrics, safe_divide)

class HistoricalPatentManager:
    """Manages historical patent data for backtesting"""
    
    def __init__(self):
        self.historical_snapshots = {}
        self.patent_timeline = {}
        
    def load_historical_snapshot(self, snapshot_date: str, data_path: str) -> Dict:
        """Load a historical Orange Book snapshot"""
        
        print(f"Loading historical patent data from {snapshot_date}...")
        
        try:
            # Load historical Orange Book files
            products = pd.read_csv(os.path.join(data_path, 'products.txt'), 
                                 sep='~', encoding='utf-8', low_memory=False)
            patents = pd.read_csv(os.path.join(data_path, 'patent.txt'), 
                                sep='~', encoding='utf-8', low_memory=False)
            exclusivity = pd.read_csv(os.path.join(data_path, 'exclusivity.txt'), 
                                    sep='~', encoding='utf-8', low_memory=False)
            
            # Store the snapshot
            self.historical_snapshots[snapshot_date] = {
                'products': products,
                'patents': patents,
                'exclusivity': exclusivity,
                'snapshot_date': pd.to_datetime(snapshot_date)
            }
            
            print(f"Loaded {len(patents)} patents from {snapshot_date}")
            return self.historical_snapshots[snapshot_date]
            
        except Exception as e:
            print(f"Error loading historical data from {snapshot_date}: {e}")
            return None
    
    def calculate_patent_cliffs_at_date(self, analysis_date: datetime, 
                                      target_drugs: Dict, 
                                      snapshot_date: str) -> pd.DataFrame:
        """Calculate patent cliffs from historical perspective"""
        
        if snapshot_date not in self.historical_snapshots:
            print(f"No snapshot available for {snapshot_date}")
            return pd.DataFrame()
        
        snapshot = self.historical_snapshots[snapshot_date]
        products = snapshot['products']
        patents = snapshot['patents']
        
        results = []
        
        for drug_name, drug_info in target_drugs.items():
            # Find the drug in historical products
            drug_products = products[
                products['Trade_Name'].str.upper().str.contains(drug_name, na=False)
            ]
            
            if not drug_products.empty:
                # Get NDA numbers for this drug
                nda_numbers = drug_products['Appl_No'].unique()
                
                # Find patents for these NDAs
                drug_patents = patents[patents['Appl_No'].isin(nda_numbers)].copy()
                
                # Convert patent expiry dates
                drug_patents['Patent_Expire_Date_Text'] = pd.to_datetime(
                    drug_patents['Patent_Expire_Date_Text'], errors='coerce'
                )
                
                # Filter to patents still valid at analysis date
                valid_patents = drug_patents[
                    drug_patents['Patent_Expire_Date_Text'] > analysis_date
                ]
                
                if not valid_patents.empty:
                    # Find next patent expiry
                    next_expiry = valid_patents['Patent_Expire_Date_Text'].min()
                    
                    results.append({
                        'drug': drug_name,
                        'company': drug_info['company'],
                        'ticker': drug_info['ticker'],
                        'revenue_billions': drug_info['revenue_billions'],
                        'next_patent_expiry': next_expiry,
                        'analysis_date': analysis_date,
                        'total_valid_patents': len(valid_patents)
                    })
        
        cliff_df = pd.DataFrame(results)
        
        if not cliff_df.empty:
            # Calculate time to expiry
            cliff_df['days_to_expiry'] = (
                cliff_df['next_patent_expiry'] - cliff_df['analysis_date']
            ).dt.days
            cliff_df['years_to_expiry'] = cliff_df['days_to_expiry'] / 365
        
        return cliff_df
    
    def build_patent_timeline(self, target_drugs: Dict, 
                            start_date: datetime, end_date: datetime,
                            snapshot_date: str = '2019-09-01') -> Dict:
        """Build timeline of patent cliff data for backtesting"""
        
        print(f"Building patent timeline from {start_date} to {end_date}")
        
        timeline = {}
        
        if snapshot_date not in self.historical_snapshots:
            print(f"No snapshot loaded for {snapshot_date}")
            return {}
        
        # Generate quarterly analysis dates for efficiency
        current_date = start_date
        while current_date <= end_date:
            cliff_analysis = self.calculate_patent_cliffs_at_date(
                current_date, target_drugs, snapshot_date
            )
            
            if not cliff_analysis.empty:
                timeline[current_date.strftime('%Y-%m-%d')] = cliff_analysis
            
            # Move to next quarter
            if current_date.month <= 3:
                current_date = current_date.replace(month=4, day=1)
            elif current_date.month <= 6:
                current_date = current_date.replace(month=7, day=1)
            elif current_date.month <= 9:
                current_date = current_date.replace(month=10, day=1)
            else:
                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
        
        self.patent_timeline = timeline
        print(f"Built timeline with {len(timeline)} time points")
        return timeline
    
    def get_patent_data_for_date(self, analysis_date: datetime) -> Optional[pd.DataFrame]:
        """Get patent cliff data for given date"""
        
        available_dates = [pd.to_datetime(d) for d in self.patent_timeline.keys()]
        
        if not available_dates:
            return None
        
        # Find closest date <= analysis_date
        valid_dates = [d for d in available_dates if d <= analysis_date]
        
        if not valid_dates:
            closest_date = min(available_dates)
        else:
            closest_date = max(valid_dates)
        
        date_key = closest_date.strftime('%Y-%m-%d')
        return self.patent_timeline.get(date_key)

class HistoricalPatentCliffAnalyzer:
    """Historical patent cliff analysis for backtesting"""
    
    def __init__(self, historical_manager: HistoricalPatentManager):
        self.historical_manager = historical_manager
        
    def calculate_portfolio_weights_historical(self, analysis_date: datetime,
                                             target_drugs: Dict,
                                             company_revenues: Dict) -> pd.Series:
        """Calculate portfolio weights using historical patent data"""
        
        # Get patent cliff data for this date
        cliff_data = self.historical_manager.get_patent_data_for_date(analysis_date)
        
        if cliff_data is None or cliff_data.empty:
            # Equal weights fallback
            tickers = list(set([info['ticker'] for info in target_drugs.values()]))
            equal_weight = 1.0 / len(tickers) if tickers else 0
            return pd.Series(equal_weight, index=tickers)
        
        weights = []
        
        for _, row in cliff_data.iterrows():
            ticker = row['ticker']
            total_revenue = company_revenues.get(ticker, 50.0)
            
            # Revenue risk percentage
            revenue_risk_percent = (row['revenue_billions'] / total_revenue) * 100
            
            # Time factor: reduce weight as patent cliff approaches
            time_factor = max(0.1, min(1.0, row['years_to_expiry'] / 5))
            
            # Risk factor: reduce weight based on revenue at risk
            risk_factor = max(0.1, 1 - min(0.9, revenue_risk_percent / 100))
            
            # Diversification penalty for multiple drugs
            diversification_factor = max(0.5, 1 - RISK_PARAMETERS.get('diversification_penalty', 0.1))
            
            # Combined weight
            raw_weight = time_factor * risk_factor * diversification_factor
            
            weights.append({
                'ticker': ticker,
                'raw_weight': raw_weight
            })
        
        weights_df = pd.DataFrame(weights)
        
        if not weights_df.empty and weights_df['raw_weight'].sum() > 0:
            # Apply position limits
            raw_weights = weights_df.set_index('ticker')['raw_weight']
            adjusted_weights = apply_position_limits(raw_weights)
            return adjusted_weights
        else:
            # Equal weights fallback
            tickers = list(set([info['ticker'] for info in target_drugs.values()]))
            equal_weight = 1.0 / len(tickers) if tickers else 0
            return pd.Series(equal_weight, index=tickers)

class PatentCliffBacktester:
    """Enhanced backtesting engine with historical patent data"""
    
    def __init__(self, config: Dict = None, historical_data_path: str = None):
        self.config = config or BACKTEST_CONFIG
        self.historical_data_path = historical_data_path
        
        # Initialize historical patent manager
        if historical_data_path and os.path.exists(historical_data_path):
            self.historical_manager = HistoricalPatentManager()
            self.historical_analyzer = None
            self.use_historical_data = True
            self.setup_historical_data()
        else:
            print("No historical data path provided or path doesn't exist. Using static weights.")
            self.use_historical_data = False
            
        self.results = {}
    
    def setup_historical_data(self):
        """Setup historical patent data for backtesting"""
        
        print("Setting up historical patent data...")
        
        try:
            # Load the historical snapshot
            self.historical_manager.load_historical_snapshot(
                '2019-09-01', 
                self.historical_data_path
            )
            
            # Build timeline for backtesting period
            start_date = pd.to_datetime(self.config['start_date'])
            end_date = pd.to_datetime(self.config['end_date'])
            
            timeline = self.historical_manager.build_patent_timeline(
                TARGET_DRUGS, start_date, end_date
            )
            
            # Create historical analyzer
            self.historical_analyzer = HistoricalPatentCliffAnalyzer(self.historical_manager)
            
            print("Historical patent data setup complete!")
            
        except Exception as e:
            print(f"Error setting up historical data: {e}")
            print("Falling back to static weights.")
            self.use_historical_data = False
    
    def get_company_revenues(self) -> Dict:
        """Get company revenue estimates"""
        company_revenues = {}
        for drug_info in TARGET_DRUGS.values():
            # Estimate total company revenue as ~5x drug revenue
            company_revenues[drug_info['ticker']] = drug_info['revenue_billions'] * 5
        return company_revenues
    
    def calculate_portfolio_weights(self, date: datetime) -> pd.Series:
        """Calculate portfolio weights for given date"""
        
        if self.use_historical_data and self.historical_analyzer:
            # Use historical patent data
            company_revenues = self.get_company_revenues()
            weights = self.historical_analyzer.calculate_portfolio_weights_historical(
                date, TARGET_DRUGS, company_revenues
            )
            return weights
        else:
            # Use equal weights as fallback
            tickers = list(set([info['ticker'] for info in TARGET_DRUGS.values()]))
            equal_weight = 1.0 / len(tickers) if tickers else 0
            return pd.Series(equal_weight, index=tickers)
    
    def prepare_stock_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Download and prepare stock and benchmark data"""
        
        print("Preparing stock market data...")
        
        # Get unique tickers
        tickers = list(set([drug_info['ticker'] for drug_info in TARGET_DRUGS.values()]))
        
        print(f"Downloading stock data for {len(tickers)} tickers: {tickers}")
        
        # Download stock data
        try:
            if len(tickers) > 1:
                stock_data = yf.download(
                    tickers,
                    start=self.config['start_date'],
                    end=self.config['end_date'],
                    progress=False
                )
            else:
                stock_data = yf.download(
                    tickers[0],
                    start=self.config['start_date'],
                    end=self.config['end_date'],
                    progress=False
                )
                # Convert to MultiIndex format for consistency
                stock_data.columns = pd.MultiIndex.from_product([stock_data.columns, [tickers[0]]])
        
        except Exception as e:
            print(f"Error downloading stock data: {e}")
            raise
        
        print(f"Downloading benchmark data ({self.config['benchmark_ticker']})...")
        
        # Download benchmark data
        try:
            benchmark_raw = yf.download(
                self.config['benchmark_ticker'],
                start=self.config['start_date'],
                end=self.config['end_date'],
                progress=False
            )
            
            # Extract benchmark price
            if isinstance(benchmark_raw.columns, pd.MultiIndex):
                benchmark_data = benchmark_raw['Adj Close'].iloc[:, 0]
            else:
                benchmark_data = benchmark_raw['Adj Close'] if 'Adj Close' in benchmark_raw.columns else benchmark_raw['Close']
        
        except Exception as e:
            print(f"Error downloading benchmark data: {e}")
            raise
        
        return stock_data, benchmark_data
    
    def run_simulation(self, stock_data: pd.DataFrame) -> Tuple[pd.DataFrame, List]:
        """Run portfolio simulation"""
        
        print("Running portfolio simulation...")
        
        # Get rebalancing dates
        rebalance_dates = get_trading_dates(
            self.config['start_date'],
            self.config['end_date'],
            self.config['rebalance_frequency']
        )
        
        # Extract price data
        try:
            if isinstance(stock_data.columns, pd.MultiIndex):
                if 'Adj Close' in stock_data.columns.get_level_values(0):
                    prices = stock_data['Adj Close']
                else:
                    prices = stock_data['Close']
            else:
                prices = stock_data
        except Exception as e:
            print(f"Error extracting prices: {e}")
            prices = stock_data
        
        # Initialize simulation variables
        portfolio_values = []
        transaction_costs_history = []
        weights_history = []
        
        initial_capital = self.config['initial_capital']
        current_capital = initial_capital
        current_weights = pd.Series(dtype=float)
        
        # Get available tickers that match our price data
        target_tickers = list(set([info['ticker'] for info in TARGET_DRUGS.values()]))
        available_tickers = [t for t in target_tickers if t in prices.columns]
        
        if not available_tickers:
            print(f"Warning: No matching tickers found!")
            print(f"Target tickers: {target_tickers}")
            print(f"Available columns: {list(prices.columns)}")
            # Use whatever tickers are available
            available_tickers = list(prices.columns)[:min(len(prices.columns), 5)]
        
        print(f"Simulating with {len(available_tickers)} tickers: {available_tickers}")
        prices = prices[available_tickers]
        
        # Simulate day by day
        for i, date in enumerate(prices.index):
            
            # Check if rebalancing is needed
            is_rebalance_date = any(
                abs((date.date() - rd.date()).days) <= 2 for rd in rebalance_dates
            ) or current_weights.empty
            
            if is_rebalance_date:
                # Calculate new weights
                target_weights = self.calculate_portfolio_weights(date)
                
                # Filter to available tickers and normalize
                target_weights = target_weights.reindex(available_tickers, fill_value=0)
                
                if target_weights.sum() > 0:
                    target_weights = target_weights / target_weights.sum()
                else:
                    # Equal weights fallback
                    target_weights = pd.Series(1.0/len(available_tickers), index=available_tickers)
                
                # Calculate transaction costs
                if not current_weights.empty:
                    transaction_cost = calculate_transaction_costs(
                        current_weights, target_weights, self.config.get('transaction_cost', 0.001)
                    )
                    current_capital *= (1 - transaction_cost)
                    
                    transaction_costs_history.append({
                        'date': date,
                        'cost_percent': transaction_cost,
                        'cost_dollars': current_capital * transaction_cost
                    })
                
                current_weights = target_weights
                weights_history.append({
                    'date': date,
                    'weights': current_weights.copy()
                })
            
            # Calculate daily return
            if not current_weights.empty and i > 0:
                prev_prices = prices.iloc[i-1][current_weights.index]
                curr_prices = prices.iloc[i][current_weights.index]
                
                # Calculate returns
                daily_returns = (curr_prices - prev_prices) / prev_prices
                daily_returns = daily_returns.fillna(0)
                
                # Portfolio return
                portfolio_return = (current_weights * daily_returns).sum()
                current_capital *= (1 + portfolio_return)
            
            # Record portfolio value
            portfolio_values.append({
                'date': date,
                'portfolio_value': current_capital
            })
        
        portfolio_df = pd.DataFrame(portfolio_values)
        
        print(f"Simulation complete. Final portfolio value: ${current_capital:,.2f}")
        print(f"Total return: {(current_capital/initial_capital - 1):.2%}")
        
        return portfolio_df, transaction_costs_history
    
    def calculate_performance_metrics(self, portfolio_df: pd.DataFrame, 
                                    benchmark_data: pd.Series) -> Dict:
        """Calculate comprehensive performance metrics"""
        
        print("Calculating performance metrics...")
        
        # Set portfolio index
        portfolio_df = portfolio_df.set_index('date')
        
        # Align data
        common_dates = portfolio_df.index.intersection(benchmark_data.index)
        portfolio_values = portfolio_df.reindex(common_dates)['portfolio_value']
        benchmark_values = benchmark_data.reindex(common_dates)
        
        # Calculate returns
        portfolio_returns = portfolio_values.pct_change().dropna()
        benchmark_returns = benchmark_values.pct_change().dropna()
        
        # Total returns
        total_portfolio_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
        total_benchmark_return = (benchmark_values.iloc[-1] / benchmark_values.iloc[0]) - 1
        
        # Annualized returns
        years = len(portfolio_returns) / 252
        ann_portfolio_return = (1 + total_portfolio_return) ** (1/years) - 1
        ann_benchmark_return = (1 + total_benchmark_return) ** (1/years) - 1
        
        # Volatility
        portfolio_vol = portfolio_returns.std() * np.sqrt(252)
        benchmark_vol = benchmark_returns.std() * np.sqrt(252)
        
        # Sharpe ratio
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
        aligned_returns = pd.DataFrame({
            'portfolio': portfolio_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if len(aligned_returns) > 1:
            covariance = np.cov(aligned_returns['portfolio'], aligned_returns['benchmark'])[0, 1]
            benchmark_variance = np.var(aligned_returns['benchmark'])
            beta = safe_divide(covariance, benchmark_variance, 1.0)
            alpha = ann_portfolio_return - (rf_rate + beta * (ann_benchmark_return - rf_rate))
            
            # Information ratio
            active_returns = aligned_returns['portfolio'] - aligned_returns['benchmark']
            tracking_error = active_returns.std() * np.sqrt(252)
            information_ratio = safe_divide(active_returns.mean() * 252, tracking_error)
        else:
            beta = 1.0
            alpha = 0.0
            information_ratio = 0.0
            tracking_error = 0.0
        
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
    
    def plot_results(self, portfolio_df: pd.DataFrame, 
                    benchmark_data: pd.Series, metrics: Dict):
        """Create backtest visualization"""
        
        # Create 2+1 layout as requested
        fig = plt.figure(figsize=(16, 12))
        
        # Top row: 2 plots
        ax1 = plt.subplot2grid((2, 2), (0, 0))
        ax2 = plt.subplot2grid((2, 2), (0, 1))
        
        # Bottom row: 1 plot spanning both columns
        ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)
        
        # Plot 1: Cumulative Performance
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
        
        # Plot 2: Rolling Sharpe Ratio
        portfolio_returns = portfolio_df['portfolio_value'].pct_change().dropna()
        rolling_sharpe = (portfolio_returns.rolling(60).mean() / 
                         portfolio_returns.rolling(60).std()) * np.sqrt(252)
        
        ax2.plot(rolling_sharpe.index, rolling_sharpe, color='green', linewidth=2)
        ax2.axhline(y=1.0, color='gray', linestyle='--', alpha=0.7, label='Sharpe = 1.0')
        ax2.set_title('Rolling 60-Day Sharpe Ratio', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Sharpe Ratio')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Performance Metrics Comparison
        strategy_metrics = [
            metrics['Annualized Return (Strategy)'],
            metrics['Volatility (Strategy)'],
            metrics['Sharpe Ratio (Strategy)'],
            metrics['Maximum Drawdown (Strategy)']
        ]
        
        benchmark_metrics = [
            metrics['Annualized Return (Benchmark)'],
            metrics['Volatility (Benchmark)'],
            metrics['Sharpe Ratio (Benchmark)'],
            metrics['Maximum Drawdown (Benchmark)']
        ]
        
        x = np.arange(len(strategy_metrics))
        width = 0.35
        
        bars1 = ax3.bar(x - width/2, strategy_metrics, width, label='Strategy', color='blue', alpha=0.7)
        bars2 = ax3.bar(x + width/2, benchmark_metrics, width, label='Benchmark', color='red', alpha=0.7)
        
        ax3.set_xlabel('Metrics')
        ax3.set_ylabel('Values')
        ax3.set_title('Performance Metrics Comparison', fontsize=14, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(['Ann. Return', 'Volatility', 'Sharpe', 'Max DD'], rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.show()
    
    def run_backtest(self) -> Dict:
        """Run complete backtesting pipeline"""
        
        print("Starting Patent Cliff Strategy Backtest")
        print("=" * 60)
        print(f"Period: {self.config['start_date']} to {self.config['end_date']}")
        print(f"Initial Capital: ${self.config['initial_capital']:,}")
        print(f"Rebalancing: {self.config['rebalance_frequency']}")
        print(f"Benchmark: {self.config['benchmark_ticker']}")
        print(f"Using Historical Patent Data: {self.use_historical_data}")
        print("=" * 60)
        
        try:
            # Prepare market data
            stock_data, benchmark_data = self.prepare_stock_data()
            
            # Run simulation
            portfolio_df, transaction_costs = self.run_simulation(stock_data)
            
            # Calculate metrics
            metrics = self.calculate_performance_metrics(portfolio_df, benchmark_data)
            
            # Display results
            print("\n" + "=" * 50)
            print("BACKTEST RESULTS")
            print("=" * 50)
            print(format_performance_metrics(metrics))
            
            # Transaction cost analysis
            if transaction_costs:
                total_tc_dollars = sum([tc['cost_dollars'] for tc in transaction_costs])
                total_tc_percent = total_tc_dollars / self.config['initial_capital']
                print(f"\nTransaction Costs:")
                print(f"Total: ${total_tc_dollars:,.2f} ({total_tc_percent:.2%})")
                print(f"Number of Rebalances: {len(transaction_costs)}")
            
            # Create visualizations
            print("\nGenerating visualizations...")
            self.plot_results(portfolio_df, benchmark_data, metrics)
            
            # Store results
            self.results = {
                'portfolio_performance': portfolio_df,
                'benchmark_performance': benchmark_data,
                'metrics': metrics,
                'transaction_costs': transaction_costs,
                'config': self.config
            }
            
            return self.results
            
        except Exception as e:
            print(f"Error during backtesting: {e}")
            raise

def main():
    """Main execution function"""
    
    # Set path to historical patent data (update this path!)
    historical_data_path = "C:\Users\Nikhi\Desktop\BiotechOptimiser\BiotechOptimiser\historical_patent_data"
    
    # You can also run without historical data by setting this to None
    # historical_data_path = None
    
    # Initialize backtester
    backtester = PatentCliffBacktester(
        config=BACKTEST_CONFIG,
        historical_data_path=historical_data_path
    )
    
    # Run backtest
    results = backtester.run_backtest()
    
    return results

if __name__ == "__main__":
    results = main()