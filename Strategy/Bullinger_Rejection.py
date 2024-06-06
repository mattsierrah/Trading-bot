import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

# Load data
data = pd.read_csv("RNDRUSDT_1.csv", parse_dates=['date'], index_col='date')

# Calculate VWAP
data.ta.vwap(append=True)

data

# Calculate Bollinger Bands
data.ta.bbands(length=10, std=1.5, append=True)

# Calculate SMA
data['SMA'] = ta.sma(data['close'], length=20)

# Calculate RSI
data['RSI'] = ta.rsi(data['close'], length=14)

data

# Calculate MACD
macd = ta.macd(data['close'], fast=12, slow=26, signal=9)
data = pd.concat([data, macd], axis=1)

# Add the upper and lower bands to the DataFrame
data['Upper Band'] = data['BBU_10_1.5']
data['Lower Band'] = data['BBL_10_1.5']

# Drop NaN values
data.dropna(inplace=True)

# Function to check trend based on moving average
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

# Apply the function to the DataFrame
data['Trend'] = check_candles(data, 7, 'SMA')

# Entry Based on Bollinger Bands - Candles Crossing
data['entry'] = 0

# Condition for entry category 2 (buy entry)
buy_entry_condition = (data['Trend'] == 2) & ((data['open'] < data['Lower Band']) & (data['close'] > data['Lower Band']))
data.loc[buy_entry_condition, 'entry'] = 2

# Condition for entry category 1 (sell entry)
sell_entry_condition = (data['Trend'] == 1) & ((data['open'] > data['Upper Band']) & (data['close'] < data['Upper Band']))
data.loc[sell_entry_condition, 'entry'] = 1

# Filter entries
entries = data[data['entry'] != 0]

# Print entries
print(entries)

# Plotting the data
fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Candlesticks')])

# Add the moving averages and other indicators to the plot
fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name='SMA', line=dict(color='red')))
fig.add_trace(go.Scatter(x=data.index, y=data['Lower Band'], mode='lines', name='Lower Band', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=data.index, y=data['Upper Band'], mode='lines', name='Upper Band', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=data.index, y=data['VWAP_D'], mode='lines', name='VWAP_D', line=dict(color='purple')))
#fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='orange')))
#fig.add_trace(go.Scatter(x=data.index, y=data['MACD_12_26_9'], mode='lines', name='MACD', line=dict(color='green')))
#fig.add_trace(go.Scatter(x=data.index, y=data['MACDh_12_26_9'], mode='lines', name='MACD Histogram', line=dict(color='cyan')))
#fig.add_trace(go.Scatter(x=data.index, y=data['MACDs_12_26_9'], mode='lines', name='MACD Signal', line=dict(color='magenta')))

fig.update_layout(
    title='Technical Analysis on RNDRUSDT',
    yaxis_title='Price',
    xaxis_title='Date',
    xaxis_rangeslider_visible=False,
    template='plotly_dark'
)

fig.show()

##  Entry based on RSI and Bollinger Bands

def add_rsi_column(data):
    # Calculate RSI with a period of 14
    data['RSI'] = ta.rsi(data['close'])
    return data

data = add_rsi_column(data)

def rsi_signal(data):
    data['RSI Signal'] = 0  # Initialize the signal column with 0

    # Set the signal category to 2 when the price is below the lower Bollinger Band and RSI is below 30
    data.loc[(data['close'] < data['Lower Band']) & (data['RSI'] < 55), 'RSI Signal'] = 2

    # Set the signal category to 1 when the price is above the upper Bollinger Band and RSI is above 70
    data.loc[(data['close'] > data['Upper Band']) & (data['RSI'] > 45), 'RSI Signal'] = 1

    return data

data = rsi_signal(data)

data[data["RSI Signal"]!=0]

data['entry'] = 0

# Condition for entry category 2 (buy entry)
buy_entry_condition = (data['Trend'] == 2) & (data['RSI Signal'] == 2) & (data['low'] < data['Lower Band'])
data.loc[buy_entry_condition, 'entry'] = 2

# Condition for entry category 1 (sell entry)
sell_entry_condition = (data['Trend'] == 1) & (data['RSI Signal'] == 1) & (data['high'] > data['Upper Band'])
data.loc[sell_entry_condition, 'entry'] = 1

data[data['entry']!=0]

## 3 - Entry based on a rejection candle next to Bollinger Bands


def identify_shooting_star(data):
    # Create a new column for shooting star
    data['shooting_star'] = data.apply(lambda row: 2 if (
        ( (min(row['open'], row['close']) - row['low']) > (1.5 * abs(row['close'] - row['open']))) and 
        (row['high'] - max(row['close'], row['open'])) < (0.8 * abs(row['close'] - row['open'])) and 
        (abs(row['open'] - row['close']) > row['open'] * 0.01)
    ) else 1 if (
        (row['high'] - max(row['open'], row['close'])) > (1.5 * abs(row['open'] - row['close'])) and 
        (min(row['close'], row['open']) - row['low']) < (0.8 * abs(row['open'] - row['close'])) and 
        (abs(row['open'] - row['close']) > row['open'] * 0.01)
    ) else 0, axis=1)

    return data

data = identify_shooting_star(data)

data[data['shooting_star']!=0]