import asyncio
import logging
import os

from discord.ext import commands
import discord

from utils.classes import KurisuBot, PrefixManager
from utils.schema import schema

logging.getLogger("main")


def get_prefix(bot: KurisuBot, msg: discord.Message):
    if not msg.guild or not str(msg.guild.id) in bot.prefixes:
        return commands.when_mentioned_or(
            bot.get_config("config", "config", "prefix"))(bot, msg)
    return commands.when_mentioned_or(bot.prefixes.get(str(msg.guild.id)))(bot,
                                                                           msg)


bot = KurisuBot(command_prefix=get_prefix)

if discord.__version__ != "2.0.0a":
    bot.logger.critical(
        f"DISCORD.PY VERSION REQUIREMENT NOT MET. EXPECTED 2.0.0a, GOT {discord.__version__}."
    )
    bot.logger.critical("EXITING!")
    exit(code=26)

pm = PrefixManager(bot=bot)


async def DatabaseInit(Schema: str):
    bot.logger.info("Initializing Database...")
    await bot.db.execute(query=Schema)
    bot.logger.info("Schema Execution Complete.")
    bot.logger.info("Attempting To Append Prefixes To On-Memory Cache.")
    try:
        await pm.startup_caching()
    except Exception as e:
        bot.logger.critical(
            f"Error While Appending Guild Prefixes To Database.\nError: {e}\nExiting..."
        )
        exit(code=26)
    bot.logger.info("Guild Prefixes Successfully Appended To On-Memory Cache.")
    bot.logger.info("Database Initialization Complete.")


if not bot.get_config("configoptions", "options", "no_priviledged_owners"):
    for o in bot.get_config("config", "config", "owner_ids"):
        bot.owner_ids.add(o)

asyncio.run(DatabaseInit(schema))
bot.logger.info(f"Starting Kurisu with Process ID {os.getpid()}")
bot.run(bot.get_config("config", "config", "token"))
