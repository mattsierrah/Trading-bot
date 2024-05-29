from datetime import date, timedelta
import pandas as pd
from binance import Client

# Define dates
today = date.today()
yesterday = today - timedelta(days=1)

def criptodata(dataticker):
    api_key = "Your api key"
    api_secret = "you api secret key"
    # Create a Binance Client instance
    client = Client(api_key, api_secret)
    
    # Get the current price of the ticker
    try:
        price = client.get_symbol_ticker(symbol=dataticker)
        print(price)
    except Exception as e:
        print(f"Error price for {dataticker}: {e}")
        return
    
    # Get historical data
    asset = dataticker
    start = "2020-01-01"
    end = str(yesterday)
    timeframe = Client.KLINE_INTERVAL_1DAY
    
    try:
        klines = client.get_historical_klines(asset, timeframe, start, end)
    except Exception as e:
        print(f"Error historical data for {dataticker}: {e}")
        return
    
    # Create the DataFrame
    df = pd.DataFrame(klines)
    
    # Adjust DataFrame Columns
    df = df.iloc[:, :12]
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_asset_volume', 'number_of_trades',
    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    
    # Convert open_time to date and set as index
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df.set_index('open_time', inplace=True)
    
    # Convert columns to float type
    df = df.astype(float)
    
    # Save the DataFrame to a CSV file
    df.to_csv(dataticker + ".csv", encoding='utf-8')
    print(f"Data extraction finished for {dataticker} :)")

# Ticker List
ticker_list = ["BNBUSDT", "RNDRUSDT", "SOLUSDT", "BTCUSDT"]

# Extract data for each ticker
for ticker in ticker_list:
    criptodata(ticker)