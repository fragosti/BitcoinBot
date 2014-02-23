import time
import sys, traceback
from async import run_async
from research import *


class Bot:

    def __init__(self, algorithm, pair="btc_usd", volatile_mode=False):
        self.algorithm = algorithm
        self.pair = pair
        self.research = algorithm.research
        self.volatile_mode = volatile_mode
        self._trade = True

    def trade(self):
        cur_pair = self.pair
        if self.volatile_mode:
            cur_pair = self.research.getMostVolatile()[0]
        print self.algorithm.decide(cur_pair)

    @run_async
    def start(self):
        self._trade = True
        while self._trade:
            try:
                self.trade()
                time.sleep(10)
            except:
                traceback.print_exc(file=sys.stdout)
                print "Something has gone wrong"
                break
        return

    def stop(self):
        self._trade = False
        return





