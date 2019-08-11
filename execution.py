from data import DataHandler
from portfolio import Portfolio
from stratergy import Stratergy
from event import FillEvent, OrderEvent


class ExecutionHandler:
    def __init__(self, events):
        """
            takes an order and fills it. acts as a simulated brokerage
        """
        self.events = events

    def execute_order(self, event):
        """
            for testing there is no slipage or fees to start
        """
        fill = FillEvent(
            symbol=event.symbol,
            quantity=event.quantity,
            direction=event.direction,
            fill_cost=None,
        )
        self.events.put(fill)


# if __name__ == "__main__":

#     historicData = DataHandler()
#     portfolio = Portfolio(historicData)
#     stratergy = Stratergy(historicData)
#     simpleExecution = ExecutionHandler()
#     count = 0
#     while True:
#         count += 1
#         # Get market event/data
#         if historicData.finished == False:
#             historicData.update_bars()
#         else:
#             break

#         # Handle processing of new market data
#         portfolio.update()
#         signal = stratergy.calculate_signal()
#         print("signal : ", signal)
#         order = portfolio.handle_signal(signal)
#         fill = simpleExecution.execute_order(order)
#         portfolio.process_fill(fill)
