import logging
import os

import aiohttp
import discord
import pomice
from databases import Database
from discord.ext import commands
from exts.functions import get_prefix, database_init, color_convert
from helpers.confighandler import Config
from helpers.loghandler import LoggingHandler

from .context import KurisuContext


class Kurisu(commands.AutoShardedBot):
    """Custom subclass for added functionality"""

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
            logging.getLogger(logger).setLevel(logging.DEBUG if logger == "kurisu" else logging.INFO)
            logging.getLogger(logger).addHandler(LoggingHandler())
        super().__init__(command_prefix=get_prefix, intents=discord.Intents.all(), *args, **kwargs)
        self.logger = logging.getLogger("kurisu")
        self._config = Config()
        self._db = Database("sqlite:///src/data/kurisu.db")
        self._session = aiohttp.ClientSession()
        self.logger = logging.getLogger("kurisu")
        self.owner_ids = self.config.get("owner_ids") or super().owner_ids
        self.prefixes = {}
        self.ok_color = color_convert(self._config.get("ok_color"))
        self.info_color = color_convert(self._config.get("info_color"))
        self.error_color = color_convert(self._config.get("error_color"))
        self.executed_commands = 0
        self._node_pool = pomice.NodePool()

    @property
    def config(self) -> Config:
        return self._config

    @property
    def node_pool(self) -> pomice.NodePool:
        return self._node_pool

    @property
    def db(self) -> Database:
        return self._db

    @property
    def session(self) -> aiohttp.ClientSession:
        return self._session

    async def on_connect(self) -> None:
        self.logger.info(f"Logged in as {self.user}")

    async def on_ready(self) -> None:
        self.logger.info("Ready!")

    async def on_message(self, msg: discord.Message) -> None:
        await self.invoke(await self.get_context(msg, cls=KurisuContext))

    def startup(self) -> None:
        self.logger.info("Starting Now!")
        self.loop.create_task(database_init(self))

        self.logger.info("Registering Cogs...")
        for cog in os.listdir("src/cogs"):
            if cog.endswith("py"):
                try:
                    self.load_extension(f"cogs.{cog[:-3]}")
                    self.logger.info(f"Loaded {cog}")
                except commands.ExtensionError as e:
                    self.logger.warning(f"Failed loading {cog}\nError:{e}")
        self.logger.info("Done")

        super().run(self.config.get("token"))

    async def close(self) -> None:
        """Closes bot. Prone to restart"""
        if self._session:
            await self._session.close()
        if self._db.connection:
            await self._db.disconnect()
        for node in list(self.node_pool.nodes.values()):
            for player in list(node.players.values()):
                await player.destroy()
        await super().close()

    async def full_close(self) -> None:
        """
        Does the same exact thing as the close method.
        However cleanly and fully exits without being prone to restart
        """
        await self.close()
        exit(26)
