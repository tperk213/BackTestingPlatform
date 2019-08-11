from dataHandler import DataHandler


class Portfolio:
    """
        stores
        holdings: array of dict that store date and cash
            [
                {"datetime": start_date, "cash":starting cash, "stock_value":0},
                {"datetime": timestamp, "cash":current cash on hand, "stock_vale": current stock value},
                ...
                {"datetime": end_date, "cash":final cash}
            ]
        current_holdings: dict of current holdings no datetime 
                            a single entry to holdings
            {
                "cash":
                "stock_value":
                "total":
            }
        positions: array of dict that store date and stock held
            [
                {"datetime": start_date, "position":0},
                {"datetime": timestamp, "position":current position held},
                ...
                {"datetime": end_date, "positon":final value of position}
            ]
        current_positions: dict of stock position
            {
                "stock": amount of stock int
            }
    """

    def __init__(self, dataHandler, starting_capital=100000):

        self.dataHandler = dataHandler

        # Holdings init
        self.holdings = [
            {
                "datetime": dataHandler.start_date,
                "cash": starting_capital,
                "stock_value": 0,
                "total": starting_capital,
            }
        ]
        self.current_holdings = {
            "datetime": dataHandler.start_date,
            "cash": starting_capital,
            "stock_value": 0,
            "total": starting_capital,
        }

        # positions init
        self.positions = [{"datetime": dataHandler.start_date, "stock": 0}]

        self.current_positions = {"stock": 0}

    def update(self):
        timestamp = self.dataHandler.get_latest_bar()[0]

        # avoids duplicating the first entry
        if timestamp != self.dataHandler.start_date:

            # update positions
            self.positions.append(
                {"datetime": timestamp, "stock": self.current_positions["stock"]}
            )

            # update holdings
            temp_holdings = {
                "datetime": timestamp,
                "cash": self.current_holdings["cash"],
                "stock_value": 0,
                "total": self.current_holdings["cash"],
            }

            temp_holdings["stock_value"] = self.current_positions[
                "stock"
            ] * self.dataHandler.get_latest_bar_value("adj_close")

            temp_holdings["total"] += temp_holdings["stock_value"]
            self.current_holdings["total"] = temp_holdings["total"]

            self.holdings.append(temp_holdings)

    def handle_signal(self, signal):
        """
            signal is string "BUY" or "SELL"
            return order dict of
                quantity
                signal
        """
        mkt_quantity = 100
        cur_quantity = self.current_positions["stock"]

        if signal == "BUY":
            order = {"quantity": mkt_quantity, "signal": "BUY"}
        elif signal == "SELL":
            order = {"quantity": cur_quantity, "signal": "SELL"}
        else:
            order = {"quantity": 0, "signal": "None"}
        return order

    def update_positions_from_fill(self, fill_order):
        fill_direction = 0
        if fill_order["signal"] == "BUY":
            fill_direction = 1
        if fill_order["signal"] == "SELL":
            fill_direction = -1

        self.current_positions["stock"] += fill_direction * fill_order["quantity"]

    def update_holdings_from_fill(self, fill_order):
        fill_direction = 0
        if fill_order["signal"] == "BUY":
            fill_direction = 1
        if fill_order["signal"] == "SELL":
            fill_direction = -1

        fill_cost = self.dataHandler.get_latest_bar_value("adj_close")
        cost = fill_direction * fill_cost * fill_order["quantity"]

        self.current_holdings["stock_value"] = self.current_positions[
            "stock"
        ] * self.dataHandler.get_latest_bar_value("adj_close")
        self.current_holdings["cash"] -= cost

    def process_fill(self, fill_order):
        """
            updates the portfolio based on the fill order that comes from execution
        """
        if fill_order["signal"] != "None":
            self.update_positions_from_fill(fill_order)
            self.update_holdings_from_fill(fill_order)


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

