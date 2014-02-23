import time
from bot import Bot
import settings
import defaults


################
## DEFAULT BOT ## (You can create multiple bots with different settings)
################

bot = Bot(defaults.algorithm, defaults.pair)
bot.start()
print bot._trade
bot.stop()
print bot._trade