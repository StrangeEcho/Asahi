import logging

from discord.ext import commands
import discord

from config import BOT_PREFIX, TOKEN
from utils.classes import KurisuBot, PrefixManager
from utils.schema import schema

logging.getLogger("main")


def get_prefix(bot: KurisuBot, msg: discord.Message):
    if not msg.guild or not str(msg.guild.id) in bot.prefixes:
        return commands.when_mentioned_or(BOT_PREFIX)(bot, msg)
    return commands.when_mentioned_or(bot.prefixes.get(str(msg.guild.id)))(bot, msg)


bot = KurisuBot(command_prefix=get_prefix)


if discord.__version__ != "2.0.0a":
    bot.logger.critical(
        f"DISCORD.PY VERSION REQUIREMENT NOT MET. EXPECTED 2.0.0a, GOT {discord.__version__}."
    )
    bot.logger.critical("EXITING!")
    exit(code=1)

pm = PrefixManager(bot=bot)


def DatabaseInit(Schema: str):
    bot.logger.info("Initializing Database...")
    bot.db.execute(Schema)
    bot.logger.info("Schema Execution Complete.")
    bot.logger.info("Attempting To Append Prefixes To On-Memory Cache.")
    try:
        pm.startup_caching()
    except Exception as e:
        bot.logger.critical(
            f"Error While Appending Guild Prefixes To Database.\nError: {e}\nExiting..."
        )
        exit(code=1)
    bot.logger.info("Guild Prefixes Successfully Appended To On-Memory Cache.")
    bot.logger.info("Database Initialization Complete.")


DatabaseInit(schema)
bot.logger.info("Running Kurisu Now!")
bot.run(TOKEN)
