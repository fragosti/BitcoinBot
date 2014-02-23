from abc import ABCMeta, abstractmethod


class TradingApi:
    """ An interface for a trading API.
    If you write an API extend this class
    and implement the methods.
    Alternatively if you are using an API,
    use a wrapper class that extends this class.
    This makes the whole program more flexible.
    Despite duck typing, extending this class
    will make sure that you can apply a new API
    to past algorithm and research classes.

    """
    __metaclass__ = ABCMeta

    @staticmethod
    def getDepth(pair):
        pass

    @staticmethod
    def getTradeFee():
        pass

    @staticmethod
    def buy(pair, price, amount):
        pass

    @staticmethod
    def sell(pair, price, amount):
        pass

    @staticmethod
    def getTicker(pair):
        """ Return a dictionary/struct/object of attributes"""
        pass

    @staticmethod
    def getAccountInfo():
        pass

    @staticmethod
    def cancelOrder(order_id):
        pass

    @staticmethod
    def activeOrders(pair):
        pass

