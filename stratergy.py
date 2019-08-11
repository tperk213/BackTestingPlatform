from data import DataHandler


class Stratergy:
    def __init__(self, data):
        self.data = data

    def calculate_signal(self):

        interested_bar_vals = self.data.get_bar_values("adj_close", N=2)
        if len(interested_bar_vals) > 0:
            current_val = interested_bar_vals[-1]
            previous_val = interested_bar_vals[-2]

            if current_val > previous_val:
                signal = "BUY"
            elif current_val < previous_val:
                signal = "SELL"
            else:
                signal = "NONE"
        else:
            signal = "NONE"

        return signal


if __name__ == "__main__":

    historicData = DataHandler()
    # portfolio = Portfolio(historicData)
    stratergy = Stratergy(historicData)
    count = 0
    while True:
        count += 1
        # Get market event/data
        if historicData.finished == False:
            historicData.update_bars()
        else:
            break

        # Handle processing of new market data
        signal = stratergy.calculate_signal()
        print("signal : ", signal)
        # portfolio.update()
