from data import DataHandler
from portfolio import Portfolio
from stratergy import Stratergy
from execution import ExecutionHandler


if __name__ == "__main__":

    historicData = DataHandler()
    portfolio = Portfolio(historicData)
    stratergy = Stratergy(historicData)
    simpleExecution = ExecutionHandler()
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
        signal = stratergy.calculate_signal()
        # print("signal : ", signal)
        order = portfolio.handle_signal(signal)
        fill = simpleExecution.execute_order(order)
        portfolio.process_fill(fill)
    stats = portfolio.output_summary_stats()
    print(stats)
    portfolio.display_results()
