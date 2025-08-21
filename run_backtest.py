# run_backtest.py
"""
Simple script to run the patent cliff backtest with your 2019 Orange Book data
"""

import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import your modules
from backtest_engine import PatentCliffBacktester
from config import TARGET_DRUGS, BACKTEST_CONFIG

def analyze_orange_book_coverage():
    """
    Analyze how many of your target drugs are found in the 2019 Orange Book
    Run this first to validate your data
    """
    print("ANALYZING ORANGE BOOK COVERAGE")
    print("="*50)
    
    # You'll need to update these paths
    try:
        products = pd.read_csv('data/orange_book_2019/products.txt', sep='~', encoding='latin-1')
        patents = pd.read_csv('data/orange_book_2019/patent.txt', sep='~', encoding='latin-1')
        
        print(f"Orange Book contains:")
        print(f"  - {len(products)} products")
        print(f"  - {len(patents)} patents")
        print(f"  - {len(products['Trade_Name'].unique())} unique trade names")
        
        print(f"\nTarget drugs coverage:")
        found_drugs = []
        missing_drugs = []
        
        for drug_name in TARGET_DRUGS.keys():
            # Search for drug in products (case-insensitive)
            matches = products[products['Trade_Name'].str.upper().str.contains(drug_name.upper(), na=False)]
            
            if not matches.empty:
                found_drugs.append(drug_name)
                print(f"  ✓ {drug_name}: {len(matches)} products found")
            else:
                missing_drugs.append(drug_name)
                print(f"  ✗ {drug_name}: Not found")
        
        print(f"\nSummary:")
        print(f"  - Found: {len(found_drugs)}/{len(TARGET_DRUGS)} drugs ({len(found_drugs)/len(TARGET_DRUGS)*100:.1f}%)")
        print(f"  - Missing: {len(missing_drugs)} drugs")
        
        if missing_drugs:
            print(f"\nMissing drugs may have different trade names in Orange Book.")
            print(f"Try searching for alternative names or active ingredients.")
            
        return found_drugs, missing_drugs
        
    except FileNotFoundError as e:
        print(f"✗ Could not load Orange Book files: {e}")
        print("Please update the file paths in this script.")
        return [], list(TARGET_DRUGS.keys())
    
def run_patent_cliff_analysis():
    """
    Run the patent cliff analysis on your 2019 data
    """
    print("\nSTARTING PATENT CLIFF ANALYSIS")
    print("="*50)
    
    # First check drug coverage
    found_drugs, missing_drugs = analyze_orange_book_coverage()
    
    if len(found_drugs) < 5:
        print(f"\nWarning: Only {len(found_drugs)} drugs found in Orange Book.")
        print("Consider updating drug names or file paths before proceeding.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return None
    
    # Initialize and run backtester
    print(f"\nInitializing backtester...")
    backtester = PatentCliffBacktester(
        start_date=BACKTEST_CONFIG['start_date'],
        end_date=BACKTEST_CONFIG['end_date']
    )
    
    # Load all data
    print("Loading historical data...")
    if not backtester.load_historical_data():
        print("Failed to load data. Check file paths and try again.")
        return None
    
    # Run the backtest
    print("Running backtest simulation...")
    try:
        results = backtester.run_backtest()
        
        # Display results
        backtester.print_performance_summary()
        backtester.plot_results()
        
        return backtester
        
    except Exception as e:
        print(f"Error during backtest: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_specific_patent_events():
    """
    Look at specific patent cliff events in your data
    """
    print("\nANALYZING SPECIFIC PATENT EVENTS")
    print("="*50)
    
    # Load Orange Book data
    try:
        products = pd.read_csv('data/orange_book_2019/products.txt', sep='~', encoding='latin-1')
        patents = pd.read_csv('data/orange_book_2019/patent.txt', sep='~', encoding='latin-1')
        
        # Convert patent dates
        patents['Patent_Expire_Date_Text'] = pd.to_datetime(patents['Patent_Expire_Date_Text'], errors='coerce')
        
        # Find patents expiring 2020-2024
        target_period = patents[
            (patents['Patent_Expire_Date_Text'] >= '2020-01-01') & 
            (patents['Patent_Expire_Date_Text'] <= '2024-12-31')
        ]
        
        print(f"Patents expiring 2020-2024: {len(target_period)}")
        
        # Match with target drugs
        print("\nTarget drugs with patents expiring 2020-2024:")
        
        for drug_name in TARGET_DRUGS.keys():
            # Find products for this drug
            drug_products = products[products['Trade_Name'].str.upper().str.contains(drug_name.upper(), na=False)]
            
            if not drug_products.empty:
                # Find patents for these products
                nda_numbers = drug_products['Appl_No'].unique()
                drug_patents = target_period[target_period['Appl_No'].isin(nda_numbers)]
                
                if not drug_patents.empty:
                    earliest = drug_patents['Patent_Expire_Date_Text'].min()
                    latest = drug_patents['Patent_Expire_Date_Text'].max()
                    print(f"  {drug_name}: {len(drug_patents)} patents, earliest: {earliest.strftime('%Y-%m-%d')}, latest: {latest.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        print(f"Error analyzing patent events: {e}")

def main():
    """
    Main execution function
    """
    print("PATENT CLIFF BACKTEST WITH 2019 ORANGE BOOK DATA")
    print("="*60)
    print("This will test the patent cliff avoidance strategy using actual")
    print("FDA Orange Book data from 2019 to predict patent cliffs 2020-2024")
    print()
    
    # Step 1: Analyze what data we have
    analyze_specific_patent_events()
    
    # Step 2: Run the full backtest
    backtester = run_patent_cliff_analysis()
    
    if backtester:
        print("\n" + "="*60)
        print("BACKTEST COMPLETE!")
        print("="*60)
        print("Results show how the patent cliff strategy would have performed")
        print("from 2020-2024 using actual patent expiry data from 2019.")
        print("\nKey things to analyze:")
        print("1. Did the strategy avoid major patent cliff events?")
        print("2. How did performance compare to S&P 500?")
        print("3. Were transaction costs reasonable?")
        print("4. What would you change going forward?")
        
        return backtester
    else:
        print("\nBacktest failed. Please check your data files and try again.")
        return None

if __name__ == "__main__":
    backtester = main()