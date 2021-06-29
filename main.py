from utils.classes import HimejiBot
from config import TOKEN

import logging

import discord

logging.getLogger("main")

bot = HimejiBot()

if discord.__version__ != "2.0.0a":
    bot.logger.critical(f"DISCORD.PY VERSION REQUIREMENT NOT MET. EXPECTED 2.0.0a, GOT {discord.__version__}.")
    bot.logger.critical("EXITING!")
    exit(code=1)
else:
    bot.run(TOKEN)

