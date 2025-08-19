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
    'DUPIXENT': {'company': 'Sanofi', 'ticker': 'SNY', 'revenue_billions': 10.9},
    'OZEMPIC': {'company': 'Novo Nordisk', 'ticker': 'NVO', 'revenue_billions': 14.2},
    'WEGOVY': {'company': 'Novo Nordisk', 'ticker': 'NVO', 'revenue_billions': 4.5},
    'TRULICITY': {'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 7.4},
    'IMBRUVICA': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 4.7},
    'VRAYLAR': {'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 4.5},
    'TECFIDERA': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 3.5},
    'SPINRAZA': {'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 2.0},
    'XARELTO': {'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 6.5},
    'EYLEA': {'company': 'Regeneron', 'ticker': 'REGN', 'revenue_billions': 8.1},
    'HERCEPTIN': {'company': 'Roche', 'ticker': 'ROG', 'revenue_billions': 6.4},
    'AVASTIN': {'company': 'Roche', 'ticker': 'ROG', 'revenue_billions': 6.2},
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