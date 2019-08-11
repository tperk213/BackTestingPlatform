import pandas as pd


class DataHandler:
    """
        Holds the data frame of the current and future bar info
    """

    def __init__(self, start_date=None, end_date=None):

        # data is stored as an iterator of form
        # (index, row)
        # row is a dict i belive with keys of column names
        # bar will be of form
        # (index, row)
        self.data = pd.read_csv(
            "E:\\Code\\EventDrivenTrading\\stock_dfs\\AAPL.csv",
            header=0,
            index_col=0,
            parse_dates=True,
            names=["datetime", "open", "high", "low", "close", "volume", "adj_close"],
        )

        if start_date is not None:
            self.data = self.data.loc[start_date:]
        self.start_date = self.data.first_valid_index()

        if end_date is not None:
            self.data = self.data.loc[:end_date]
        print(self.data)
        self.data = self.data.iterrows()

        self.latest_data = []
        self.finished = False

    def _get_new_bar(self):
        # b is of form
        # (index, row)
        # row is a dict i belive with keys of column names
        for b in self.data:
            yield b

    def update_bars(self):
        try:
            bar = next(self._get_new_bar())
            # bar is of form
            # (index, row)
            # row is a dict i belive with keys of column names
        except StopIteration:
            print("finished backtest")
            self.finished = True
        else:
            if bar is not None:
                self.latest_data.append(bar)

    def get_latest_bar(self):
        return self.latest_data[-1]


if __name__ == "__main__":
    dh = DataHandler("2015-01-01")

    # print(dh.data)
    count = 0

    while True:
        count += 1
        print(count)
        if dh.finished == False:
            dh.update_bars()
        else:
            print(dh.latest_data)
            break

