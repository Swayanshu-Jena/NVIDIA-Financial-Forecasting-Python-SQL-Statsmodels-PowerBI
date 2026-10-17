import os
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine

# Automatically created the data directories if they don't exist
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

# Downloaded daily stock data for NVIDIA and the S&P 500
data = yf.download(['NVDA', '^GSPC'], start='2021-01-01', end='2026-10-01', group_by='ticker')

# SAVED RAW DATA: Export the untouched data immediately after downloading
data['NVDA'].to_csv('data/raw/nvda_stock_history.csv')
data['^GSPC'].to_csv('data/raw/sp500_market_index.csv')

# Removed empty rows and fixed column names for NVIDIA
nvda_df = data['NVDA'].copy().dropna()
nvda_df.reset_index(inplace=True)
nvda_df.columns = [col.lower().replace(' ', '_') for col in nvda_df.columns]

# Extracted, cleaned, and formatted the S&P 500 data
sp500_df = data['^GSPC'].copy().dropna()
sp500_df.reset_index(inplace=True)
sp500_df.columns = [col.lower().replace(' ', '_') for col in sp500_df.columns]

# Saved the Q3 2026 revenue numbers for the pie chart
segments_data = {
    'segment': ['Data Center', 'Gaming', 'Professional Visualization', 'Automotive & OEM'],
    'revenue_billions': [51.2, 3.4, 0.55, 0.56] 
}
segment_df = pd.DataFrame(segments_data)

# SAVED PROCESSED DATA: Export the cleaned data before sending it to SQL
nvda_df.to_csv('data/processed/cleaned_stock_data.csv', index=False)
sp500_df.to_csv('data/processed/sp500_index_data.csv', index=False)
segment_df.to_csv('data/processed/q3_revenue_segments.csv', index=False)

# Connected to the local database
engine = create_engine('mysql+pymysql://root:Swayanshu2004@localhost:3306/financial_data')

# Saved all tables to the database so Power BI can use them
nvda_df.to_sql('cleaned_stock_data', con=engine, if_exists='replace', index=False)
sp500_df.to_sql('sp500_index_data', con=engine, if_exists='replace', index=False)
segment_df.to_sql('nvidia_revenue_distribution', con=engine, if_exists='replace', index=False)