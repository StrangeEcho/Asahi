from __future__ import annotations

import logging
import os
import typing as t

import aiohttp
import disnake
import pomice
from databases import Database
from datetime import datetime
from disnake.ext import commands

from helpers.confighandler import Config
from helpers.loghandler import LoggingHandler
from exts.functions import color_convert
from .context import KurisuContext
from .database import PrefixManager


class Kurisu(commands.AutoShardedBot):
    """Custom subclass for added functionality"""

    def __init__(self, *args, **kwargs):
        for logger in [
            "kurisu",
            "disnake.client",
            "disnake.gateway",
            "disnake.http",
            "disnake.ext.commands.core",
            "listeners",
            "main",
        ]:
            logging.getLogger(logger).setLevel(logging.DEBUG if logger == "kurisu" else logging.INFO)
            logging.getLogger(logger).addHandler(LoggingHandler())
        super().__init__(command_prefix=self.get_prefix, intents=disnake.Intents.all(), *args, **kwargs)
        self.prefixes = {}
        self.logger = logging.getLogger("kurisu")
        self._config = Config()
        self._db = Database("sqlite:///db/database.db")
        self._session = aiohttp.ClientSession()
        self.logger = logging.getLogger("kurisu")
        self.owner_ids = self.config.get("owner_ids") or super().owner_ids
        self.ok_color = color_convert(self._config.get("ok_color"))
        self.info_color = color_convert(self._config.get("info_color"))
        self.error_color = color_convert(self._config.get("error_color"))
        self.executed_commands = 0
        self._node_pool = pomice.NodePool()
        self.start_time = datetime.now()

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

    async def get_prefix(self, message: disnake.Message) -> t.List[str]:
        """
        Called after every message to check if a command is being called
        """
        if not message.guild or message.guild.id not in self.prefixes.keys():
            return commands.when_mentioned_or(self.config.get("prefix"))(self, message)
        else:
            return commands.when_mentioned_or(self.prefixes[message.guild.id])(self, message)

    async def on_connect(self) -> None:
        self.logger.info(f"Logged in as {self.user}")

    async def on_ready(self) -> None:
        self.logger.info("Ready!")

    async def on_message(self, message: disnake.Message) -> None:
        await self.invoke(await self.get_context(message, cls=KurisuContext))

    async def database_init(self) -> None:
        with open("./schema.sql") as f:
            await self.db.execute_many(f.read())

        self.logger.info("Finished Building Database")

        try:
            await PrefixManager(self).startup_caching()
        except Exception as e:
            self.logger.critical(f"{e}\nExiting...")
            await self.close()

        self.logger.info("Loaded guild prefixes into cache.")
        self.logger.info("Database Init Finished.")

    def startup(self) -> None:
        self.logger.info("Starting Now!")
        self.loop.create_task(self.database_init())

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
        """
        Unstably closes bot. Prone to restart
        """

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
