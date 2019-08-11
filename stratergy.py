from data import DataHandler
from event import SignalEvent


class Stratergy:
    def __init__(self, data, events):
        self.data = data
        self.events = events

    def calculate_signal(self):

        interested_bar_vals = self.data.get_bar_values("adj_close", N=2)
        bar_date = self.data.get_latest_bar_datetime()
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
        new_event = SignalEvent(bar_date, signal)
        self.events.put(new_event)

