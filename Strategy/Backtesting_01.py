import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Simple Moving Average function
def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

# SMA Cross Strategy class
class SmaCross(Strategy):
    n1 = 30
    n2 = 100

    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()

# Load data from CSV file
data = pd.read_csv('RNDRUSDT_1.csv', parse_dates=['date'], index_col='date').tail(366)

# Format the data for the backtesting framework
data.columns = [col.capitalize() for col in data.columns]  # Ensure column names match expected format

# Code for running the backtest.
bt = Backtest(data, SmaCross)
stats = bt.run()

#print(stats['_trades'].to_string())
print(stats)

bt.plot()

# Define a range of values to test for each parameter
param_grid = {'n1': range(5, 60, 5), 'n2': range(10, 90, 5)}
# Run the optimization
res = bt.optimize(**param_grid)

# Print the best results and the parameters that lead to these results
print("Best result: ", res['Return [%]'])
print("Parameters for best result: ", res['_strategy'])

print(res)
print(res['_equity_curve'])

