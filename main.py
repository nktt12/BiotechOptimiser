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
    'REVLIMID': {'company': 'Bristol Myers', 'ticker': 'BMY', 'revenue_billions': 12.8},
    'KEYTRUDA': {'company': 'Merck', 'ticker': 'MRK', 'revenue_billions': 20.9},
    'HUMIRA': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 21.2},
    'OPDIVO': {'company': 'Bristol Myers', 'ticker': 'BMY', 'revenue_billions': 8.1}
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
patent_cliff_analysis = analyze_patent_cliffs(products, patents, target_drugs)
print(patent_cliff_analysis)

# Calculate revenue at risk
patent_cliff_analysis['months_to_expiry'] = (
    patent_cliff_analysis['latest_patent_expiry'] - datetime.now()
).dt.days / 30

print("\nPatent Cliff Timeline:")
print(patent_cliff_analysis[['drug', 'ticker', 'revenue_billions', 'months_to_expiry']].sort_values('months_to_expiry'))