from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp

if TYPE_CHECKING:
    from kurisu import Kurisu
from data.database import SCHEMA, PrefixManager

import discord
from discord.ext.commands import when_mentioned_or


def get_prefix(bot: Kurisu, msg: discord.Message):
    if not msg.guild or msg.guild.id not in bot.prefixes.keys():
        return when_mentioned_or(bot.config.get("prefix"))(bot, msg)
    else:
        return when_mentioned_or(bot.prefixes[msg.guild.id])(bot, msg)


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


def color_convert(color: str) -> int:
    """Convert colors from config file"""

    if color.startswith("0x"):
        return color
    else:
        return int(color.replace("#", "0x"), 16)


async def get_ud_results(term: str, max: int = 5):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.urbandictionary.com/v0/define?term={term}") as resp:
            try:
                return (await resp.json())["list"][:max]
            except (IndexError, KeyError):
                pass
    await session.close()
