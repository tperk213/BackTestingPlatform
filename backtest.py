import queue
from my_utils import params_to_attr


class Backtest:
    @params_to_attr
    def __init__(
        self,
        csv_dir,
        symbol_list,
        inital_capital,
        start_date,
        end_date,
        data_handler_cls,
        execution_handler_cls,
        portfolio_cls,
        stratergy_cls,
    ):

        self.events = queue.Queue()

        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

        self._generate_trading_instances()

    def _generate_trading_instances(self):
        print("Creating DataHandler, Stratergy, Portfolio")
        self.data_handler = self.data_handler_cls(
            self.events, self.csv_dir, self.symbol_list, self.start_date, self.end_date
        )
        self.portfolio = self.portfolio_cls(self.data_handler, self.events)
        self.stratergys = [self.stratergy_cls(self.data_handler, self.events)]
        self.execution_handler = self.execution_handler_cls(self.events)

    def _run_backtest(self):
        count = 0
        while True:
            count += 1
            # Get market event/data
            if self.data_handler.finished == False:
                self.data_handler.update_bars()
            else:
                break

            # handle events in que
            while True:

                # get event from queue
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:

                    if event is not None:
                        # switch on event type
                        if event.type == "MARKET":
                            # Handle processing of new market data
                            for s in self.stratergys:
                                s.calculate_signal()
                            self.portfolio.update()
                        elif event.type == "SIGNAL":
                            self.signals += 1
                            self.portfolio.handle_signal(event)

                        elif event.type == "ORDER":
                            self.orders += 1
                            self.execution_handler.execute_order(event)
                        # print("signal : ", signal)
                        elif event.type == "FILL":
                            self.fills += 1
                            self.portfolio.process_fill(event)

    def _output_performance(self):
        print("Signals : {}".format(self.signals))
        print("Orders : {}".format(self.orders))
        print("Fills : {}".format(self.fills))

        stats = self.portfolio.output_summary_stats()
        print(stats)
        self.portfolio.display_results()

    def simulate_trading(self):
        self._run_backtest()
        self._output_performance()
