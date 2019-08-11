from data import DataHandler
from portfolio import Portfolio
from stratergy import Stratergy
from execution import ExecutionHandler
import queue


if __name__ == "__main__":

    events = queue.Queue()
    historicData = DataHandler(events)
    portfolio = Portfolio(historicData, events)
    stratergy = Stratergy(historicData, events)
    simpleExecution = ExecutionHandler(events)

    count = 0
    while True:
        count += 1
        # Get market event/data
        if historicData.finished == False:
            historicData.update_bars()
        else:
            break

        # handle events in que
        while True:

            # get event from queue
            try:
                event = events.get(False)
            except queue.Empty:
                break
            else:

                if event is not None:
                    # switch on event type
                    if event.type == "MARKET":
                        # Handle processing of new market data
                        stratergy.calculate_signal()
                        portfolio.update()
                    elif event.type == "SIGNAL":
                        portfolio.handle_signal(event)

                    elif event.type == "ORDER":
                        simpleExecution.execute_order(event)
                    # print("signal : ", signal)
                    elif event.type == "FILL":
                        portfolio.process_fill(event)

    stats = portfolio.output_summary_stats()
    print(stats)
    portfolio.display_results()
