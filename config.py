# config.py
"""Configuration file for patent cliff optimizer"""

from datetime import datetime

# Data file paths
DATA_PATHS = {
    'products': 'data/products.txt',
    'patents': 'data/patent.txt',
    'exclusivity': 'data/exclusivity.txt'
}

# High-revenue drugs to focus on
TARGET_DRUGS = {
    # Johnson & Johnson - Top 10 drugs
    'DARZALEX': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 13.2},
    'STELARA': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 10.4},
    'XARELTO': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 6.5},
    'TREMFYA': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 4.8},
    'ERLEADA': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 3.6},
    'IMBRUVICA_JNJ': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 3.2},
    'CARVYKTI': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 1.8},
    'RYBREVANT': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 1.2},
    'TECVAYLI': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 0.6},
    'BALVERSA': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 0.4},
    
    # Pfizer - Top 10 drugs
    'ELIQUIS': {'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 13.5},
    'PREVNAR': {'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 6.4},
    'IBRANCE': {'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 5.9},
    'COMIRNATY': {'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 5.6},
    'PAXLOVID': {'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 4.9},
    'VYNDAQEL_FAMILY': {'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 3.9},
    'XTANDI': {'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 2.9},
    'NURTEC_ODT': {'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 1.5},
    'PADCEV': {'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 1.2},
    'LORBRENA': {'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 0.5},
    
    # Merck & Co. - Top 10 drugs
    'KEYTRUDA': {'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 31.0},
    'GARDASIL': {'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 8.6},
    'JANUVIA': {'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 2.3},
    'WINREVAIR': {'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 1.1},
    'PNEUMOVAX': {'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 0.9},
    'BRIDION': {'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 0.8},
    'VAXNEUVANCE': {'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 0.4},
    'RECARBRIO': {'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 0.3},
    'LAGEVRIO': {'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 0.2},
    'ZOSTAVAX': {'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 0.1},
    
    # AbbVie - Top 10 drugs
    'SKYRIZI': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 13.7},
    'HUMIRA': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 8.9},
    'RINVOQ': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 6.0},
    'IMBRUVICA': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 4.7},
    'VRAYLAR': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 3.3},
    'BOTOX_THERAPEUTIC': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 3.3},
    'VENCLEXTA': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 2.8},
    'UBRELVY': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 1.2},
    'ELAHERE': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 0.8},
    'QULIPTA': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 0.6},
    
    # Bristol Myers Squibb - Top 10 drugs
    'ELIQUIS_BMS': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 13.5},
    'OPDIVO': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 9.1},
    'REVLIMID': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 3.7},
    'POMALYST': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 2.6},
    'YERVOY': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 2.5},
    'SPRYCEL': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 2.1},
    'ABRAXANE': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 1.5},
    'BREYANZI': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 0.9},
    'SOTYKTU': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 0.3},
    'COBENFY': {'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 0.1},
    
    # Amgen - Top 10 drugs
    'PROLIA': {'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 4.4},
    'REPATHA': {'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 2.6},
    'XGEVA': {'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 2.1},
    'ENBREL': {'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 2.0},
    'EVENITY': {'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 1.8},
    'OTEZLA': {'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 1.7},
    'BLINCYTO': {'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 1.5},
    'KYPROLIS': {'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 1.5},
    'NPLATE': {'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 1.4},
    'TEZSPIRE': {'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 1.1},
    
    # Eli Lilly - Top 10 drugs
    'MOUNJARO': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 20.8},
    'ZEPBOUND': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 13.5},
    'TRULICITY': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 7.4},
    'VERZENIO': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 4.6},
    'JARDIANCE': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 2.9},
    'HUMALOG': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 2.8},
    'TALTZ': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 2.3},
    'EMGALITY': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 1.0},
    'OLUMIANT': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 0.8},
    'CYRAMZA': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 0.7},
    
    # Gilead Sciences - Top 10 drugs
    'BIKTARVY': {'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 13.4},
    'DESCOVY': {'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 4.8},
    'GENVOYA': {'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 3.2},
    'TRUVADA': {'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 2.1},
    'ODEFSEY': {'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 1.8},
    'STRIBILD': {'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 0.9},
    'VEMLIDY': {'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 0.8},
    'COMPLERA': {'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 0.6},
    'ATRIPLA': {'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 0.4},
    'SUNLENCA': {'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 0.3},
    
    # Biogen - Top 10 drugs
    'TECFIDERA': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 1.9},
    'SPINRAZA': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 1.7},
    'TYSABRI': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 1.6},
    'AVONEX': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 0.8},
    'SKYCLARYS': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 0.5},
    'PLEGRIDY': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 0.4},
    'LEQEMBI': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 0.4},
    'FAMPYRA': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 0.3},
    'FUMADERM': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 0.2},
    'ZINBRYTA': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 0.1},
    
    # Moderna - Top 10 products (limited commercial portfolio, includes pipeline)
    'SPIKEVAX': {'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 0.8},
    'MRESVIA': {'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 0.008},
    'CMV_VACCINE': {'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 0.0},
    'FLU_VACCINE': {'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 0.0},
    'RSV_VACCINE_PEDS': {'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 0.0},
    'ZIKA_VACCINE': {'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 0.0},
    'EBV_VACCINE': {'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 0.0},
    'MPOX_VACCINE': {'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 0.0},
    'HIV_VACCINE': {'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 0.0},
    'CANCER_VACCINE': {'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 0.0},
}

# Backtesting parameters
BACKTEST_CONFIG = {
    'start_date': '2020-01-01',
    'end_date': '2024-12-31',
    'rebalance_frequency': 'quarterly',  # 'monthly', 'quarterly', 'annually'
    'initial_capital': 100000,  # $100k
    'transaction_cost': 0.001,  # 0.1% transaction cost
    'min_weight': 0.05,  # Minimum 5% allocation
    'max_weight': 0.20,  # Maximum 20% allocation
    'benchmark_ticker': 'SPY',  # S&P 500 benchmark
}

# Risk model parameters
RISK_PARAMETERS = {
    'lookback_window': 252,  # 1 year for volatility calculation
    'min_time_to_cliff': 0.5,  # Minimum 6 months to patent cliff
    'max_revenue_risk_percent': 100,  # Maximum 30% of company revenue at risk
    'diversification_penalty': 0.1,  # 10% penalty per additional drug at risk
}

# Analysis parameters
ANALYSIS_CONFIG = {
    'stock_data_start': '2020-01-01',
    'stock_data_end': '2024-12-31',
    'plot_style': 'seaborn-v0_8',
    'figure_size': (12, 10),
}