from WindPy import *
import time
from collections import defaultdict
from threading import Thread
from queue import Queue, Empty


ORDER = 'ORDER'
INORDER = 'INORDER'
STOCK = 'STOCK'
TRADESIDE = 'TRADESIDE'
ORDERPRICE = 'ORDERPRICE'
ORDERVOLUME = 'ORDERVOLUME'
# What is the process of trading?
# You get some information, You trade based on that information,
# And then you listen, you wait and trade on that information.

# So I can have two threads, one thread is listening and trading
# Another thread is going to do the strategy and send out the information about trading.
# I am going to first complete the listening one.

# Credit to VNPY. I basically copy the code from this project.

# This Engine will start and listen to all the events that is sending out from the other application
# There should be only two types of events, they are:
# 下单， 撤单


class TradeEngine:
    def __init__(self):
        self.queue = Queue()
        self.active = False
        self.thread = Thread(target=self.run)
        self.handlers = defaultdict(list)

    def run(self):
        while self.active:
            try:
                event = self.queue.get(block=True, timeout=1)
                self.process(event)
            except Empty:
                pass

    def process(self, event):
        if event.type_ in self.handlers:
            for handler in self.handlers[event.type_]:
                handler(event)

    def register(self, type_, handler):
        handler_list = self.handlers[type_]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, type_, handler):
        handler_list = self.handlers[type_]
        if handler in handler_list:
            handler_list.remove(handler)
        if not handler_list:
            del self.handlers[type_]

    def start(self):
        self.active = True
        self.thread.start()

    def stop(self):
        self.active = False
        self.thread.join()

    def put(self, event):
        self.queue.put(event)


class Event:
    """Event Implementation"""
    def __init__(self, type_=None, dictionary=None):
        self.type_ = type_
        self.dict = dictionary


class OtherApp:
    """
    For testing purpose,
    Basically, this app will send out event to my engine.
    And then my engine will try to do it.
    """
    def __init__(self, trading_engine = None):
        self.active = False
        self.trading_engine = trading_engine
        self.thread = Thread(target=self.run)

    def generate_event(self):
        if int(time.time()) % 2 == 0:
            return Event('order')
        else:
            return Event('inorder')

    def run(self):
        while self.active:
            time.sleep(1)
            event = self.generate_event()      # this should be where strategy gives event
            print(self.thread.name + ' putting event into queue')
            self.trading_engine.put(event)

    def start(self):
        self.active = True
        self.thread.run()

    def stop(self):
        self.active = False
        self.thread.join()


def order(event):
    # process the event and then
    assert event.type_ == ORDER, 'event is not type ORDER'
    stocks = event.dict[STOCK]
    trade_side = event.dict[TRADESIDE]
    order_price = event.dict[ORDERPRICE]
    order_volume = event.dict[ORDERVOLUME]
    for stock in stocks:
        w.torder(SecurityCode=stock, TradeSide=trade_side, OrderPrice=order_price, OrderVolume=order_volume)
    print("I\'m ordering stocks")


def inorder(event):
    # process the event and then
    print("I\'m inordering stocks")


if __name__ == "__main__":
    pass
    # engine = TradeEngine()
    # engine.start()
    # # before we get to business, we also need to register handler for order and inorder
    # engine.register(type_='order', handler=order)
    # engine.register(type_='inorder', handler=inorder)
    # app = OtherApp(trading_engine=engine)
    # app.start()
