import os
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from sqlalchemy import create_engine

print("Connecting to database and fetching historical data...")
# Connected using root password
engine = create_engine('mysql+pymysql://root:Swayanshu2004@localhost:3306/financial_data')
nvidia_df = pd.read_sql("SELECT date, close FROM cleaned_stock_data", con=engine, parse_dates=['date'])

# Set datetime index and handle market holidays with forward fill
nvidia_df.set_index('date', inplace=True)
nvidia_df = nvidia_df.asfreq('B').ffill()

print("Running Augmented Dickey-Fuller Test for Stationarity...")
adf_result = adfuller(nvidia_df['close'].dropna())
print(f"ADF Statistic: {adf_result[0]:.4f}")
print(f"p-value: {adf_result[1]:.4f} (Series is non-stationary if p > 0.05)")

# Fit the ARIMA Model
# order=(1,1,1) applies first-order differencing (d=1) to handle the non-stationary trend
print("Fitting ARIMA Model (This may take a moment)...")
model = ARIMA(nvidia_df['close'], order=(1, 1, 1))
fitted_model = model.fit()

# Generated 30-day forward predictions with confidence intervals
print("Generating 30-day forecast...")
forecast = fitted_model.get_forecast(steps=30)
forecast_df = pd.DataFrame({
    'date': forecast.predicted_mean.index,
    'predicted_close': forecast.predicted_mean.values,
    'lower_ci_95': forecast.conf_int(alpha=0.05).iloc[:, 0].values,
    'upper_ci_95': forecast.conf_int(alpha=0.05).iloc[:, 1].values
})

# Ensured the processed directory exists
os.makedirs('data/processed', exist_ok=True)

# SAVED PROCESSED FORECAST: Export the ARIMA results to the local data folder
forecast_df.to_csv('data/processed/nvidia_arima_forecast.csv', index=False)
print("Forecast CSV successfully saved to data/processed/nvidia_arima_forecast.csv")

# Pushed forecast table to SQL using the updated 'nvidia' naming convention
forecast_df.to_sql('nvidia_arima_forecast', con=engine, if_exists='replace', index=False)
print("Forecast data successfully loaded into SQL table: nvidia_arima_forecast")