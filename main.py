import logging

import discord

from config import TOKEN
from utils.classes import bot

logging.getLogger("main")


if discord.__version__ != "2.0.0a":
    bot.logger.critical(
        f"DISCORD.PY VERSION REQUIREMENT NOT MET. EXPECTED 2.0.0a, GOT {discord.__version__}."
    )
    bot.logger.critical("EXITING!")
    exit(code=1)
else:
    bot.run(TOKEN)
