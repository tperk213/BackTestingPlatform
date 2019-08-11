from stratergy import Stratergy
from data import DataHandler
from portfolio import Portfolio
from event import SignalEvent
from backtest import Backtest
from execution import ExecutionHandler
from my_utils import params_to_attr

import datetime
import statsmodels.api as sm


class OLSMRStratergy(Stratergy):
    @params_to_attr
    def __init__(self, data, events, ols_window=30, zscore_low=0.5, zscore_high=3.0):
        """
            Params:
                data: dataHandler
                events: event Queue
                ols_window: window for calculating the relationship between the pair of stocks
                zscor:
                    the number of standard deviations from the mean of the residuals
                    used as enter and exit flags 
                    zscore_low:
                    zscore_high:
        """

        self.pair = ("AREX", "WLL")
        self.datetime = datetime.datetime.utcnow()

        self.long_market = False
        self.short_market = False

    def calculate_xy_signal(self, zscore_last):

        y_signal = None
        x_signal = None
        p0 = self.pair[0]
        p1 = self.pair[1]
        dt = self.datetime
        hr = abs(self.hedge_ratio)

        if zscore_last <= -self.zscore_high and not self.long_market:
            self.long_market = True
            y_signal = SignalEvent(p0, dt, "BUY", 1.0)
            x_signal = SignalEvent(p1, dt, "SELL", hr)

        if abs(zscore_last) <= self.zscore_low and self.long_market:
            self.long_market = False
            y_signal = SignalEvent(p0, dt, "EXIT", 1.0)
            x_signal = SignalEvent(p1, dt, "EXIT", 1.0)

        if zscore_last >= self.zscore_high and not self.short_market:
            self.short_market = True
            y_signal = SignalEvent(p0, dt, "SELL", 1.0)
            x_signal = SignalEvent(p1, dt, "BUY", hr)

        if abs(zscore_last) <= self.zscore_low and self.short_market:
            self.short_market = False
            y_signal = SignalEvent(p0, dt, "EXIT", 1.0)
            x_signal = SignalEvent(p1, dt, "EXIT", 1.0)

        return y_signal, x_signal

    def calculate_signal(self):
        """
            gets windowed data and calculates zscores and puts events in Queue
        """
        y = self.data.get_bar_values(self.pair[0], "adj_close", N=self.ols_window)
        x = self.data.get_bar_values(self.pair[1], "adj_close", N=self.ols_window)

        if y is not None and x is not None:
            if len(y) >= self.ols_window and len(x) >= self.ols_window:
                # get hedge ratio
                self.hedge_ratio = sm.OLS(y, x).fit().params[0]

                # get z score of residuals
                spread = y - self.hedge_ratio * x
                zscore_last = ((spread - spread.mean()) / spread.std())[-1]

                # calculate signals and add to events queue
                y_signal, x_signal = self.calculate_xy_signal(zscore_last)
                if y_signal is not None and x_signal is not None:
                    self.events.put(y_signal)
                    self.events.put(x_signal)


if __name__ == "__main__":

    csv_dir = "E:\\Code\\EventDrivenTrading\\stock_dfs"
    symbol_list = ["AREX", "WLL"]
    initial_capital = 100000
    start_date = datetime.datetime(2013, 1, 1)
    end_date = datetime.datetime(2014, 1, 1)

    backtest = Backtest(
        csv_dir,
        symbol_list,
        initial_capital,
        start_date,
        end_date,
        DataHandler,
        ExecutionHandler,
        Portfolio,
        OLSMRStratergy,
    )

    backtest.simulate_trading()
