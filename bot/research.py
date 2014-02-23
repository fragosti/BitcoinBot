import btceapi
from operator import itemgetter


class Research:
    
    def __init__(self, api):
        self.api = api

    def getVolatilityOrder(self):
        tst = []
        for pair in self.api.all_pairs:
            ticker = self.api.getTicker(pair)
            tst.append((pair, ticker.high / ticker.low))
        return sorted(tst, key=itemgetter(1))

    def getMostVolatile(self):
        return self.getVolatilityOrder()[-1]

    def is_high(self, pair):
        ticker = self.api.getTicker(pair)
        return ticker.last > ticker.avg

    def is_low(self, pair):
        ticker = self.api.getTicker(pair)
        return ticker.last < ticker.avg

    def should_buy(self, pair):
        if self.is_high(pair):
            return False
        ticker = self.api.getTicker(pair)
        fee = self.api.getTradeFee(pair)
        last = ticker.last
        avg = ticker.avg
        pot_profit = ((last*last)/(avg*avg) - 1)
        return pot_profit > fee

    def should_sell(self, pair):
        if self.is_low(pair):
            return False
        ticker = self.api.getTicker(pair)
        fee = self.api.getTradeFee(pair)
        last = ticker.last
        avg = ticker.avg
        pot_profit = ((avg*avg)/(last*last)- 1)
        return pot_profit > fee
