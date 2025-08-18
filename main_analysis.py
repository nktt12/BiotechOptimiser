# main_analysis.py
"""Main patent cliff analysis module"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from typing import Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

from config import TARGET_DRUGS, DATA_PATHS, ANALYSIS_CONFIG, RISK_PARAMETERS
from utils import (load_orange_book_data, get_unique_tickers, download_stock_data, 
                   get_latest_revenues, apply_position_limits)

class PatentCliffAnalyzer:
    """Main class for patent cliff analysis"""
    
    def __init__(self):
        self.products = None
        self.patents = None
        self.exclusivity = None
        self.stock_data = None
        self.company_revenues = None
        
    def load_data(self):
        """Load all required data"""
        print("Loading Orange Book data...")
        self.products, self.patents, self.exclusivity = load_orange_book_data(DATA_PATHS)
        
        print("Downloading stock data...")
        tickers = get_unique_tickers(TARGET_DRUGS)
        self.stock_data = download_stock_data(
            tickers, 
            ANALYSIS_CONFIG['stock_data_start'], 
            ANALYSIS_CONFIG['stock_data_end']
        )
        
        print("Fetching company revenues...")
        self.company_revenues = get_latest_revenues(tickers)
        print(f"Company revenues: {self.company_revenues}")
        
    def analyze_patent_cliffs(self) -> pd.DataFrame:
        """Find patent expiry dates for target drugs"""
        
        results = []
        
        for drug_name, drug_info in TARGET_DRUGS.items():
            # Find the drug in products
            drug_products = self.products[
                self.products['Trade_Name'].str.upper().str.contains(drug_name, na=False)
            ]
            
            if not drug_products.empty:
                # Get NDA numbers for this drug
                nda_numbers = drug_products['Appl_No'].unique()
                
                # Find patents for these NDAs
                drug_patents = self.patents[self.patents['Appl_No'].isin(nda_numbers)].copy()
                
                # Convert patent expiry dates and find the latest one
                drug_patents['Patent_Expire_Date_Text'] = pd.to_datetime(
                    drug_patents['Patent_Expire_Date_Text'], errors='coerce'
                )
                latest_expiry = drug_patents['Patent_Expire_Date_Text'].max()
                
                results.append({
                    'drug': drug_name,
                    'company': drug_info['company'],
                    'ticker': drug_info['ticker'],
                    'revenue_billions': drug_info['revenue_billions'],
                    'latest_patent_expiry': latest_expiry,
                    'total_patents': len(drug_patents)
                })
        
        cliff_df = pd.DataFrame(results)
        
        # Calculate time to expiry
        cliff_df['days_to_expiry'] = (
            cliff_df['latest_patent_expiry'] - pd.Timestamp.now()
        ).dt.days
        cliff_df['years_to_expiry'] = cliff_df['days_to_expiry'] / 365
        
        return cliff_df
    
    def calculate_revenue_risk(self, cliff_analysis: pd.DataFrame) -> pd.DataFrame:
        """Calculate revenue at risk by individual drug"""
        
        risk_analysis = []
        
        for _, row in cliff_analysis.iterrows():
            ticker = row['ticker']
            drug_revenue = row['revenue_billions']
            total_revenue = self.company_revenues.get(ticker, 50.0)  # Default fallback
            
            risk_percentage = (drug_revenue / total_revenue * 100) if total_revenue > 0 else 0
            
            risk_analysis.append({
                'ticker': ticker,
                'drug': row['drug'],
                'drug_revenue': drug_revenue,
                'total_company_revenue': total_revenue,
                'revenue_at_risk_percent': risk_percentage,
                'years_to_cliff': row['years_to_expiry'],
                'days_to_cliff': row['days_to_expiry']
            })
        
        return pd.DataFrame(risk_analysis)
    
    def calculate_company_risk(self, cliff_analysis: pd.DataFrame) -> pd.DataFrame:
        """Aggregate patent cliff risk at company level"""
        
        company_risk = []
        
        for ticker in cliff_analysis['ticker'].unique():
            company_drugs = cliff_analysis[cliff_analysis['ticker'] == ticker]
            
            # Calculate total revenue at risk for this company
            total_drug_revenue = company_drugs['revenue_billions'].sum()
            
            # Find the earliest patent cliff (most urgent risk)
            earliest_cliff = company_drugs['latest_patent_expiry'].min()
            years_to_earliest_cliff = (earliest_cliff - pd.Timestamp.now()).days / 365
            
            # Count number of drugs at risk
            drugs_at_risk = len(company_drugs)
            
            # Get company name
            company_name = company_drugs['company'].iloc[0]
            
            company_risk.append({
                'ticker': ticker,
                'company': company_name,
                'total_drug_revenue_at_risk': total_drug_revenue,
                'years_to_earliest_cliff': years_to_earliest_cliff,
                'number_of_drugs_at_risk': drugs_at_risk,
                'drug_list': ', '.join(company_drugs['drug'].tolist())
            })
        
        return pd.DataFrame(company_risk)
    
    def calculate_portfolio_weights(self, company_risk: pd.DataFrame) -> pd.DataFrame:
        """Calculate risk-adjusted portfolio weights"""
        
        weights = []
        
        for _, row in company_risk.iterrows():
            ticker = row['ticker']
            total_revenue = self.company_revenues.get(ticker, 50.0)
            
            # Calculate what % of company revenue is at patent cliff risk
            revenue_risk_percent = (row['total_drug_revenue_at_risk'] / total_revenue) * 100
            
            # Time factor: reduce weight as earliest cliff approaches
            time_factor = max(0.1, min(1.0, row['years_to_earliest_cliff'] / 5))
            
            # Risk factor: reduce weight based on total revenue at risk
            risk_factor = max(0.1, 1 - min(0.9, revenue_risk_percent / 100))
            
            # Diversification penalty: slight penalty for multiple drugs at risk
            diversification_factor = max(0.5, 1 - (row['number_of_drugs_at_risk'] - 1) * RISK_PARAMETERS['diversification_penalty'])
            
            # Combined adjustment
            risk_adjusted_weight = time_factor * risk_factor * diversification_factor
            
            weights.append({
                'ticker': ticker,
                'company': row['company'],
                'total_revenue_at_risk_billions': row['total_drug_revenue_at_risk'],
                'revenue_risk_percent': revenue_risk_percent,
                'years_to_earliest_cliff': row['years_to_earliest_cliff'],
                'drugs_at_risk': row['number_of_drugs_at_risk'],
                'drug_list': row['drug_list'],
                'time_factor': time_factor,
                'risk_factor': risk_factor,
                'diversification_factor': diversification_factor,
                'raw_weight': risk_adjusted_weight
            })
        
        weights_df = pd.DataFrame(weights)
        
        # Apply position limits and normalize
        raw_weights = weights_df.set_index('ticker')['raw_weight']
        adjusted_weights = apply_position_limits(raw_weights)
        
        weights_df['normalized_portfolio_weight'] = weights_df['ticker'].map(adjusted_weights)
        
        return weights_df
    
    def plot_analysis(self, revenue_risk: pd.DataFrame):
        """Create visualization plots"""
        
        plt.style.use('default')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Stock prices over time
        tickers = revenue_risk['ticker'].unique()
        for ticker in tickers:
            if ('Close', ticker) in self.stock_data.columns:
                prices = self.stock_data[('Close', ticker)].dropna()
                normalized_prices = prices / prices.iloc[0] * 100
                ax1.plot(normalized_prices.index, normalized_prices, 
                        label=f"{ticker}", linewidth=2, alpha=0.7)
        
        ax1.set_title('Normalized Stock Performance (Base = 100)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Normalized Price')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Risk vs Time to Patent Cliff
        scatter = ax2.scatter(revenue_risk['years_to_cliff'], 
                             revenue_risk['revenue_at_risk_percent'],
                             s=revenue_risk['drug_revenue']*20,
                             alpha=0.6, c=revenue_risk['drug_revenue'], 
                             cmap='viridis')
        
        for _, row in revenue_risk.iterrows():
            if row['years_to_cliff'] > 0:  # Only label valid dates
                ax2.annotate(f"{row['ticker']}", 
                            (row['years_to_cliff'], row['revenue_at_risk_percent']),
                            xytext=(5, 5), textcoords='offset points',
                            fontsize=8, alpha=0.8)
        
        ax2.set_xlabel('Years to Patent Cliff')
        ax2.set_ylabel('Revenue at Risk (%)')
        ax2.set_title('Patent Cliff Risk Analysis', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax2, label='Drug Revenue ($B)')
        
        # Plot 3: Company revenue exposure
        company_summary = revenue_risk.groupby('ticker').agg({
            'revenue_at_risk_percent': 'sum',
            'drug_revenue': 'sum'
        }).sort_values('revenue_at_risk_percent', ascending=True)
        
        bars = ax3.barh(range(len(company_summary)), company_summary['revenue_at_risk_percent'])
        ax3.set_yticks(range(len(company_summary)))
        ax3.set_yticklabels(company_summary.index)
        ax3.set_xlabel('Total Revenue at Risk (%)')
        ax3.set_title('Company Revenue Exposure', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # Add value labels on bars
        for i, (ticker, row) in enumerate(company_summary.iterrows()):
            ax3.text(row['revenue_at_risk_percent'] + 0.5, i, 
                    f"{row['revenue_at_risk_percent']:.1f}%", 
                    va='center', fontsize=9)
        
        # Plot 4: Time to cliff distribution
        valid_years = revenue_risk[revenue_risk['years_to_cliff'] > 0]['years_to_cliff']
        ax4.hist(valid_years, bins=10, alpha=0.7, edgecolor='black')
        ax4.set_xlabel('Years to Patent Cliff')
        ax4.set_ylabel('Number of Drugs')
        ax4.set_title('Distribution of Patent Cliff Timing', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def run_full_analysis(self):
        """Run the complete analysis pipeline"""
        print("Starting Patent Cliff Analysis...")
        
        # Load all data
        self.load_data()
        
        # Run analysis
        print("\nAnalyzing patent cliffs...")
        cliff_analysis = self.analyze_patent_cliffs()
        
        print("\nCalculating revenue risk...")
        revenue_risk = self.calculate_revenue_risk(cliff_analysis)
        
        print("\nCalculating company-level risk...")
        company_risk = self.calculate_company_risk(cliff_analysis)
        
        print("\nCalculating portfolio weights...")
        portfolio_weights = self.calculate_portfolio_weights(company_risk)
        
        # Display results
        print("\n" + "="*60)
        print("PATENT CLIFF ANALYSIS RESULTS")
        print("="*60)
        
        print(f"\nAnalyzed {len(cliff_analysis)} drugs from {len(company_risk)} companies")
        
        print("\nCompany-Level Risk Summary:")
        print(company_risk[['ticker', 'company', 'total_drug_revenue_at_risk', 
                           'years_to_earliest_cliff', 'number_of_drugs_at_risk']].round(2))
        
        print("\nPortfolio Weights:")
        weight_summary = portfolio_weights[['ticker', 'company', 'revenue_risk_percent', 
                                          'years_to_earliest_cliff', 'normalized_portfolio_weight']]
        print(weight_summary.round(4))
        
        print(f"\nTotal portfolio weight allocated: {portfolio_weights['normalized_portfolio_weight'].sum():.4f}")
        
        # Create visualizations
        print("\nGenerating visualizations...")
        self.plot_analysis(revenue_risk)
        
        return {
            'cliff_analysis': cliff_analysis,
            'revenue_risk': revenue_risk,
            'company_risk': company_risk,
            'portfolio_weights': portfolio_weights,
            'stock_data': self.stock_data
        }

def main():
    """Main execution function"""
    analyzer = PatentCliffAnalyzer()
    results = analyzer.run_full_analysis()
    return results

if __name__ == "__main__":
    results = main()