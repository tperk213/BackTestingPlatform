from data import DataHandler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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

    # Stats section

    def create_equit_curve(self):
        curve = pd.DataFrame(self.holdings)
        curve.set_index("datetime")
        curve["returns"] = curve["total"].pct_change()
        curve["equity_curve"] = (1.0 + curve["returns"]).cumprod()
        self.equity_curve = curve

    def create_sharp_ratio(self, returns, periods=252):
        """
            returns is a pandas series of percentage returns
            periods can be daily 252, hourly 252*6.5, minutely 252*6.5*60
        """
        return np.sqrt(periods) * (np.mean(returns) / np.std(returns))

    def create_drawdowns(self, pnl):
        """
            keeps track of the largest peak-to-trough drawdown of the Pnl curve and duration of drawdone
            Pnl is a pandas series of percentage returns
        """

        hwm = [0]
        drawdown = pd.Series(index=pnl.index)
        duration = pd.Series(index=pnl.index)

        for t in range(1, len(pnl.index)):
            hwm.append(max(hwm[t - 1], pnl[t]))
            drawdown[t] = hwm[t] - pnl[t]
            duration[t] = 0 if drawdown[t] == 0 else duration[t - 1] + 1

        return drawdown, drawdown.max(), duration.max()

    def output_summary_stats(self):

        self.create_equit_curve()

        total_return = self.equity_curve["equity_curve"].iloc[-1]
        returns = self.equity_curve["returns"]
        pnl = self.equity_curve["equity_curve"]

        sharp_ratio = self.create_sharp_ratio(returns)
        drawdown, max_dd, dd_duration = self.create_drawdowns(pnl)
        self.equity_curve["drawdown"] = drawdown

        stats = [
            ("Total Return", "{}%".format(round((total_return - 1.0) * 100, 2))),
            ("Sharp Ratio", "{}".format(round(sharp_ratio, 2))),
            ("Max Drawdown", "{}".format(round(max_dd * 100, 2))),
            ("Drawdown Duration", "{}".format(dd_duration)),
        ]

        self.equity_curve.to_csv("equity.csv")
        return stats

    def display_results(self):
        # devide figure into 3 parts
        fig = plt.figure()
        ax1 = fig.add_subplot(311)
        ax2 = fig.add_subplot(312)
        ax3 = fig.add_subplot(313)
        self.equity_curve.plot(
            kind="line",
            x="datetime",
            y="equity_curve",
            ax=ax1,
            color="blue",
            legend=False,
            grid=True,
        )
        ax1.set_ylabel("Equity")
        ax1.set_xlabel(None)
        ax1.set_yticks(
            np.arange(
                self.equity_curve["equity_curve"].min(),
                self.equity_curve["equity_curve"].max(),
                0.05,
            )
        )
        self.equity_curve.plot(
            kind="line",
            x="datetime",
            y="returns",
            ax=ax2,
            color="black",
            legend=False,
            grid=True,
        )
        ax2.set_ylabel("returns %")
        ax2.set_xlabel(None)
        ax2_y_step = (
            self.equity_curve["returns"].max() - self.equity_curve["returns"].min()
        ) / 3
        ax2.set_yticks(
            np.arange(
                self.equity_curve["returns"].min(),
                self.equity_curve["returns"].max() + ax2_y_step,
                ax2_y_step,
            )
        )
        self.equity_curve.plot(
            kind="line",
            x="datetime",
            y="drawdown",
            ax=ax3,
            color="red",
            legend=False,
            grid=True,
        )
        ax3.set_ylabel("Drawdown %")
        ax3.set_yticks(
            np.arange(
                self.equity_curve["drawdown"].min(),
                self.equity_curve["drawdown"].max(),
                0.05,
            )
        )
        plt.tight_layout()
        plt.show()


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

