import pandas as pd
import numpy as np
import os

from my_utils import params_to_attr
from event import MarketEvent
from math import isnan


class DataHandler:
    """
        Holds the data frame of the current and future bar info
    """

    @params_to_attr
    def __init__(self, events, csv_dir, symbol_list, start_date=None, end_date=None):
        """
            Params:
                events:
                    queue object of events only used to register new market events
                csv_dir:
                    directory path where csv files are located
                    "E:\\Code\\EventDrivenTrading\\stock_dfs"
                symbol_list:
                    list of ticker/symbol names of the csv files required from the folder
                    ["APPL", "GOOG"]
                    the csv files are assumed to be of form "symbol.csv"
                
            self.symbol_data is dictionary of iterator with key being symbol
            {"symbol": iterator(datetime, row)}
                (index="datetime", row)
                row_keys:
                "open", "high", "low", "close", "volume", "adj_close"
            
            bar will be of form
            (index="datetime", row)
        
        """
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.open_convert_csv_files(symbol_list, csv_dir, start_date, end_date)
        self.finished = False

    def open_convert_csv_files(self, symbol_list, csv_dir, start_date, end_date):
        """
            Opens the csv files and combines them into a dataframe self.symbol_data[s]
            csv files are assumed to be from yahoo finance

            combines index datetimes of all files so they are same length
            pads forward any missing values for all symbols

            self.symbol_data dictionary of iterator with key being symbol
            {"symbol": iterator(datetime, row)}
        """
        comb_index = None
        for s in symbol_list:
            self.symbol_data[s] = pd.read_csv(
                os.path.join(csv_dir, "{}.csv".format(s)),
                header=0,
                index_col=0,
                parse_dates=True,
                names=[
                    "datetime",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "adj_close",
                ],
            )

            # Combine indexs to match pad values forward if missing
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            # create start entry in latest_symbol_data
            self.latest_symbol_data[s] = []

        # reIndex and turn into iterator
        for s in symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(
                index=comb_index, method="pad"
            )
            if start_date is not None:
                self.symbol_data[s] = self.symbol_data[s].loc[start_date:]
            else:
                self.start_date = self.symbol_data[s].index[0]
            if end_date is not None:
                self.symbol_data[s] = self.symbol_data[s].loc[:end_date]

            self.symbol_data[s] = self.symbol_data[s].iterrows()

    def _get_new_bar(self, symbol):
        # b is of form
        # (index, row)
        # row is a dict i belive with keys of column names
        for b in self.symbol_data[symbol]:
            yield b

    def update_bars(self):
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
                # bar is of form
                # (index, row)
                # row is a dict i belive with keys of column names
            except StopIteration:
                print("finished backtest")
                self.finished = True
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)

        self.events.put(MarketEvent())

    def get_latest_bar(self, symbol):
        return self.latest_symbol_data[symbol][-1]

    def get_latest_bars(self, symbol, N=1):

        return self.latest_symbol_data[symbol][-N:]

    def get_bar_values(self, symbol, key, N):
        bars = None
        if N <= len(self.latest_symbol_data[symbol]):
            bars = np.array(
                [getattr(b[1], key) for b in self.get_latest_bars(symbol, N)]
            )
        return bars

    def get_latest_bar_value(self, symbol, key):
        val = getattr(self.get_latest_bar(symbol)[1], key)
        if isnan(val):
            val = 0
        return val

    def get_latest_bar_datetime(self, symbol):
        return self.latest_symbol_data[symbol][-1][0]


# if __name__ == "__main__":
#     dh = DataHandler("2015-01-01")

#     # print(dh.data)
#     count = 0

#     while True:
#         count += 1
#         print(count)
#         if dh.finished == False:
#             dh.update_bars()
#         else:
#             print(dh.latest_data)
#             break

