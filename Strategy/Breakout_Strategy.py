import pandas as pd
from backtesting import Backtest, Strategy

# Load data from CSV file
data = pd.read_csv('RNDRUSDT_1.csv', parse_dates=['date'], index_col='date')


# Ensure column names match the expected format
data.columns = [col.capitalize() for col in data.columns]

# Define the Breakout Strategy
class BreakoutStrategy(Strategy):
    n = 20  # Look-back period for the breakout

    def init(self):
        # Convert to pandas Series for rolling calculation
        high_series = pd.Series(self.data.High, index=self.data.index)
        low_series = pd.Series(self.data.Low, index=self.data.index)

        # Track the highest high and lowest low over the look-back period
        self.highest_high = self.I(lambda: high_series.rolling(self.n).max())
        self.lowest_low = self.I(lambda: low_series.rolling(self.n).min())

    def next(self):
        # If the current price breaks above the highest high, buy
        if self.data.Close[-1] > self.highest_high[-1]:
            self.position.close()
            self.buy()
        
        # If the current price breaks below the lowest low, sell
        elif self.data.Close[-1] < self.lowest_low[-1]:
            self.position.close()
            self.sell()

# Run the backtest
bt = Backtest(data, BreakoutStrategy, cash=10000, commission=.002)
stats = bt.run()
print(stats)

bt.plot()

# Optimize Parameters
param_grid = {'n': range(10, 50, 5)}
res = bt.optimize(**param_grid)

# Print the best results and the parameters that lead to these results
print("Best result: ", res['Return [%]'])
print("Parameters for best result: ", res['_strategy'])

print(res)
print(res['_equity_curve'])