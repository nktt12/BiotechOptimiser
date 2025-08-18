import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

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
# --- NEW PART: Get latest total revenues from yfinance ---
def get_latest_revenues(tickers):
    revenues = {}
    for ticker in tickers:
        t = yf.Ticker(ticker)
        try:
            # Pull annual financials
            financials = t.financials
            
            # Get "Total Revenue" if available
            if "Total Revenue" in financials.index:
                latest_revenue = financials.loc["Total Revenue"].iloc[0]
                revenues[ticker] = latest_revenue / 1e9  # convert to billions
            else:
                revenues[ticker] = None
        except Exception as e:
            print(f"Could not fetch revenue for {ticker}: {e}")
            revenues[ticker] = None
    return revenues

company_total_revenues = get_latest_revenues(tickers)
print("\nFetched total revenues (billions):", company_total_revenues)

# Calculate what % of each company's revenue is at patent cliff risk
def calculate_revenue_risk(cliff_analysis, company_total_revenues):
    """Calculate revenue at risk by company"""
    
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

revenue_risk = calculate_revenue_risk(cliff_analysis, company_total_revenues)
print("\nRevenue at risk analysis:")
print(revenue_risk)

# Plot stock performance vs patent cliff timing
def plot_stock_vs_patent_risk(stock_data, revenue_risk):
    """Plot stock performance colored by patent cliff risk"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Stock prices over time
    for ticker in revenue_risk['ticker'].unique():
        if ('Close', ticker) in stock_data.columns:
            ax1.plot(stock_data.index, stock_data[('Close', ticker)], 
                    label=f"{ticker}", linewidth=2)
    
    ax1.set_title('Stock Prices Over Time')
    ax1.set_ylabel('Stock Price ($)')
    ax1.legend()
    ax1.grid(True)
    
    # Plot 2: Risk vs Time to Patent Cliff
    scatter = ax2.scatter(revenue_risk['years_to_cliff'], 
                         revenue_risk['revenue_at_risk_percent'],
                         s=revenue_risk['drug_revenue']*50,  # Size by revenue
                         alpha=0.7)
    
    for _, row in revenue_risk.iterrows():
        ax2.annotate(f"{row['ticker']}\n{row['drug']}", 
                    (row['years_to_cliff'], row['revenue_at_risk_percent']))
    
    ax2.set_xlabel('Years to Patent Cliff')
    ax2.set_ylabel('Revenue at Risk (%)')
    ax2.set_title('Patent Cliff Risk Analysis')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

plot_stock_vs_patent_risk(stock_data, revenue_risk)

def calculate_patent_adjusted_weights(revenue_risk):
    """Calculate portfolio weights adjusted for patent cliff risk"""
    
    weights = []
    for _, row in revenue_risk.iterrows():
        # Reduce weight as patent cliff approaches and risk increases
        time_factor = max(0.1, row['years_to_cliff'] / 5)  # Normalize to 5 years
        #Don't want to weight it to 0 so have the 0.1
        risk_factor = max(0.1, 1 - (row['revenue_at_risk_percent'] / 100))
        
        adjusted_weight = time_factor * risk_factor
        weights.append({
            'ticker': row['ticker'],
            'base_weight': 0.5,  # Equal weight starting point
            'risk_adjusted_weight': adjusted_weight,
            'recommendation': 'Underweight' if adjusted_weight < 0.5 else 'Overweight'
        })
    
    weights_df = pd.DataFrame(weights)
    
    # Normalize weights to sum to 1
    total_weight = weights_df['risk_adjusted_weight'].sum()
    weights_df['normalized_weight'] = weights_df['risk_adjusted_weight'] / total_weight
    
    return weights_df

portfolio_weights = calculate_patent_adjusted_weights(revenue_risk)
print("\nPatent-adjusted portfolio weights:")
print(portfolio_weights)