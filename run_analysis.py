# run_analysis.py
"""Main runner script for patent cliff analysis and backtesting"""

import sys
from datetime import datetime

def run_current_analysis():
    """Run current patent cliff analysis"""
    from main_analysis import main as run_main_analysis
    
    print("Running Current Patent Cliff Analysis...")
    print("=" * 60)
    
    results = run_main_analysis()
    return results

def run_backtest():
    """Run backtesting analysis"""
    from backtest import main as run_backtest_analysis
    
    print("\nRunning Backtesting Analysis...")
    print("=" * 60)
    
    results = run_backtest_analysis()
    return results

def main():
    """Main execution function"""
    
    print(f"Patent Cliff Optimizer - Analysis Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Run current analysis
        current_results = run_current_analysis()
        
        # Run backtest
        backtest_results = run_backtest()
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print("✓ Current patent cliff analysis completed")
        print("✓ Historical backtesting completed")
        print("✓ All visualizations generated")
        
        # Summary statistics
        if backtest_results and 'metrics' in backtest_results:
            metrics = backtest_results['metrics']
            print(f"\nKEY RESULTS:")
            print(f"Strategy Return: {metrics['Annualized Return (Strategy)']:.2%}")
            print(f"Benchmark Return: {metrics['Annualized Return (Benchmark)']:.2%}")
            print(f"Excess Return: {metrics['Excess Return']:.2%}")
            print(f"Sharpe Ratio: {metrics['Sharpe Ratio (Strategy)']:.3f}")
            print(f"Max Drawdown: {metrics['Maximum Drawdown (Strategy)']:.2%}")
        
        return {
            'current_analysis': current_results,
            'backtest_results': backtest_results
        }
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = main()