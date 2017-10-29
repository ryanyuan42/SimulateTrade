from Trade import Event
from threading import Thread
import math
from WindPy import *
from util import position_parser, start

SecurityCode = 'SecurityCode'
TradeSide = 'TradeSide'
OrderPrice = 'OrderPrice'
OrderVolume = 'OrderVolume'
Option = 'Option'
CASH = 'CASH'


class Model:
    def __init__(self):
        pass

    def fit(self):
        pass

    def predict(self, feed):
        pass


class Strategy:
    def __init__(self, trading_engine=None):
        self.LogonID = '1'
        self.current_position = None
        self.total_asset = None
        self.active = False
        self.trading_engine = trading_engine
        self.thread = Thread(target=self.run)

    def generate_trade_info(self, feed):
        # if not feed:
        #     return []
        m = Model()
        prediction = m.predict(feed)
        # By prediction, we can get our desired position
        target_position = self.calc_position(prediction)

        # FIXME: This is only for testing.
        target_position = {'CASH': 1}
        old_position = {k: self.current_position[k] / self.total_asset for k in self.current_position}
        trade_info = self.position_change(old_position, target_position)
        trade_info_lst = [(key, trade_info[key]) for key in trade_info]
        trade_info_lst = sorted(trade_info_lst, key=lambda x: x[1])
        return trade_info_lst

    def before_trading(self):
        # update necessary account information
        self.current_position = self.get_current_position()
        self.total_asset = sum([self.current_position[ticker] for ticker in self.current_position])

    @staticmethod
    def get_price(ticker):
        price_res = w.wsq(ticker, "rt_last")
        return price_res.Data[0][0]

    def generate_events(self, feed):
        trade_info_lst = self.generate_trade_info(feed)
        # Now we start generate event to put into trade engine
        total_money = self.total_asset
        for t in trade_info_lst:
            ticker, diff = t[0], t[1]
            if ticker == CASH:
                continue
            option = "OrderType=BOP"
            price = self.get_price(ticker)
            if diff < 0:
                trade_side = 'Sell'
                order_price = 0
                order_volume = round(-(total_money * diff) / price, -2)
                event_dict = {SecurityCode: ticker,
                              TradeSide: trade_side,
                              OrderPrice: order_price,
                              OrderVolume: order_volume,
                              Option: option}
                event = Event(type_="order", dictionary=event_dict)
                yield event
            elif diff > 0:
                trade_side = 'Buy'
                order_price = 0
                order_volume = round((total_money * diff) / price, -2)
                event_dict = {SecurityCode: ticker,
                              TradeSide: trade_side,
                              OrderPrice: order_price,
                              OrderVolume: order_volume,
                              Option: option}
                event = Event(type_="order", dictionary=event_dict)
                yield event

    def run(self):
        pass

    def calc_position(self, scores):
        pass

    @staticmethod
    def position_change(old_position, new_position):
        """

        Old position                             New Position
        A 1/4 (money / total)                    X 1/5
        B 1/4 (money / total)                    A 1/5
        C 1/4 (money / total)                    B 1/5
        D 1/4 (money / total)                    D 1/5
                                                 E 1/5


        :param old_position: dict, contains keys as ticker and values as weights
        :param new_position: dict, contains keys as ticker and values as weights
        :return:
        """
        trade_info = dict()
        for ticker in old_position:
            if ticker in new_position:
                diff = new_position[ticker] * 1 - old_position[ticker] * 1
            else:
                # used to exist but now is gone
                diff = -old_position[ticker] * 1
            trade_info[ticker] = diff

        for ticker in new_position:
            if ticker not in old_position:
                diff = new_position[ticker] * 1
                trade_info[ticker] = diff

        return trade_info

    def get_current_position(self):
        position_res = w.tquery("Position", "LogonID=%s" % self.LogonID)
        position = position_parser(position_res)

        SecurityCodes = position['SecurityCode']
        HoldingValues = position['HoldingValue']
        capital_res = w.tquery("Capital", "LogonID=%s" % self.LogonID)
        capital = position_parser(capital_res)
        AvailableFund = capital['AvailableFund'][0]

        old_position = dict()
        for ticker, value in zip(SecurityCodes, HoldingValues):
            old_position[ticker] = value
        old_position[CASH] = AvailableFund
        return old_position

    def start(self):
        self.active = True
        self.thread.run()

    def stop(self):
        self.active = False
        self.thread.join()

    @staticmethod
    def round_down(x):
        return int(math.floor(x / 100)) * 100
if __name__ == "__main__":
    start()
    a = Strategy(trading_engine=None)
    a.before_trading()
    for event in a.generate_events(feed=None):
        print(event.dict)
