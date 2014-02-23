from bot import tradingapi_base
import btceapi
import settings
from btceapi import common

class BTCESimulationApi():
    #handler = btceapi.KeyHandler(settings.key_file, resaveOnDeletion=True)
    #adaptedAPI = btceapi.TradeAPI(self.handler.getKeys()[0],handler)

    all_pairs = common.all_pairs
    all_currencies = common.all_currencies

    def __init__(self, handler):
        self.handler = handler
        self.adaptedAPI = btceapi.TradeAPI(self.handler.getKeys()[0], self.handler)

    @staticmethod
    def getDepth(pair):
        return btceapi.getDepth(pair, settings.connection)

    @staticmethod
    def getTradeFee(pair):
        return btceapi.getTradeFee(pair, settings.connection)

    def buy(self,pair, price, amount):
        ticker = BTCESimulationApi.getTicker(pair)
        buy_price = ticker.last
        buy_amount = amount/buy_price
        return self.adaptedAPI.trade(pair, "buy", buy_price, buy_amount, settings.connection)

    def sell(self,pair, price, amount):
        ticker = BTCESimulationApi.getTicker(pair)
        sell_price = ticker.last
        sell_amount = amount/sell_price
        return self.adaptedAPI.trade(pair, "sell", sell_price, sell_amount, settings.connection)

    @staticmethod
    def getTicker(pair):
        return btceapi.getTicker(pair, settings.connection)

    def getAccountInfo(self):
        return self.adaptedAPI.getInfo(settings.connection)

    def cancelOrder(self, order_id):
        return self.adaptedAPI.cancelOrder(order_id,settings.connection)

    def activeOrders(self, pair):
        return self.adaptedAPI.activeOrders(pair, settings.connection)