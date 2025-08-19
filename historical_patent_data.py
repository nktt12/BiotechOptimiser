# historical_patent_data.py
"""Historical patent data management for backtesting"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import os

class HistoricalPatentManager:
    """Manages historical patent data for backtesting"""
    
    def __init__(self):
        self.historical_snapshots = {}
        self.patent_timeline = {}
        
    def load_historical_snapshot(self, snapshot_date: str, data_path: str) -> Dict:
        """Load a historical Orange Book snapshot"""
        
        print(f"Loading historical patent data from {snapshot_date}...")
        
        try:
            # Load historical Orange Book files (same format as current)
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
        """Calculate what patent cliffs looked like from a historical perspective"""
        
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
                
                # Find patents for these NDAs in historical data
                drug_patents = patents[patents['Appl_No'].isin(nda_numbers)].copy()
                
                # Convert patent expiry dates
                drug_patents['Patent_Expire_Date_Text'] = pd.to_datetime(
                    drug_patents['Patent_Expire_Date_Text'], errors='coerce'
                )
                
                # Filter to patents that were still valid at the analysis date
                # (i.e., hadn't expired yet from the historical perspective)
                valid_patents = drug_patents[
                    drug_patents['Patent_Expire_Date_Text'] > analysis_date
                ]
                
                if not valid_patents.empty:
                    # Find the next patent expiry after the analysis date
                    next_expiry = valid_patents['Patent_Expire_Date_Text'].min()
                    
                    results.append({
                        'drug': drug_name,
                        'company': drug_info['company'],
                        'ticker': drug_info['ticker'],
                        'revenue_billions': drug_info['revenue_billions'],
                        'next_patent_expiry': next_expiry,
                        'analysis_date': analysis_date,
                        'total_valid_patents': len(valid_patents),
                        'snapshot_source': snapshot_date
                    })
        
        cliff_df = pd.DataFrame(results)
        
        if not cliff_df.empty:
            # Calculate time to expiry from the historical analysis date
            cliff_df['days_to_expiry'] = (
                cliff_df['next_patent_expiry'] - cliff_df['analysis_date']
            ).dt.days
            cliff_df['years_to_expiry'] = cliff_df['days_to_expiry'] / 365
        
        return cliff_df
    
    def build_patent_timeline(self, target_drugs: Dict, 
                            start_date: datetime, end_date: datetime) -> Dict:
        """Build a timeline of patent cliff data for backtesting"""
        
        print(f"Building patent timeline from {start_date} to {end_date}")
        
        timeline = {}
        
        # For now, we'll use the 2019 snapshot for the entire period
        # In a more sophisticated implementation, you'd have multiple snapshots
        snapshot_date = '2019-09-01'
        
        if snapshot_date not in self.historical_snapshots:
            print(f"No snapshot loaded for {snapshot_date}")
            return {}
        
        # Generate monthly analysis dates
        current_date = start_date
        while current_date <= end_date:
            cliff_analysis = self.calculate_patent_cliffs_at_date(
                current_date, target_drugs, snapshot_date
            )
            
            if not cliff_analysis.empty:
                timeline[current_date.strftime('%Y-%m-%d')] = cliff_analysis
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        self.patent_timeline = timeline
        print(f"Built timeline with {len(timeline)} time points")
        return timeline
    
    def get_patent_data_for_date(self, analysis_date: datetime) -> Optional[pd.DataFrame]:
        """Get the most appropriate patent cliff data for a given date"""
        
        # Find the closest available date in our timeline
        available_dates = [pd.to_datetime(d) for d in self.patent_timeline.keys()]
        
        if not available_dates:
            return None
        
        # Find closest date that's <= analysis_date
        valid_dates = [d for d in available_dates if d <= analysis_date]
        
        if not valid_dates:
            # Use the earliest available if analysis_date is before our data
            closest_date = min(available_dates)
        else:
            # Use the latest available that's still <= analysis_date
            closest_date = max(valid_dates)
        
        date_key = closest_date.strftime('%Y-%m-%d')
        return self.patent_timeline.get(date_key)

# Modified PatentCliffAnalyzer for historical analysis
class HistoricalPatentCliffAnalyzer:
    """Historical version of PatentCliffAnalyzer"""
    
    def __init__(self, historical_manager: HistoricalPatentManager):
        self.historical_manager = historical_manager
        self.company_revenues = None  # Will need to set this externally
        
    def calculate_portfolio_weights_historical(self, analysis_date: datetime,
                                             target_drugs: Dict,
                                             company_revenues: Dict) -> pd.Series:
        """Calculate portfolio weights based on historical patent data"""
        
        # Get patent cliff data for this date
        cliff_data = self.historical_manager.get_patent_data_for_date(analysis_date)
        
        if cliff_data is None or cliff_data.empty:
            # Return equal weights as fallback
            tickers = list(set([info['ticker'] for info in target_drugs.values()]))
            equal_weight = 1.0 / len(tickers)
            return pd.Series(equal_weight, index=tickers)
        
        # Calculate weights using the same logic as current analyzer
        weights = []
        
        for _, row in cliff_data.iterrows():
            ticker = row['ticker']
            total_revenue = company_revenues.get(ticker, 50.0)
            
            # Calculate revenue risk percentage
            revenue_risk_percent = (row['revenue_billions'] / total_revenue) * 100
            
            # Time factor: reduce weight as patent cliff approaches
            time_factor = max(0.1, min(1.0, row['years_to_expiry'] / 5))
            
            # Risk factor: reduce weight based on revenue at risk
            risk_factor = max(0.1, 1 - min(0.9, revenue_risk_percent / 100))
            
            # Combined weight
            raw_weight = time_factor * risk_factor
            
            weights.append({
                'ticker': ticker,
                'raw_weight': raw_weight,
                'years_to_cliff': row['years_to_expiry'],
                'revenue_risk_percent': revenue_risk_percent
            })
        
        weights_df = pd.DataFrame(weights)
        
        # Normalize weights
        if not weights_df.empty and weights_df['raw_weight'].sum() > 0:
            weights_df['normalized_weight'] = (
                weights_df['raw_weight'] / weights_df['raw_weight'].sum()
            )
            return weights_df.set_index('ticker')['normalized_weight']
        else:
            # Fallback to equal weights
            tickers = list(set([info['ticker'] for info in target_drugs.values()]))
            equal_weight = 1.0 / len(tickers)
            return pd.Series(equal_weight, index=tickers)

# Usage example:
def setup_historical_backtesting(historical_data_path: str, target_drugs: Dict):
    """Setup historical patent data for backtesting"""
    
    # Initialize historical manager
    hist_manager = HistoricalPatentManager()
    
    # Load historical snapshot (e.g., from September 2019)
    hist_manager.load_historical_snapshot('2019-09-01', historical_data_path)
    
    # Build timeline for backtesting period
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    timeline = hist_manager.build_patent_timeline(target_drugs, start_date, end_date)
    
    # Create historical analyzer
    historical_analyzer = HistoricalPatentCliffAnalyzer(hist_manager)
    
    return historical_analyzer, timeline