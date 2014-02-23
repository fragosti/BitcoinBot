from wrappers import simwrapper
from algorithms import *

import btceapi
################
# Bot Settings #
################

pair = "ppc_usd"

sleep_time = 10

volatility_mode = False

key = "AZGRIZYJ-H8VRF495-34H6CAF4-9UWI56WI-74U0063R"
secret = "71eb80d6e1b60f4df6ae413cf36b44d1cdd30238fe82ef5a09416cfbb44e059e"

handler = btceapi.KeyHandler(resaveOnDeletion=True)
handler.addKey(key, secret, 1)

api = simwrapper.BTCESimulationApi(handler)

algorithm = BasicAlgo(api)