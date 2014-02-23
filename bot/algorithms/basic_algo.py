from algorithmbase import Algorithm
from bot.research import Research


class BasicAlgo(Algorithm):
    """
    Algorithm should only be concerned with getting max profit
    from given pair.
    """
    def __init__(self, api, trade_amount=10,ceiling = 10, floor=10, abs_ceiling=5, abs_floor=3):
        self.api = api
        self.research = Research(api)
        self.trade_amount = trade_amount
        self.ceiling = ceiling
        self.floor = floor
        self.abs_ceiling = abs_ceiling
        self.abs_floor = abs_floor

    def decide(self, pair):
        message = "did not trade"
        if self.research.should_buy(pair):
            self.api.buy(pair, 0, self.trade_amount)
            message = "bought "+pair+ " for " + str(self.trade_amount)
        if self.research.should_sell(pair):
            self.api.sell(pair, 0, self.trade_amount)
            message = "sold " + str(self.trade_amount) + "of " + pair
        return message
