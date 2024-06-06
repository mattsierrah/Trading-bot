import pandas as pd
import numpy as np
import pandas_ta as ta
import plotly.graph_objects as go
from sklearn.model_selection import ParameterGrid
from sklearn.metrics import accuracy_score

# Load data
data = pd.read_csv("RNDRUSDT 15m.csv", parse_dates=['Date'], index_col='Date')

# Calculate VWAP
data.ta.vwap(append=True)

# Define the check_candles function with additional parameter optimization
def check_candles(data, backcandles, ma_column):
    categories = [0 for _ in range(backcandles)]
    for i in range(backcandles, len(data)):
        if all(data['close'][i-backcandles:i] > data[ma_column][i-backcandles:i]):
            categories.append(2)  # Uptrend
        elif all(data['close'][i-backcandles:i] < data[ma_column][i-backcandles:i]):
            categories.append(1)  # Downtrend
        else:
            categories.append(0)  # No trend
    return categories

# Optimize parameters
best_params = None
best_score = -1

# Define the parameter grid for optimization
param_grid = {    'backcandles': [3, 5, 7],
    'vwap_period': [20, 30, 50]
} 

for params in ParameterGrid(param_grid):
    # Calculate VWAP with different periods
    data['VWAP'] = data['close'].rolling(window=params['vwap_period']).mean()
    
    # Apply the check_candles function
    data['Category'] = check_candles(data, params['backcandles'], 'VWAP')
    
    # Evaluate performance (for simplicity, we use a dummy accuracy score)
    score = accuracy_score(data['Category'][params['backcandles']:], 
                           data['Category'][params['backcandles']:])
    
    if score > best_score:
        best_score = score
        best_params = params

print(f"Best parameters: {best_params} with score: {best_score}")

data 

# Apply the best parameters
data['VWAP'] = data['close'].rolling(window=best_params['vwap_period']).mean()
data['Category'] = check_candles(data, best_params['backcandles'], 'VWAP')

# Combine with other indicators (RSI and MACD)
data['RSI'] = ta.rsi(data['close'], length=14)
macd = ta.macd(data['close'])
data = pd.concat([data, macd], axis=1)

# Filter data for potential buy/sell signals
buy_signals = data[(data['Category'] == 2) & (data['RSI'] < 30) & (data['MACD_12_26_9'] > data['MACDs_12_26_9'])]
sell_signals = data[(data['Category'] == 1) & (data['RSI'] > 70) & (data['MACD_12_26_9'] < data['MACDs_12_26_9'])]

print(f"Buy signals:\n{buy_signals}")
print(f"Sell signals:\n{sell_signals}")

data

# Visualization
dfpl = data[:]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                                     open=dfpl['open'],
                                     high=dfpl['high'],
                                     low=dfpl['low'],
                                     close=dfpl['close'])])

fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['VWAP'], mode='lines', name='VWAP', line=dict(color='red')))
fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['close'], mode='markers', name='Buy Signal', 
                         marker=dict(color='green', size=10, symbol='triangle-up')))
fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['close'], mode='markers', name='Sell Signal', 
                         marker=dict(color='red', size=10, symbol='triangle-down')))

fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()
