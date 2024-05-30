import pandas as pd
import numpy as np

# Load the last 30 rows of the CSV files
rndr_df = pd.read_csv("RNDRUSDT.csv").tail(30)
sol_df = pd.read_csv("SOLUSDT.csv").tail(30)

# Print column names to ensure they match our expectations
print(f"RNDR columns: {rndr_df.columns.tolist()}")
print(f"SOL columns: {sol_df.columns.tolist()}")

# Select the 'close_time' and 'close' columns
rndr_prices = rndr_df[["close_time", "close"]]
sol_prices = sol_df[["close_time", "close"]]

# Merge the DataFrames on the 'close_time' column
merged_df = pd.merge(rndr_prices, sol_prices, on="close_time", how="inner", suffixes=('_rndr', '_sol'))

# Calculate the correlation coefficient between RNDR and SOL close prices
correlation = np.corrcoef(merged_df["close_rndr"], merged_df["close_sol"])[0, 1]
print(f"Correlation: {correlation:.4f}")

# Assign a score based on the correlation level
def get_correlation_score(corr):
    if corr > 0.8:
        return 10
    elif corr > 0.78:
        return 9
    elif corr > 0.4:
        return 8
    elif corr > 0.2:
        return 7
    elif corr > 0:
        return 6
    elif corr > -0.2:
        return 5
    elif corr > -0.4:
        return 4
    elif corr > -0.6:
        return 3
    elif corr > -0.8:
        return 2
    else:
        return 1

# Get the score
score = get_correlation_score(correlation)

# Print the score
print(f"The correlation score between RNDR and SOL is: {score}")