from data import DataHandler
from event import SignalEvent
from my_utils import params_to_attr
import datetime


class Stratergy:
    def __init__(self):
        pass

    def calculate_signal(self):
        """
            Is trigered on a market event being put in the event que
            calculates and adds a signal event to the 
            events que based on data and symbol information
        """
        pass


class SimpleStratergy(Stratergy):
    def __init__(self, symbol, data, events):
        """
            Params:
                symbol: list of string symbols that are of interest
                    ["AAPL", "BRW", ]
                data: dataHandler of market data
                    dataHandler object
                events: event queue
                    Queue object

        """
        self.symbol = symbol
        self.data = data
        self.events = events

    def calculate_signal(self):

        interested_bar_vals = self.data.get_bar_values(self.symbol, "adj_close", N=2)
        bar_date = self.data.get_latest_bar_datetime(self.symbol)
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
        new_event = SignalEvent(self.symbol, bar_date, signal, 1)
        self.events.put(new_event)

