from datetime import datetime
import asyncio
import logging
import os

from aiohttp import ClientSession
from databases import Database
from discord.ext import commands, menus
import discord

import configoptions
import config

from .log import LoggingHandler


class EmbedListMenu(menus.ListPageSource):
    """
    Paginated embed menu.
    """

    def __init__(self, data):
        """
        Initializes the EmbedListMenu.
        """
        super().__init__(data, per_page=1)

    async def format_page(self, menu, embeds):
        """
        Formats the page.
        """
        return embeds


class KurisuBot(commands.AutoShardedBot):
    """Idk"""

    def __init__(self, *args, **kwargs):
        for logger in [
            "kurisu",
            "discord.client",
            "discord.gateway",
            "discord.http",
            "discord.ext.commands.core",
            "listeners",
            "main",
        ]:
            logging.getLogger(logger).setLevel(
                logging.DEBUG if logger == "kurisu" else logging.INFO
            )
            logging.getLogger(logger).addHandler(LoggingHandler())
        self.logger = logging.getLogger("kurisu")
        super().__init__(
            help_command=None,
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(roles=False, everyone=False),
            *args,
            **kwargs,
        )
        self.owner_ids = config.OWNER_IDS
        self.ok_color = int(str(f"0x{configoptions.OK_COLOR}").replace("#", ""), base=16)
        self.error_color = int(str(f"0x{configoptions.ERROR_COLOR}").replace("#", ""), base=16)
        self.uptime = None
        self._session = None
        self.startup_time = datetime.now()
        self.version = "2.2.1"
        self.db = Database("sqlite:///kurisu.db")
        self.executed_commands = 0
        self.prefixes = {}

    @property
    def database(self) -> Database:
        return self.db

    @property
    def session(self) -> ClientSession:
        if self._session is None:
            self._session = ClientSession(loop=self.loop)
        return self._session

    async def on_connect(self):
        self.logger.info(f"Logged in as {self.user.name}(ID: {self.user.id})")
        try:
            await self.db.connect()
        except AssertionError:
            pass
        self.logger.info("Connected to the database: `kurisu.db`")

    async def on_ready(self):
        if self.uptime is not None:
            return
        self.uptime = datetime.utcnow()
        self.logger.info(
            f"FINISHED CHUNKING {len(self.guilds)} GUILDS AND CACHING {len(self.users)} USERS",
        )
        self.logger.info(f"Registered Shard Count: {len(self.shards)}")
        bot_owner_usernames = []
        for o in self.owner_ids:
            bot_owner_usernames.append(await self.fetch_user(o))
        self.logger.info("Acknowledged Owner ID(s): " + ", ".join(map(str, bot_owner_usernames)))
        self.logger.info("ATTEMPTING TO MOUNT COG EXTENSIONS!")
        loaded_cogs = 0
        unloaded_cogs = 0
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{cog[:-3]}")
                    self.logger.info(f"Loaded {cog}")
                    loaded_cogs += 1
                except Exception as e:
                    unloaded_cogs += 1
                    self.logger.warning(f"Failed to load the cog: {cog}")
                    self.logger.warning(f"{e}")
        self.logger.info("DONE")
        self.logger.info(f"Total mounted cogs: {loaded_cogs}")
        msg = f"Total unmounted cogs: {unloaded_cogs}"
        self.logger.info(msg) if unloaded_cogs == 0 else self.logger.warning(msg)
        time_difference = ((self.startup_time - datetime.now()) * 1000).total_seconds()
        formatted_time_difference = str(time_difference).replace("-", "")
        self.logger.info(f"Elapsed Time Since Startup: {formatted_time_difference} Ms")
        self.logger.info("STARTUP COMPLETE. READY!")

    # noinspection PyMethodMayBeStatic
    async def on_shard_disconnect(self, shard_id):
        self.logger.warning(f"SHARD {shard_id} IS NOW IN A DISCONNECTED STATE FROM DISCORD")

    async def close(self):
        """Logs out bot and closes any active connections. Method is used to restart bot."""
        await super().close()
        if self._session:
            await self._session.close()
            self.logger.info("HTTP Client Session(s) closed")
        await self.db.disconnect()
        self.logger.info("Database Connection Closed")
        await asyncio.sleep(1)

    async def full_exit(self):
        """Completely kills the process and closes all connections. However, it will continue to restart if being ran with PM2"""
        if self._session:
            await self._session.close()
            self.logger.info("HTTP Client Session Closed.")
        await self.db.disconnect()
        self.logger.info("Database Connection Closed")
        exit(code=26)


class PrefixManager:
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    async def add_prefix(self, guild: int, prefix: str):
        await self.bot.db.execute(
            query="INSERT INTO guildsettings (guild, prefix) VALUES (:guild, :prefix) ON CONFLICT(guild) DO UPDATE SET prefix = :update_prefix",
            values={
                "guild": guild,
                "prefix": prefix,
                "update_prefix": prefix,
            },
        )
        self.bot.prefixes[str(guild)] = prefix

    async def remove_prefix(self, guild: int):
        if str(guild) in self.bot.prefixes:
            self.bot.prefixes.pop(str(guild))
            await self.bot.db.execute(
                query="DELETE FROM guildsettings WHERE guild = :guild_id",
                values={
                    "guild_id": guild,
                },
            )

    async def startup_caching(self):
        for g, p in await self.bot.db.fetch_all(query="SELECT guild, prefix FROM guildsettings"):
            self.bot.prefixes.setdefault(str(g), str(p))
            self.bot.logger.info("Prefixes Appended To Cache")
