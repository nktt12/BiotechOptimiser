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
    # Your existing drugs...
    'KEYTRUDA': {'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 31.0},
    'MOUNJARO': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 19.0},
    'SKYRIZI': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 13.0},
    'ELIQUIS': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 13.0},
    'DARZALEX': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 13.0},
    'BIKTARVY': {'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 13.0},
    'ZEPBOUND': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 11.0},
    'HUMIRA': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 12.2},
    'REVLIMID': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 12.4},
    'ENBREL': {'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 8.7},
    'REMICADE': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 8.3},
    'RITUXAN': {'company': 'Roche', 'ticker': 'ROG', 'revenue_billions': 7.1},
    'LANTUS': {'company': 'Sanofi', 'ticker': 'SNY', 'revenue_billions': 7.0},
    'COSENTYX': {'company': 'Novartis', 'ticker': 'NVS', 'revenue_billions': 6.1},
    
    # Additional high-revenue drugs:
    'DUPIXENT': {'company': 'Sanofi', 'ticker': 'SNY', 'revenue_billions': 10.9},  # dermatology/asthma
    'OZEMPIC': {'company': 'Novo Nordisk', 'ticker': 'NVO', 'revenue_billions': 14.2},  # diabetes/obesity
    'WEGOVY': {'company': 'Novo Nordisk', 'ticker': 'NVO', 'revenue_billions': 4.5},   # obesity
    'TRULICITY': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 7.4},   # diabetes
    'IMBRUVICA': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 4.7},     # cancer
    'VRAYLAR': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 4.5},       # mental health
    'TECFIDERA': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 3.5},     # multiple sclerosis
    'SPINRAZA': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 2.0},      # rare disease
    'XARELTO': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 6.5},  # anticoagulant
    'EYLEA': {'company': 'Regeneron', 'ticker': 'REGN', 'revenue_billions': 8.1},      # ophthalmology
    'HERCEPTIN': {'company': 'Roche', 'ticker': 'ROG', 'revenue_billions': 6.4},       # cancer
    'AVASTIN': {'company': 'Roche', 'ticker': 'ROG', 'revenue_billions': 6.2},         # cancer
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

def calculate_company_patent_risk(cliff_analysis):
    """Aggregate patent cliff risk at company level"""
    
    company_risk = []
    
    # Group by ticker to handle multiple drugs per company
    for ticker in cliff_analysis['ticker'].unique():
        company_drugs = cliff_analysis[cliff_analysis['ticker'] == ticker]
        
        # Calculate total revenue at risk for this company
        total_drug_revenue = company_drugs['revenue_billions'].sum()
        
        # Find the earliest patent cliff (most urgent risk)
        earliest_cliff = company_drugs['latest_patent_expiry'].min()
        years_to_earliest_cliff = (earliest_cliff - pd.Timestamp.now()).days / 365
        
        # Count number of drugs at risk
        drugs_at_risk = len(company_drugs)
        
        # Get company name (take first one)
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

def calculate_company_portfolio_weights(company_risk, company_total_revenues):
    """Calculate portfolio weights at company level"""
    
    weights = []
    
    for _, row in company_risk.iterrows():
        ticker = row['ticker']
        total_revenue = company_total_revenues.get(ticker, 50.0)  # Default if not found
        
        # Calculate what % of company revenue is at patent cliff risk
        revenue_risk_percent = (row['total_drug_revenue_at_risk'] / total_revenue) * 100
        
        # Time factor: reduce weight as earliest cliff approaches
        time_factor = max(0.1, row['years_to_earliest_cliff'] / 5)
        
        # Risk factor: reduce weight based on total revenue at risk
        risk_factor = max(0.1, 1 - (revenue_risk_percent / 100))
        
        # Diversification penalty: slight penalty for having multiple drugs at risk
        diversification_factor = max(0.8, 1 - (row['number_of_drugs_at_risk'] - 1) * 0.1)
        
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
            'risk_adjusted_weight': risk_adjusted_weight
        })
    
    weights_df = pd.DataFrame(weights)
    
    # Normalize weights to sum to 1
    total_weight = weights_df['risk_adjusted_weight'].sum()
    weights_df['normalized_portfolio_weight'] = weights_df['risk_adjusted_weight'] / total_weight
    
    return weights_df

# Calculate company-level risk first
company_level_risk = calculate_company_patent_risk(cliff_analysis)
print("\nCompany-level patent cliff risk:")
print(company_level_risk)

# Then calculate portfolio weights
portfolio_weights = calculate_company_portfolio_weights(company_level_risk, company_total_revenues)
print("\nCompany-level portfolio weights:")
print(portfolio_weights[['ticker', 'total_revenue_at_risk_billions', 'revenue_risk_percent', 
                        'years_to_earliest_cliff', 'drugs_at_risk', 'normalized_portfolio_weight']])