# config.py - Enhanced with comprehensive drug lists for backtesting
"""Configuration file for patent cliff optimizer with expanded drug datasets"""

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
}

# NEW DRUG LAUNCHES (2020-2025) - 50 Top Performers
NEW_DRUG_LAUNCHES = {
    # Blockbuster Launches (>$5B revenue potential)
    'MOUNJARO_LAUNCH': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 20.8,
        'launch_date': '2022-05-13', 'patent_expiry': '2034-07-25',
        'indication': 'Type 2 Diabetes/Weight Management', 'peak_sales_estimate': 25.0,
        'status': 'blockbuster'
    },
    'ZEPBOUND_LAUNCH': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 13.5,
        'launch_date': '2023-11-08', 'patent_expiry': '2034-07-25',
        'indication': 'Chronic Weight Management', 'peak_sales_estimate': 20.0,
        'status': 'blockbuster'
    },
    'COMIRNATY_LAUNCH': {
        'company': 'Pfizer/BioNTech', 'ticker': 'PFE', 'revenue_billions': 37.8,
        'launch_date': '2020-12-11', 'patent_expiry': '2033-12-13',
        'indication': 'COVID-19 Vaccine', 'peak_sales_estimate': 45.0,
        'status': 'pandemic_blockbuster'
    },
    'SPIKEVAX_LAUNCH': {
        'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 18.4,
        'launch_date': '2020-12-18', 'patent_expiry': '2036-10-21',
        'indication': 'COVID-19 Vaccine', 'peak_sales_estimate': 20.0,
        'status': 'pandemic_blockbuster'
    },
    'PAXLOVID_LAUNCH': {
        'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 18.9,
        'launch_date': '2021-12-22', 'patent_expiry': '2034-12-13',
        'indication': 'COVID-19 Treatment', 'peak_sales_estimate': 22.0,
        'status': 'pandemic_blockbuster'
    },
    'SKYRIZI_EXPANSION': {
        'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 13.7,
        'launch_date': '2020-06-01', 'patent_expiry': '2029-04-15',
        'indication': 'Psoriasis/Psoriatic Arthritis', 'peak_sales_estimate': 16.0,
        'status': 'blockbuster'
    },
    'DUPIXENT_EXPANSION': {
        'company': 'Sanofi/Regeneron', 'ticker': 'SNY', 'revenue_billions': 11.6,
        'launch_date': '2020-03-01', 'patent_expiry': '2031-03-28',
        'indication': 'Atopic Dermatitis/Asthma', 'peak_sales_estimate': 15.0,
        'status': 'expanding_blockbuster'
    },
    'WEGOVY_LAUNCH': {
        'company': 'Novo Nordisk', 'ticker': 'NVO', 'revenue_billions': 4.5,
        'launch_date': '2021-06-04', 'patent_expiry': '2031-12-05',
        'indication': 'Chronic Weight Management', 'peak_sales_estimate': 15.0,
        'status': 'blockbuster'
    },
    'LEQEMBI_LAUNCH': {
        'company': 'Biogen/Eisai', 'ticker': 'BIIB', 'revenue_billions': 0.4,
        'launch_date': '2023-01-06', 'patent_expiry': '2027-12-09',
        'indication': 'Alzheimer\'s Disease', 'peak_sales_estimate': 10.0,
        'status': 'breakthrough_therapy'
    },
    'ADUHLEM_LAUNCH': {
        'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 0.0,
        'launch_date': '2021-06-07', 'patent_expiry': '2031-06-07',
        'indication': 'Alzheimer\'s Disease', 'peak_sales_estimate': 8.0,
        'status': 'controversial_withdrawal'
    },

    # Major Immunology/Oncology Launches
    'RINVOQ_EXPANSION': {
        'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 6.0,
        'launch_date': '2020-08-01', 'patent_expiry': '2031-02-18',
        'indication': 'Rheumatoid Arthritis/UC/AD', 'peak_sales_estimate': 8.0,
        'status': 'growing_blockbuster'
    },
    'VRAYLAR_EXPANSION': {
        'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 3.3,
        'launch_date': '2020-05-15', 'patent_expiry': '2029-05-15',
        'indication': 'Bipolar/Schizophrenia', 'peak_sales_estimate': 5.0,
        'status': 'growing_blockbuster'
    },
    'BREYANZI_LAUNCH': {
        'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 0.9,
        'launch_date': '2021-02-05', 'patent_expiry': '2033-02-05',
        'indication': 'B-cell Lymphoma', 'peak_sales_estimate': 3.0,
        'status': 'car_t_therapy'
    },
    'ABECMA_LAUNCH': {
        'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 0.4,
        'launch_date': '2021-03-26', 'patent_expiry': '2033-03-26',
        'indication': 'Multiple Myeloma', 'peak_sales_estimate': 2.0,
        'status': 'car_t_therapy'
    },
    'CARVYKTI_LAUNCH': {
        'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 1.8,
        'launch_date': '2022-02-28', 'patent_expiry': '2034-02-28',
        'indication': 'Multiple Myeloma', 'peak_sales_estimate': 4.0,
        'status': 'car_t_therapy'
    },
    'TECVAYLI_LAUNCH': {
        'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 0.6,
        'launch_date': '2022-10-31', 'patent_expiry': '2034-10-31',
        'indication': 'Multiple Myeloma', 'peak_sales_estimate': 3.0,
        'status': 'bispecific_antibody'
    },
    'RYBREVANT_LAUNCH': {
        'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 1.2,
        'launch_date': '2021-05-21', 'patent_expiry': '2033-05-21',
        'indication': 'Non-Small Cell Lung Cancer', 'peak_sales_estimate': 4.0,
        'status': 'targeted_therapy'
    },
    'TREMFYA_EXPANSION': {
        'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 4.8,
        'launch_date': '2020-07-01', 'patent_expiry': '2030-07-01',
        'indication': 'Psoriasis/Ulcerative Colitis', 'peak_sales_estimate': 6.0,
        'status': 'expanding_immunology'
    },
    'ERLEADA_EXPANSION': {
        'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 3.6,
        'launch_date': '2020-09-14', 'patent_expiry': '2032-09-14',
        'indication': 'Prostate Cancer', 'peak_sales_estimate': 5.0,
        'status': 'expanding_oncology'
    },
    'BALVERSA_LAUNCH': {
        'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 0.4,
        'launch_date': '2021-04-03', 'patent_expiry': '2033-04-03',
        'indication': 'Bladder Cancer', 'peak_sales_estimate': 2.0,
        'status': 'targeted_therapy'
    },

    # Pfizer Major Launches
    'VYNDAQEL_EXPANSION': {
        'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 3.9,
        'launch_date': '2020-05-03', 'patent_expiry': '2030-05-03',
        'indication': 'Cardiomyopathy', 'peak_sales_estimate': 6.0,
        'status': 'rare_disease_blockbuster'
    },
    'NURTEC_ODT_LAUNCH': {
        'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 1.5,
        'launch_date': '2020-02-27', 'patent_expiry': '2032-02-27',
        'indication': 'Migraine', 'peak_sales_estimate': 3.0,
        'status': 'cgrp_inhibitor'
    },
    'PADCEV_EXPANSION': {
        'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 1.2,
        'launch_date': '2020-12-18', 'patent_expiry': '2032-12-18',
        'indication': 'Urothelial Cancer', 'peak_sales_estimate': 4.0,
        'status': 'adc_therapy'
    },
    'LORBRENA_LAUNCH': {
        'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 0.5,
        'launch_date': '2021-11-30', 'patent_expiry': '2033-11-30',
        'indication': 'Non-Small Cell Lung Cancer', 'peak_sales_estimate': 2.0,
        'status': 'targeted_therapy'
    },
    'ELREXFIO_LAUNCH': {
        'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 0.1,
        'launch_date': '2023-08-14', 'patent_expiry': '2035-08-14',
        'indication': 'Multiple Myeloma', 'peak_sales_estimate': 1.5,
        'status': 'bispecific_antibody'
    },

    # Merck Major Launches
    'WINREVAIR_LAUNCH': {
        'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 1.1,
        'launch_date': '2024-03-26', 'patent_expiry': '2036-03-26',
        'indication': 'Pulmonary Arterial Hypertension', 'peak_sales_estimate': 5.0,
        'status': 'breakthrough_therapy'
    },
    'LAGEVRIO_LAUNCH': {
        'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 0.2,
        'launch_date': '2021-10-11', 'patent_expiry': '2033-10-11',
        'indication': 'COVID-19 Treatment', 'peak_sales_estimate': 8.0,
        'status': 'antiviral_therapy'
    },
    'RECARBRIO_LAUNCH': {
        'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 0.3,
        'launch_date': '2020-07-17', 'patent_expiry': '2032-07-17',
        'indication': 'Complicated UTI/Pneumonia', 'peak_sales_estimate': 1.0,
        'status': 'antibiotic'
    },
    'VAXNEUVANCE_LAUNCH': {
        'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 0.4,
        'launch_date': '2021-07-19', 'patent_expiry': '2033-07-19',
        'indication': 'Pneumococcal Disease', 'peak_sales_estimate': 2.0,
        'status': 'vaccine'
    },

    # Additional Major Launches
    'UBRELVY_LAUNCH': {
        'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 1.2,
        'launch_date': '2020-02-21', 'patent_expiry': '2032-02-21',
        'indication': 'Migraine', 'peak_sales_estimate': 3.0,
        'status': 'cgrp_inhibitor'
    },
    'QULIPTA_LAUNCH': {
        'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 0.6,
        'launch_date': '2021-09-28', 'patent_expiry': '2033-09-28',
        'indication': 'Migraine Prevention', 'peak_sales_estimate': 2.0,
        'status': 'cgrp_inhibitor'
    },
    'ELAHERE_LAUNCH': {
        'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 0.8,
        'launch_date': '2022-11-14', 'patent_expiry': '2034-11-14',
        'indication': 'Ovarian Cancer', 'peak_sales_estimate': 3.0,
        'status': 'adc_therapy'
    },
    'COBENFY_LAUNCH': {
        'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 0.1,
        'launch_date': '2024-09-26', 'patent_expiry': '2036-09-26',
        'indication': 'Schizophrenia', 'peak_sales_estimate': 5.0,
        'status': 'novel_mechanism'
    },
    'SOTYKTU_LAUNCH': {
        'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 0.3,
        'launch_date': '2022-09-16', 'patent_expiry': '2034-09-16',
        'indication': 'Psoriasis', 'peak_sales_estimate': 2.0,
        'status': 'oral_immunology'
    },
    'TEZSPIRE_LAUNCH': {
        'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 1.1,
        'launch_date': '2021-12-17', 'patent_expiry': '2033-12-17',
        'indication': 'Severe Asthma', 'peak_sales_estimate': 4.0,
        'status': 'biologic_respiratory'
    },
    'EVENITY_EXPANSION': {
        'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 1.8,
        'launch_date': '2020-04-15', 'patent_expiry': '2032-04-15',
        'indication': 'Osteoporosis', 'peak_sales_estimate': 3.0,
        'status': 'bone_health'
    },
    'LUMAKRAS_LAUNCH': {
        'company': 'Amgen', 'ticker': 'AMGN', 'revenue_billions': 0.4,
        'launch_date': '2021-05-28', 'patent_expiry': '2033-05-28',
        'indication': 'Non-Small Cell Lung Cancer', 'peak_sales_estimate': 2.0,
        'status': 'kras_inhibitor'
    },
    'VERZENIO_EXPANSION': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 4.6,
        'launch_date': '2020-02-28', 'patent_expiry': '2032-02-28',
        'indication': 'Breast Cancer (Early Stage)', 'peak_sales_estimate': 6.0,
        'status': 'cdk_inhibitor'
    },
    'OLUMIANT_EXPANSION': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 0.8,
        'launch_date': '2020-06-01', 'patent_expiry': '2032-06-01',
        'indication': 'Alopecia Areata', 'peak_sales_estimate': 2.0,
        'status': 'jak_inhibitor'
    },
    'EMGALITY_EXPANSION': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 1.0,
        'launch_date': '2020-09-25', 'patent_expiry': '2032-09-25',
        'indication': 'Cluster Headache', 'peak_sales_estimate': 2.5,
        'status': 'cgrp_inhibitor'
    },
    'SUNLENCA_LAUNCH': {
        'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 0.3,
        'launch_date': '2022-12-22', 'patent_expiry': '2034-12-22',
        'indication': 'HIV', 'peak_sales_estimate': 2.0,
        'status': 'long_acting_hiv'
    },
    'LIVDELZI_LAUNCH': {
        'company': 'Gilead Sciences', 'ticker': 'GILD', 'revenue_billions': 0.1,
        'launch_date': '2024-06-18', 'patent_expiry': '2036-06-18',
        'indication': 'Primary Biliary Cholangitis', 'peak_sales_estimate': 1.5,
        'status': 'rare_disease'
    },
    'SKYCLARYS_LAUNCH': {
        'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 0.5,
        'launch_date': '2023-02-28', 'patent_expiry': '2035-02-28',
        'indication': 'Friedreich\'s Ataxia', 'peak_sales_estimate': 2.0,
        'status': 'rare_neurological'
    },
    'ZURZUVAE_LAUNCH': {
        'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 0.1,
        'launch_date': '2023-08-04', 'patent_expiry': '2035-08-04',
        'indication': 'Postpartum Depression', 'peak_sales_estimate': 3.0,
        'status': 'cns_breakthrough'
    },
    'MRESVIA_LAUNCH': {
        'company': 'Moderna', 'ticker': 'MRNA', 'revenue_billions': 0.008,
        'launch_date': '2023-05-31', 'patent_expiry': '2035-05-31',
        'indication': 'RSV (Older Adults)', 'peak_sales_estimate': 2.0,
        'status': 'mrna_vaccine'
    },
    'AREXVY_LAUNCH': {
        'company': 'GSK', 'ticker': 'GSK', 'revenue_billions': 1.2,
        'launch_date': '2023-05-03', 'patent_expiry': '2035-05-03',
        'indication': 'RSV (Older Adults)', 'peak_sales_estimate': 3.0,
        'status': 'protein_vaccine'
    },
    'ABRYSVO_LAUNCH': {
        'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 0.9,
        'launch_date': '2023-05-31', 'patent_expiry': '2035-05-31',
        'indication': 'RSV (Maternal/Infant)', 'peak_sales_estimate': 2.5,
        'status': 'maternal_vaccine'
    },
    'NEXVIAZYME_LAUNCH': {
        'company': 'Sanofi', 'ticker': 'SNY', 'revenue_billions': 0.8,
        'launch_date': '2021-08-02', 'patent_expiry': '2033-08-02',
        'indication': 'Pompe Disease', 'peak_sales_estimate': 2.0,
        'status': 'enzyme_replacement'
    }
}

# BACKTEST TARGET DRUGS (2020-2025) - 50 Drugs That Expired
BACKTEST_TARGET_DRUGS = {
    # High-Value Patent Expirations (2020-2023)
    'PLAVIX': {
        'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 6.8,
        'patent_expiry': '2020-05-17', 'peak_revenue_year': 2011,
        'status': 'expired_in_period'
    },
    'HUMIRA_BACKTEST': {
        'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 18.5,
        'patent_expiry': '2023-01-31', 'peak_revenue_year': 2022,
        'status': 'expired_in_period'
    },
    'REVLIMID_BACKTEST': {
        'company': 'Bristol Myers Squibb', 'ticker': 'BMY', 'revenue_billions': 12.1,
        'patent_expiry': '2022-10-31', 'peak_revenue_year': 2021,
        'status': 'expired_in_period'
    },
    'AVASTIN': {
        'company': 'Roche', 'ticker': 'RHHBY', 'revenue_billions': 7.1,
        'patent_expiry': '2024-02-26', 'peak_revenue_year': 2018,
        'status': 'expired_in_period'
    },
    'HERCEPTIN': {
        'company': 'Roche', 'ticker': 'RHHBY', 'revenue_billions': 6.4,
        'patent_expiry': '2020-06-30', 'peak_revenue_year': 2014,
        'status': 'expired_in_period'
    },
    'RITUXAN': {
        'company': 'Roche', 'ticker': 'RHHBY', 'revenue_billions': 5.8,
        'patent_expiry': '2020-11-26', 'peak_revenue_year': 2012,
        'status': 'expired_in_period'
    },
    'LYRICA': {
        'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 5.1,
        'patent_expiry': '2020-12-30', 'peak_revenue_year': 2018,
        'status': 'expired_in_period'
    },
    'BOTOX_BACKTEST': {
        'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 4.9,
        'patent_expiry': '2022-12-15', 'peak_revenue_year': 2021,
        'status': 'expired_in_period'
    },
    'GLEEVEC': {
        'company': 'Novartis', 'ticker': 'NVS', 'revenue_billions': 4.7,
        'patent_expiry': '2021-07-30', 'peak_revenue_year': 2012,
        'status': 'expired_in_period'
    },
    'TECFIDERA_BACKTEST': {
        'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 4.3,
        'patent_expiry': '2020-04-30', 'peak_revenue_year': 2017,
        'status': 'expired_in_period'
    },
    'REMICADE': {
        'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 4.2,
        'patent_expiry': '2021-09-23', 'peak_revenue_year': 2014,
        'status': 'expired_in_period'
    },
    'NEXIUM': {
        'company': 'AstraZeneca', 'ticker': 'AZN', 'revenue_billions': 3.9,
        'patent_expiry': '2020-05-27', 'peak_revenue_year': 2013,
        'status': 'expired_in_period'
    },
    'LANTUS': {
        'company': 'Sanofi', 'ticker': 'SNY', 'revenue_billions': 3.7,
        'patent_expiry': '2020-02-12', 'peak_revenue_year': 2015,
        'status': 'expired_in_period'
    },
    'ADVAIR': {
        'company': 'GSK', 'ticker': 'GSK', 'revenue_billions': 3.5,
        'patent_expiry': '2020-08-13', 'peak_revenue_year': 2013,
        'status': 'expired_in_period'
    },
    'ENBREL_EU': {
        'company': 'Pfizer', 'ticker': 'PFE', 'revenue_billions': 3.2,
        'patent_expiry': '2023-10-15', 'peak_revenue_year': 2016,
        'status': 'expired_in_period'
    },
    'LUCENTIS': {
        'company': 'Roche', 'ticker': 'RHHBY', 'revenue_billions': 2.9,
        'patent_expiry': '2022-06-30', 'peak_revenue_year': 2012,
        'status': 'expired_in_period'
    },
    'VYVANSE': {
        'company': 'Takeda', 'ticker': 'TAK', 'revenue_billions': 2.5,
        'patent_expiry': '2023-02-24', 'peak_revenue_year': 2021,
        'status': 'expired_in_period'
    },
    'SERETIDE': {
        'company': 'GSK', 'ticker': 'GSK', 'revenue_billions': 2.3,
        'patent_expiry': '2021-01-25', 'peak_revenue_year': 2016,
        'status': 'expired_in_period'
    },
    'SUBOXONE': {
        'company': 'Indivior', 'ticker': 'INDV.L', 'revenue_billions': 2.1,
        'patent_expiry': '2020-09-14', 'peak_revenue_year': 2013,
        'status': 'expired_in_period'
    },
    'ABILIFY_MAINTENA': {
        'company': 'Otsuka', 'ticker': '4578.T', 'revenue_billions': 2.0,
        'patent_expiry': '2023-04-28', 'peak_revenue_year': 2020,
        'status': 'expired_in_period'
    },
    'COPAXONE': {
        'company': 'Teva', 'ticker': 'TEVA', 'revenue_billions': 1.8,
        'patent_expiry': '2020-09-15', 'peak_revenue_year': 2012,
        'status': 'expired_in_period'
    },
    'CIALIS': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 1.4,
        'patent_expiry': '2020-10-06', 'peak_revenue_year': 2013,
        'status': 'expired_in_period'
    },
    'NAMENDA': {
        'company': 'Allergan', 'ticker': 'AGN', 'revenue_billions': 1.3,
        'patent_expiry': '2021-07-11', 'peak_revenue_year': 2013,
        'status': 'expired_in_period'
    },
    'JANUMET': {
        'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 1.2,
        'patent_expiry': '2022-03-02', 'peak_revenue_year': 2019,
        'status': 'expired_in_period'
    },
    'RESTASIS': {
        'company': 'AbbVie', 'ticker': 'ABBV', 'revenue_billions': 1.1,
        'patent_expiry': '2020-05-27', 'peak_revenue_year': 2016,
        'status': 'expired_in_period'
    },
    'LATUDA': {
        'company': 'Sumitomo', 'ticker': '4506.T', 'revenue_billions': 1.6,
        'patent_expiry': '2023-02-28', 'peak_revenue_year': 2020,
        'status': 'expired_in_period'
    },
    'BELSOMRA': {
        'company': 'Merck & Co.', 'ticker': 'MRK', 'revenue_billions': 0.9,
        'patent_expiry': '2024-08-13', 'peak_revenue_year': 2022,
        'status': 'expired_in_period'
    },
    'VICTOZA': {
        'company': 'Novo Nordisk', 'ticker': 'NVO', 'revenue_billions': 2.8,
        'patent_expiry': '2023-06-26', 'peak_revenue_year': 2019,
        'status': 'expired_in_period'
    },
    'SYMBICORT': {
        'company': 'AstraZeneca', 'ticker': 'AZN', 'revenue_billions': 2.4,
        'patent_expiry': '2021-07-17', 'peak_revenue_year': 2015,
        'status': 'expired_in_period'
    },
    'FORTEO': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 1.4,
        'patent_expiry': '2020-08-25', 'peak_revenue_year': 2017,
        'status': 'expired_in_period'
    },
    'SIMPONI': {
        'company': 'Johnson & Johnson', 'ticker': 'JNJ', 'revenue_billions': 1.9,
        'patent_expiry': '2024-04-24', 'peak_revenue_year': 2021,
        'status': 'expired_in_period'
    },
    'XOLAIR': {
        'company': 'Roche', 'ticker': 'RHHBY', 'revenue_billions': 2.7,
        'patent_expiry': '2020-06-20', 'peak_revenue_year': 2017,
        'status': 'expired_in_period'
    },
    'SPINRAZA_COMPETITION': {
        'company': 'Biogen', 'ticker': 'BIIB', 'revenue_billions': 1.7,
        'patent_expiry': '2024-12-23', 'peak_revenue_year': 2019,
        'status': 'expired_in_period'
    },
    'ALIMTA': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 2.3,
        'patent_expiry': '2022-05-10', 'peak_revenue_year': 2016,
        'status': 'expired_in_period'
    },
    'ERBITUX': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 1.8,
        'patent_expiry': '2021-02-08', 'peak_revenue_year': 2011,
        'status': 'expired_in_period'
    },
    'HUMALOG_MIX': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 1.1,
        'patent_expiry': '2023-12-11', 'peak_revenue_year': 2019,
        'status': 'expired_in_period'
    },
    'STRATTERA': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 0.8,
        'patent_expiry': '2021-05-29', 'peak_revenue_year': 2010,
        'status': 'expired_in_period'
    },
    'CYMBALTA_GENERIC': {
        'company': 'Eli Lilly', 'ticker': 'LLY', 'revenue_billions': 1.5,
        'patent_expiry': '2020-12-11', 'peak_revenue_year': 2012,
        'status': 'expired_in_period'
    },
    'VELCADE': {
        'company': 'Takeda', 'ticker': 'TAK', 'revenue_billions': 1.9,
        'patent_expiry': '2022-05-13', 'peak_revenue_year': 2011,
        'status': 'expired_in_period'
    },
    'NINLARO': {
        'company': 'Takeda', 'ticker': 'TAK', 'revenue_billions': 0.8,
        'patent_expiry': '2024-11-20', 'peak_revenue_year': 2021,
        'status': 'expired_in_period'
    },
    'ENTYVIO_COMPETITION': {
        'company': 'Takeda', 'ticker': 'TAK', 'revenue_billions': 4.4,
        'patent_expiry': '2024-05-20', 'peak_revenue_year': 2022,
        'status': 'expired_in_period'
    },
    'ACTOS': {
        'company': 'Takeda', 'ticker': 'TAK', 'revenue_billions': 2.1,
        'patent_expiry': '2020-08-17', 'peak_revenue_year': 2010,
        'status': 'expired_in_period'
    },
    'ULORIC': {
        'company': 'Takeda', 'ticker': 'TAK', 'revenue_billions': 0.4,
        'patent_expiry': '2021-02-16', 'peak_revenue_year': 2016,
        'status': 'expired_in_period'
    },
    'COLCRYS': {
        'company': 'Takeda', 'ticker': 'TAK', 'revenue_billions': 0.3,
        'patent_expiry': '2020-07-30', 'peak_revenue_year': 2012,
        'status': 'expired_in_period'
    },
    'BENLYSTA': {
        'company': 'GSK', 'ticker': 'GSK', 'revenue_billions': 0.9,
        'patent_expiry': '2024-03-09', 'peak_revenue_year': 2022,
        'status': 'expired_in_period'
    },
    'NUCALA': {
        'company': 'GSK', 'ticker': 'GSK', 'revenue_billions': 1.5,
        'patent_expiry': '2025-11-04', 'peak_revenue_year': 2023,
        'status': 'expiring_soon'
    },
    'ANORO': {
        'company': 'GSK', 'ticker': 'GSK', 'revenue_billions': 1.1,
        'patent_expiry': '2025-12-18', 'peak_revenue_year': 2022,
        'status': 'expiring_soon'
    },
    'BREO': {
        'company': 'GSK', 'ticker': 'GSK', 'revenue_billions': 1.3,
        'patent_expiry': '2025-05-21', 'peak_revenue_year': 2021,
        'status': 'expiring_soon'
    },
    'TRELEGY': {
        'company': 'GSK', 'ticker': 'GSK', 'revenue_billions': 2.1,
        'patent_expiry': '2025-09-10', 'peak_revenue_year': 2024,
        'status': 'expiring_soon'
    },
    'ZEJULA': {
        'company': 'GSK', 'ticker': 'GSK', 'revenue_billions': 0.6,
        'patent_expiry': '2025-03-27', 'peak_revenue_year': 2023,
        'status': 'expiring_soon'
    }
}

# Backtesting parameters
BACKTEST_CONFIG = {
    'start_date': '2020-01-01',
    'end_date': '2025-12-31',
    'rebalance_frequency': 'quarterly',  # 'monthly', 'quarterly', 'annually'
    'initial_capital': 100000,  # $100k
    'transaction_cost': 0.001,  # 0.1% transaction cost
    'min_weight': 0.02,  # Minimum 2% allocation
    'max_weight': 0.15,  # Maximum 15% allocation per position
    'benchmark_ticker': 'SPY',  # S&P 500 benchmark
    'use_backtest_drugs': True,  # Flag to use backtest-specific drug list
    'include_new_launches': True,  # Include new drug launches in backtest
    'new_launch_boost': 1.2,  # 20% weight boost for promising new launches
    'launch_evaluation_window': 30,  # Days after launch to start investing
}

# Risk model parameters
RISK_PARAMETERS = {
    'lookback_window': 252,  # 1 year for volatility calculation
    'min_time_to_cliff': 0.5,  # Minimum 6 months to patent cliff
    'max_revenue_risk_percent': 100,  # Maximum revenue at risk threshold
    'diversification_penalty': 0.1,  # 10% penalty per additional drug at risk
}

# Enhanced risk model parameters for backtesting
BACKTEST_RISK_PARAMETERS = {
    'lookback_window': 252,  # 1 year for volatility calculation
    'min_time_to_cliff': 0.25,  # Minimum 3 months to patent cliff
    'cliff_horizon_years': 2.0,  # Start reducing weight 2 years before cliff
    'expired_drug_weight': 0.0,  # No weight for drugs that have already expired
    'diversification_penalty': 0.05,  # 5% penalty per additional drug at risk per company
    'risk_decay_factor': 0.5,  # How aggressively to reduce weight as cliff approaches
    
    # New launch parameters
    'new_launch_weight_boost': 1.3,  # 30% boost for new promising launches
    'launch_momentum_factor': 0.8,  # Factor for launch momentum scoring
    'blockbuster_threshold': 5.0,  # $5B revenue threshold for blockbuster status
    'pandemic_drug_volatility_adjust': 1.5,  # Higher volatility for pandemic drugs
    'breakthrough_therapy_boost': 1.2,  # 20% boost for breakthrough designations
    
    # Patent cliff timing adjustments
    'cliff_impact_severity': {
        'blockbuster': 0.8,  # 80% revenue impact for blockbusters
        'major': 0.6,  # 60% revenue impact for major drugs
        'standard': 0.4,  # 40% revenue impact for standard drugs
    },
    
    # Launch success probability factors
    'launch_success_factors': {
        'first_in_class': 1.4,
        'best_in_class': 1.2,
        'me_too': 0.8,
        'biosimilar': 0.6,
    }
}

# Analysis parameters  
ANALYSIS_CONFIG = {
    'stock_data_start': '2020-01-01',
    'stock_data_end': '2025-12-31',
    'plot_style': 'seaborn-v0_8',
    'figure_size': (12, 10),
    'include_covid_impact_analysis': True,  # Analyze COVID drug impact separately
    'sector_analysis': True,  # Include pharma sector comparison
    'patent_cliff_lead_time_analysis': [6, 12, 18, 24],  # Months before cliff to analyze
}