import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def load_orange_book_data():
    """Load the three Orange Book data files"""
    
    # Load products data
    products = pd.read_csv('data/products.txt', sep='~', encoding='latin-1')
    
    # Load patent data  
    patents = pd.read_csv('data/patent.txt', sep='~', encoding='latin-1')
    
    # Load exclusivity data
    exclusivity = pd.read_csv('data/exclusivity.txt', sep='~', encoding='latin-1')
    
    return products, patents, exclusivity

# High-revenue drugs to focus on (you'll research these)
target_drugs = {
    'ELIQUIS': {'company': 'Pfizer/BMS', 'ticker': 'PFE', 'revenue_billions': 6.0},
    'REVLIMID': {'company': 'Bristol Myers', 'ticker': 'BMY', 'revenue_billions': 12.8}
}
def analyze_patent_cliffs(products, patents, target_drugs):
    """Find patent expiry dates for target drugs"""
    
    results = []
    
    for drug_name, drug_info in target_drugs.items():
        # Find the drug in products
        drug_products = products[products['Trade_Name'].str.upper().str.contains(drug_name, na=False)]
        
        if not drug_products.empty:
            # Get NDA numbers for this drug
            nda_numbers = drug_products['Appl_No'].unique()
            
            # Find patents for these NDAs
            drug_patents = patents[patents['Appl_No'].isin(nda_numbers)].copy()
            
            # Convert patent expiry dates and find the latest one
            drug_patents['Patent_Expire_Date_Text'] = pd.to_datetime(drug_patents['Patent_Expire_Date_Text'], errors='coerce')
            latest_expiry = drug_patents['Patent_Expire_Date_Text'].max()
            
            results.append({
                'drug': drug_name,
                'company': drug_info['company'],
                'ticker': drug_info['ticker'],
                'revenue_billions': drug_info['revenue_billions'],
                'latest_patent_expiry': latest_expiry,
                'total_patents': len(drug_patents)
            })
    
    return pd.DataFrame(results)

# Run the analysis
products, patents, exclusivity = load_orange_book_data()
cliff_analysis = analyze_patent_cliffs(products, patents, target_drugs)
print(cliff_analysis)

# Calculate revenue at risk
cliff_analysis['months_to_expiry'] = (
    cliff_analysis['latest_patent_expiry'] - datetime.now()
).dt.days / 30
cliff_analysis['days_to_expiry'] = (cliff_analysis['latest_patent_expiry'] - pd.Timestamp.now()).dt.days
cliff_analysis['years_to_expiry'] = cliff_analysis['days_to_expiry'] / 365

#Print output
print("\nPatent Cliff Timeline:")
print(cliff_analysis)

#Download stock data for target drugs
# Get unique tickers (in case of duplicates)
tickers = list(set([drug_info['ticker'] for drug_info in target_drugs.values()]))
stock_data = yf.download(tickers, start='2020-01-01', end='2024-12-31')
print("\nStock data downloaded successfully!")

# Calculate what % of each company's revenue is at patent cliff risk
def calculate_revenue_risk(cliff_analysis):
    """Calculate revenue at risk by company"""
    
    # You'll need total company revenues - let's use rough estimates for now
    company_total_revenues = {
        'PFE': 100.0,  # Pfizer total revenue ~$100B
        'BMY': 46.0    # Bristol Myers ~$46B
    }
    
    risk_analysis = []
    for _, row in cliff_analysis.iterrows():
        ticker = row['ticker']
        drug_revenue = row['revenue_billions']
        total_revenue = company_total_revenues.get(ticker, 0)
        
        risk_percentage = (drug_revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        risk_analysis.append({
            'ticker': ticker,
            'drug': row['drug'],
            'drug_revenue': drug_revenue,
            'total_company_revenue': total_revenue,
            'revenue_at_risk_percent': risk_percentage,
            'years_to_cliff': row['years_to_expiry']
        })
    
    return pd.DataFrame(risk_analysis)

revenue_risk = calculate_revenue_risk(cliff_analysis)
print("\nRevenue at risk analysis:")
print(revenue_risk)