import pandas as pd


class DataHandler:
    """
        Holds the data frame of the current and future bar info
    """

    def __init__(self, start_date=None, end_date=None):

        self.data = pd.read_csv(
            "E:\\Code\\EventDrivenTrading\\stock_dfs\\AAPL.csv",
            header=0,
            index_col=0,
            parse_dates=True,
            names=["datetime", "open", "high", "low", "close", "volume", "adj_close"],
        )

        if start_date is not None:
            self.data = self.data.loc[start_date:]
        if end_date is not None:
            self.data = self.data.loc[:end_date]

        self.data = self.data.iterrows()

        self.latest_data = []
        self.finished = False

    def _get_new_bar(self):
        for b in self.data:
            print(b)
            yield b

    def update_bars(self):
        try:
            bar = next(self._get_new_bar())
        except StopIteration:
            print("finished backtest")
            self.finished = True
        else:
            if bar is not None:
                self.latest_data.append(bar)


dh = DataHandler("2015-01-01", "2016-12-28")
print(dh.data)
count = 0
while True:
    count += 1
    print(count)
    if dh.finished == False:
        dh.update_bars()
    else:
        print(dh.latest_data)
        break

