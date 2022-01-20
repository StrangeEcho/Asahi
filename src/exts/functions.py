from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu.bot import Kurisu
from data.database import SCHEMA, PrefixManager

from discord import Message


def get_prefix(bot: Kurisu, msg: Message):
    if not msg.guild or msg.guild.id not in bot.prefixes.keys():
        return bot.config.get("prefix")
    else:
        return bot.prefixes[msg.guild.id]


async def database_init(bot: Kurisu, schema=SCHEMA):
    for i in schema.split(";;"):
        await bot.db.execute(i)
    bot.logger.info("Finished Building Database")
    try:
        await PrefixManager(bot).startup_caching()
    except Exception as e:
        bot.logger.critical(f"{e}\nExiting...")
        await bot.close()
    bot.logger.info("Loaded guild prefixes into memory.")
    bot.logger.info("Database Init Finished.")
