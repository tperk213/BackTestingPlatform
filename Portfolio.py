from dataHandler import DataHandler


class Portfolio:
    """
        stores
        holdings: array of dict that store date and cash
            [
                {"datetime": start_date, "cash":starting cash},
                {"datetime": timestamp, "cash":current cash on hand},
                ...
                {"datetime": end_date, "cash":final cash}
            ]
        positions: array of dict that store date and stock held
            [
                {"datetime": start_date, "position":0},
                {"datetime": timestamp, "position":current position held},
                ...
                {"datetime": end_date, "positon":final value of position}
            ]
    """

    def __init__(self, dataHandler, starting_capital=100000):

        self.holdings = [{"datetime": dataHandler.start_date, "cash": starting_capital}]
        self.positions = [{"datetime": dataHandler.start_date, "stock": 0}]
        self.dataHandler = dataHandler

    def update(self):
        timestamp = self.dataHandler.get_latest_bar()[0]
        if timestamp != self.dataHandler.start_date:
            self.holdings.append(
                {"datetime": timestamp, "cash": self.holdings[-1]["cash"]}
            )
            self.positions.append(
                {"datetime": timestamp, "stock": self.positions[-1]["stock"]}
            )


if __name__ == "__main__":

    historicData = DataHandler()
    portfolio = Portfolio(historicData)

    count = 0
    while True:
        count += 1
        # Get market event/data
        if historicData.finished == False:
            historicData.update_bars()
        else:
            break

        # Handle processing of new market data
        portfolio.update()

