# config.py
"""Configuration file for patent cliff optimizer"""

from datetime import datetime

# Data file paths
DATA_PATHS = {
    'products': 'data/products.txt',
    'patents': 'data/patent.txt',
    'exclusivity': 'data/exclusivity.txt'
}

# High-revenue drugs to focus on (for current analysis)
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

# BACKTEST-SPECIFIC DRUG LIST (for historical backtesting 2020-2024)
BACKTEST_TARGET_DRUGS = {
    # =============================================================================
    # DRUGS THAT EXPIRED DURING 2020-2024 (50 drugs)
    # =============================================================================
    
    # Original 10 from your list
    'PLAVIX': {
        'company': 'Bristol Myers Squibb', 
        'ticker': 'BMY', 
        'revenue_billions': 6.8,
        'patent_expiry': '2020-05-17',
        'status': 'expired_in_period'
    },
    'HUMIRA_BACKTEST': {
        'company': 'AbbVie', 
        'ticker': 'ABBV', 
        'revenue_billions': 18.5,
        'patent_expiry': '2023-01-31',
        'status': 'expired_in_period'
    },
    'VYVANSE': {
        'company': 'Takeda', 
        'ticker': 'TAK', 
        'revenue_billions': 2.5,
        'patent_expiry': '2023-02-24',
        'status': 'expired_in_period'
    },
    'COPAXONE': {
        'company': 'Teva', 
        'ticker': 'TEVA', 
        'revenue_billions': 1.8,
        'patent_expiry': '2020-09-15',
        'status': 'expired_in_period'
    },
    'REVLIMID_BACKTEST': {
        'company': 'Bristol Myers Squibb', 
        'ticker': 'BMY', 
        'revenue_billions': 12.1,
        'patent_expiry': '2022-10-31',
        'status': 'expired_in_period'
    },
    'GLEEVEC': {
        'company': 'Novartis', 
        'ticker': 'NVS', 
        'revenue_billions': 4.7,
        'patent_expiry': '2021-07-30',
        'status': 'expired_in_period'
    },
    'CIALIS': {
        'company': 'Eli Lilly', 
        'ticker': 'LLY', 
        'revenue_billions': 1.4,
        'patent_expiry': '2020-10-06',
        'status': 'expired_in_period'
    },
    'AVASTIN': {
        'company': 'Roche', 
        'ticker': 'RHHBY', 
        'revenue_billions': 7.1,
        'patent_expiry': '2024-02-26',
        'status': 'expired_in_period'
    },
    'BOTOX_BACKTEST': {
        'company': 'AbbVie', 
        'ticker': 'ABBV', 
        'revenue_billions': 4.9,
        'patent_expiry': '2022-12-15',
        'status': 'expired_in_period'
    },
    'REMICADE': {
        'company': 'Johnson & Johnson', 
        'ticker': 'JNJ', 
        'revenue_billions': 4.2,
        'patent_expiry': '2021-09-23',
        'status': 'expired_in_period'
    },
    
    # Additional 40 drugs expired 2020-2024
    'NEXIUM': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 3.9,
        'patent_expiry': '2020-05-27',
        'status': 'expired_in_period'
    },
    'RITUXAN': {
        'company': 'Roche', 
        'ticker': 'RHHBY', 
        'revenue_billions': 5.8,
        'patent_expiry': '2020-11-26',
        'status': 'expired_in_period'
    },
    'HERCEPTIN': {
        'company': 'Roche', 
        'ticker': 'RHHBY', 
        'revenue_billions': 6.4,
        'patent_expiry': '2020-06-30',
        'status': 'expired_in_period'
    },
    'ABILIFY_MAINTENA': {
        'company': 'Otsuka', 
        'ticker': 'OTSKF', 
        'revenue_billions': 2.1,
        'patent_expiry': '2024-04-13',
        'status': 'expired_in_period'
    },
    'VICTOZA': {
        'company': 'Novo Nordisk', 
        'ticker': 'NVO', 
        'revenue_billions': 3.5,
        'patent_expiry': '2024-01-02',
        'status': 'expired_in_period'
    },
    'LYRICA': {
        'company': 'Pfizer', 
        'ticker': 'PFE', 
        'revenue_billions': 5.1,
        'patent_expiry': '2020-12-30',
        'status': 'expired_in_period'
    },
    'XOLAIR': {
        'company': 'Roche/Novartis', 
        'ticker': 'RHHBY', 
        'revenue_billions': 2.8,
        'patent_expiry': '2020-06-20',
        'status': 'expired_in_period'
    },
    'CRESTOR': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 3.2,
        'patent_expiry': '2020-07-08',
        'status': 'expired_in_period'
    },
    'SYMBICORT': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 2.7,
        'patent_expiry': '2021-04-23',
        'status': 'expired_in_period'
    },
    'MYRBETRIQ': {
        'company': 'Astellas', 
        'ticker': 'ALPMY', 
        'revenue_billions': 2.3,
        'patent_expiry': '2024-07-21',
        'status': 'expired_in_period'
    },
    'TECFIDERA': {
        'company': 'Biogen', 
        'ticker': 'BIIB', 
        'revenue_billions': 4.3,
        'patent_expiry': '2020-04-30',
        'status': 'expired_in_period'
    },
    'LINZESS': {
        'company': 'AbbVie/Ironwood', 
        'ticker': 'ABBV', 
        'revenue_billions': 1.8,
        'patent_expiry': '2024-08-30',
        'status': 'expired_in_period'
    },
    'JANUVIA': {
        'company': 'Merck & Co.', 
        'ticker': 'MRK', 
        'revenue_billions': 5.3,
        'patent_expiry': '2022-03-03',
        'status': 'expired_in_period'
    },
    'SYNAGIS': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 1.2,
        'patent_expiry': '2020-10-01',
        'status': 'expired_in_period'
    },
    'NASONEX': {
        'company': 'Merck & Co.', 
        'ticker': 'MRK', 
        'revenue_billions': 1.5,
        'patent_expiry': '2020-09-24',
        'status': 'expired_in_period'
    },
    'ARIMIDEX': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 0.9,
        'patent_expiry': '2020-12-17',
        'status': 'expired_in_period'
    },
    'LUCENTIS': {
        'company': 'Roche/Novartis', 
        'ticker': 'RHHBY', 
        'revenue_billions': 3.6,
        'patent_expiry': '2020-06-30',
        'status': 'expired_in_period'
    },
    'FLOVENT': {
        'company': 'GlaxoSmithKline', 
        'ticker': 'GSK', 
        'revenue_billions': 2.1,
        'patent_expiry': '2021-10-27',
        'status': 'expired_in_period'
    },
    'PREZISTA': {
        'company': 'Johnson & Johnson', 
        'ticker': 'JNJ', 
        'revenue_billions': 1.7,
        'patent_expiry': '2020-06-23',
        'status': 'expired_in_period'
    },
    'ADVAIR_DISKUS': {
        'company': 'GlaxoSmithKline', 
        'ticker': 'GSK', 
        'revenue_billions': 2.9,
        'patent_expiry': '2020-08-13',
        'status': 'expired_in_period'
    },
    'NEUPOGEN': {
        'company': 'Amgen', 
        'ticker': 'AMGN', 
        'revenue_billions': 1.8,
        'patent_expiry': '2020-12-13',
        'status': 'expired_in_period'
    },
    'ATRIPLA': {
        'company': 'Gilead Sciences', 
        'ticker': 'GILD', 
        'revenue_billions': 2.4,
        'patent_expiry': '2021-07-12',
        'status': 'expired_in_period'
    },
    'BRILINTA': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 1.6,
        'patent_expiry': '2024-05-20',
        'status': 'expired_in_period'
    },
    'SENSIPAR': {
        'company': 'Amgen', 
        'ticker': 'AMGN', 
        'revenue_billions': 1.3,
        'patent_expiry': '2021-03-03',
        'status': 'expired_in_period'
    },
    'ZYTIGA': {
        'company': 'Johnson & Johnson', 
        'ticker': 'JNJ', 
        'revenue_billions': 3.8,
        'patent_expiry': '2022-04-05',
        'status': 'expired_in_period'
    },
    'EPOGEN': {
        'company': 'Amgen', 
        'ticker': 'AMGN', 
        'revenue_billions': 1.9,
        'patent_expiry': '2020-06-11',
        'status': 'expired_in_period'
    },
    'HUMIRA_EUROPE': {
        'company': 'AbbVie', 
        'ticker': 'ABBV', 
        'revenue_billions': 4.2,
        'patent_expiry': '2020-10-16',
        'status': 'expired_in_period'
    },
    'GEODON': {
        'company': 'Pfizer', 
        'ticker': 'PFE', 
        'revenue_billions': 1.1,
        'patent_expiry': '2021-02-06',
        'status': 'expired_in_period'
    },
    'MAXALT': {
        'company': 'Merck & Co.', 
        'ticker': 'MRK', 
        'revenue_billions': 0.8,
        'patent_expiry': '2020-12-06',
        'status': 'expired_in_period'
    },
    'XYZAL': {
        'company': 'Sanofi', 
        'ticker': 'SNY', 
        'revenue_billions': 0.7,
        'patent_expiry': '2020-05-26',
        'status': 'expired_in_period'
    },
    'BONIVA': {
        'company': 'Roche', 
        'ticker': 'RHHBY', 
        'revenue_billions': 0.6,
        'patent_expiry': '2020-03-29',
        'status': 'expired_in_period'
    },
    'NAMENDA': {
        'company': 'Allergan', 
        'ticker': 'ABBV', 
        'revenue_billions': 1.5,
        'patent_expiry': '2021-07-11',
        'status': 'expired_in_period'
    },
    'TARCEVA': {
        'company': 'Roche', 
        'ticker': 'RHHBY', 
        'revenue_billions': 1.2,
        'patent_expiry': '2020-11-17',
        'status': 'expired_in_period'
    },
    'PEGASYS': {
        'company': 'Roche', 
        'ticker': 'RHHBY', 
        'revenue_billions': 0.9,
        'patent_expiry': '2020-12-10',
        'status': 'expired_in_period'
    },
    'COPAXONE_GENERIC': {
        'company': 'Teva', 
        'ticker': 'TEVA', 
        'revenue_billions': 1.1,
        'patent_expiry': '2021-05-24',
        'status': 'expired_in_period'
    },
    'SYMBICORT_HFA': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 1.6,
        'patent_expiry': '2022-09-07',
        'status': 'expired_in_period'
    },
    'SANDOSTATIN': {
        'company': 'Novartis', 
        'ticker': 'NVS', 
        'revenue_billions': 1.8,
        'patent_expiry': '2021-03-09',
        'status': 'expired_in_period'
    },
    'KALETRA': {
        'company': 'AbbVie', 
        'ticker': 'ABBV', 
        'revenue_billions': 1.3,
        'patent_expiry': '2020-09-17',
        'status': 'expired_in_period'
    },
    'HUMALOG_MIX': {
        'company': 'Eli Lilly', 
        'ticker': 'LLY', 
        'revenue_billions': 2.2,
        'patent_expiry': '2023-12-11',
        'status': 'expired_in_period'
    },
    'ZIAGEN': {
        'company': 'ViiV Healthcare/GSK', 
        'ticker': 'GSK', 
        'revenue_billions': 0.8,
        'patent_expiry': '2020-07-14',
        'status': 'expired_in_period'
    },
    
    # =============================================================================
    # DRUGS STILL PROTECTED (50 drugs) - Higher weights expected
    # =============================================================================
    
    # Original 10 from your list
    'KEYTRUDA_BACKTEST': {
        'company': 'Merck & Co.', 
        'ticker': 'MRK', 
        'revenue_billions': 31.0,
        'patent_expiry': '2028-09-30',
        'status': 'still_protected'
    },
    'OPDIVO_BACKTEST': {
        'company': 'Bristol Myers Squibb', 
        'ticker': 'BMY', 
        'revenue_billions': 9.1,
        'patent_expiry': '2026-06-30',
        'status': 'still_protected'
    },
    'ELIQUIS_BACKTEST': {
        'company': 'Bristol Myers Squibb', 
        'ticker': 'BMY', 
        'revenue_billions': 13.5,
        'patent_expiry': '2026-12-28',
        'status': 'still_protected'
    },
    'SKYRIZI_BACKTEST': {
        'company': 'AbbVie', 
        'ticker': 'ABBV', 
        'revenue_billions': 13.7,
        'patent_expiry': '2029-04-15',
        'status': 'still_protected'
    },
    'TRULICITY_BACKTEST': {
        'company': 'Eli Lilly', 
        'ticker': 'LLY', 
        'revenue_billions': 7.4,
        'patent_expiry': '2027-03-18',
        'status': 'still_protected'
    },
    'STELARA_BACKTEST': {
        'company': 'Johnson & Johnson', 
        'ticker': 'JNJ', 
        'revenue_billions': 10.4,
        'patent_expiry': '2025-09-23',
        'status': 'still_protected'
    },
    'XARELTO_BACKTEST': {
        'company': 'Johnson & Johnson', 
        'ticker': 'JNJ', 
        'revenue_billions': 6.5,
        'patent_expiry': '2025-07-15',
        'status': 'still_protected'
    },
    'IBRANCE_BACKTEST': {
        'company': 'Pfizer', 
        'ticker': 'PFE', 
        'revenue_billions': 5.9,
        'patent_expiry': '2027-11-30',
        'status': 'still_protected'
    },
    'REPATHA_BACKTEST': {
        'company': 'Amgen', 
        'ticker': 'AMGN', 
        'revenue_billions': 2.6,
        'patent_expiry': '2029-08-27',
        'status': 'still_protected'
    },
    'BIKTARVY_BACKTEST': {
        'company': 'Gilead Sciences', 
        'ticker': 'GILD', 
        'revenue_billions': 13.4,
        'patent_expiry': '2030-02-28',
        'status': 'still_protected'
    },
    
    # Additional 40 drugs still protected
    'OZEMPIC': {
        'company': 'Novo Nordisk', 
        'ticker': 'NVO', 
        'revenue_billions': 21.1,
        'patent_expiry': '2031-12-05',
        'status': 'still_protected'
    },
    'WEGOVY': {
        'company': 'Novo Nordisk', 
        'ticker': 'NVO', 
        'revenue_billions': 4.5,
        'patent_expiry': '2031-12-05',
        'status': 'still_protected'
    },
    'DUPIXENT': {
        'company': 'Sanofi/Regeneron', 
        'ticker': 'SNY', 
        'revenue_billions': 11.6,
        'patent_expiry': '2031-03-28',
        'status': 'still_protected'
    },
    'SPINRAZA': {
        'company': 'Biogen', 
        'ticker': 'BIIB', 
        'revenue_billions': 2.0,
        'patent_expiry': '2032-02-25',
        'status': 'still_protected'
    },
    'EYLEA': {
        'company': 'Regeneron/Bayer', 
        'ticker': 'REGN', 
        'revenue_billions': 6.2,
        'patent_expiry': '2030-11-18',
        'status': 'still_protected'
    },
    'IMBRUVICA': {
        'company': 'AbbVie', 
        'ticker': 'ABBV', 
        'revenue_billions': 4.8,
        'patent_expiry': '2027-07-12',
        'status': 'still_protected'
    },
    'OCREVUS': {
        'company': 'Roche', 
        'ticker': 'RHHBY', 
        'revenue_billions': 6.2,
        'patent_expiry': '2030-03-28',
        'status': 'still_protected'
    },
    'VEKLURY': {
        'company': 'Gilead Sciences', 
        'ticker': 'GILD', 
        'revenue_billions': 2.8,
        'patent_expiry': '2031-05-01',
        'status': 'still_protected'
    },
    'SPIKEVAX': {
        'company': 'Moderna', 
        'ticker': 'MRNA', 
        'revenue_billions': 18.4,
        'patent_expiry': '2036-10-21',
        'status': 'still_protected'
    },
    'COMIRNATY': {
        'company': 'Pfizer/BioNTech', 
        'ticker': 'PFE', 
        'revenue_billions': 37.8,
        'patent_expiry': '2033-12-13',
        'status': 'still_protected'
    },
    'PAXLOVID': {
        'company': 'Pfizer', 
        'ticker': 'PFE', 
        'revenue_billions': 18.9,
        'patent_expiry': '2034-12-13',
        'status': 'still_protected'
    },
    'TECENTRIQ': {
        'company': 'Roche', 
        'ticker': 'RHHBY', 
        'revenue_billions': 4.1,
        'patent_expiry': '2029-10-02',
        'status': 'still_protected'
    },
    'YERVOY': {
        'company': 'Bristol Myers Squibb', 
        'ticker': 'BMY', 
        'revenue_billions': 1.6,
        'patent_expiry': '2026-03-25',
        'status': 'still_protected'
    },
    'TAGRISSO': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 5.8,
        'patent_expiry': '2030-11-13',
        'status': 'still_protected'
    },
    'LYNPARZA': {
        'company': 'AstraZeneca/Merck', 
        'ticker': 'AZN', 
        'revenue_billions': 2.9,
        'patent_expiry': '2032-01-13',
        'status': 'still_protected'
    },
    'FARXIGA': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 4.5,
        'patent_expiry': '2025-11-22',
        'status': 'still_protected'
    },
    'JARDIANCE': {
        'company': 'Boehringer Ingelheim', 
        'ticker': 'BIRGY', 
        'revenue_billions': 6.7,
        'patent_expiry': '2025-08-02',
        'status': 'still_protected'
    },
    'MOUNJARO': {
        'company': 'Eli Lilly', 
        'ticker': 'LLY', 
        'revenue_billions': 5.2,
        'patent_expiry': '2034-07-25',
        'status': 'still_protected'
    },
    'ZEPBOUND': {
        'company': 'Eli Lilly', 
        'ticker': 'LLY', 
        'revenue_billions': 1.2,
        'patent_expiry': '2034-07-25',
        'status': 'still_protected'
    },
    'VERZENIO': {
        'company': 'Eli Lilly', 
        'ticker': 'LLY', 
        'revenue_billions': 3.4,
        'patent_expiry': '2026-09-29',
        'status': 'still_protected'
    },
    'OLUMIANT': {
        'company': 'Eli Lilly', 
        'ticker': 'LLY', 
        'revenue_billions': 0.9,
        'patent_expiry': '2029-05-23',
        'status': 'still_protected'
    },
    'RINVOQ': {
        'company': 'AbbVie', 
        'ticker': 'ABBV', 
        'revenue_billions': 5.4,
        'patent_expiry': '2031-02-18',
        'status': 'still_protected'
    },
    'VENCLYXTO': {
        'company': 'AbbVie/Roche', 
        'ticker': 'ABBV', 
        'revenue_billions': 1.9,
        'patent_expiry': '2027-12-19',
        'status': 'still_protected'
    },
    'MAVYRET': {
        'company': 'AbbVie', 
        'ticker': 'ABBV', 
        'revenue_billions': 4.1,
        'patent_expiry': '2030-08-03',
        'status': 'still_protected'
    },
    'CALQUENCE': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 2.3,
        'patent_expiry': '2030-10-21',
        'status': 'still_protected'
    },
    'ENHERTU': {
        'company': 'AstraZeneca/Daiichi Sankyo', 
        'ticker': 'AZN', 
        'revenue_billions': 2.0,
        'patent_expiry': '2031-12-25',
        'status': 'still_protected'
    },
    'IMFINZI': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 2.7,
        'patent_expiry': '2029-05-13',
        'status': 'still_protected'
    },
    'SOLIRIS': {
        'company': 'Alexion/AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 4.1,
        'patent_expiry': '2027-03-16',
        'status': 'still_protected'
    },
    'ULTOMIRIS': {
        'company': 'Alexion/AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 1.9,
        'patent_expiry': '2031-12-21',
        'status': 'still_protected'
    },
    'BREZTRI': {
        'company': 'AstraZeneca', 
        'ticker': 'AZN', 
        'revenue_billions': 1.4,
        'patent_expiry': '2030-04-25',
        'status': 'still_protected'
    },
    'TRELEGY': {
        'company': 'GlaxoSmithKline', 
        'ticker': 'GSK', 
        'revenue_billions': 2.1,
        'patent_expiry': '2030-09-13',
        'status': 'still_protected'
    },
    'NUCALA': {
        'company': 'GlaxoSmithKline', 
        'ticker': 'GSK', 
        'revenue_billions': 1.8,
        'patent_expiry': '2028-11-04',
        'status': 'still_protected'
    },
    'BENLYSTA': {
        'company': 'GlaxoSmithKline', 
        'ticker': 'GSK', 
        'revenue_billions': 0.9,
        'patent_expiry': '2026-03-09',
        'status': 'still_protected'
    },
    'SHINGRIX': {
        'company': 'GlaxoSmithKline', 
        'ticker': 'GSK', 
        'revenue_billions': 3.2,
        'patent_expiry': '2032-10-20',
        'status': 'still_protected'
    },
    'DESCOVY': {
        'company': 'Gilead Sciences', 
        'ticker': 'GILD', 
        'revenue_billions': 5.9,
        'patent_expiry': '2030-04-02',
        'status': 'still_protected'
    },
    'TRODELVY': {
        'company': 'Gilead Sciences', 
        'ticker': 'GILD', 
        'revenue_billions': 1.0,
        'patent_expiry': '2033-04-13',
        'status': 'still_protected'
    }
}


# Backtesting parameters
BACKTEST_CONFIG = {
    'start_date': '2020-01-01',
    'end_date': '2024-12-31',
    'rebalance_frequency': 'quarterly',  # 'monthly', 'quarterly', 'annually'
    'initial_capital': 100000,  # $100k
    'transaction_cost': 0.001,  # 0.1% transaction cost
    'min_weight': 0.02,  # Minimum 2% allocation
    'max_weight': 0.15,  # Maximum 15% allocation per position
    'benchmark_ticker': 'SPY',  # S&P 500 benchmark
    'use_backtest_drugs': True,  # Flag to use backtest-specific drug list
}

# Risk model parameters
RISK_PARAMETERS = {
    'lookback_window': 252,  # 1 year for volatility calculation
    'min_time_to_cliff': 0.5,  # Minimum 6 months to patent cliff
    'max_revenue_risk_percent': 100,  # Maximum 30% of company revenue at risk
    'diversification_penalty': 0.1,  # 10% penalty per additional drug at risk
}

# Risk model parameters for backtesting
BACKTEST_RISK_PARAMETERS = {
    'lookback_window': 252,  # 1 year for volatility calculation
    'min_time_to_cliff': 0.25,  # Minimum 3 months to patent cliff
    'cliff_horizon_years': 2.0,  # Start reducing weight 2 years before cliff
    'expired_drug_weight': 0.0,  # No weight for drugs that have already expired
    'diversification_penalty': 0.05,  # 5% penalty per additional drug at risk per company
    'risk_decay_factor': 0.5,  # How aggressively to reduce weight as cliff approaches
}

# Analysis parameters
ANALYSIS_CONFIG = {
    'stock_data_start': '2020-01-01',
    'stock_data_end': '2024-12-31',
    'plot_style': 'seaborn-v0_8',
    'figure_size': (12, 10),
}