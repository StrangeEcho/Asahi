import logging
import os

import discord
from databases import Database
from discord.ext import commands
from exts.functions import get_prefix, database_init, color_convert
from helpers.confighandler import Config
from helpers.loghandler import LoggingHandler


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
        self.logger = logging.getLogger("kurisu")
        self.owner_ids = self.config.get("owner_ids") or super().owner_ids
        self.prefixes = {}
        self._db = Database("sqlite:///src/data/kurisu.db")
        self.ok_color = color_convert(self._config.get("ok_color"))
        self.info_color = color_convert(self._config.get("info_color"))
        self.error_color = color_convert(self._config.get("error_color"))
        
    @property
    def config(self) -> Config:
        return self._config

    @property
    def db(self) -> Database:
        return self._db

    async def on_connect(self) -> None:
        self.logger.info(f"Logged in as {self.user}")

    async def on_ready(self) -> None:
        self.logger.info("Ready!")

    async def on_message(msg: discord.Message) -> None:
        await self.invoke(await self.get_context(msg))

    def startup(self) -> None:
        self.logger.info("Starting Now!")
        self.loop.create_task(database_init(self))
        self.logger.info("Registering Cogs...")

        loaded = 0
        unloaded = 0

        for cog in os.listdir("src/cogs"):
            if cog.endswith("py"):
                try:
                    self.load_extension(f"cogs.{cog[:-3]}")
                    self.logger.info(f"Loaded {cog}")
                    loaded += 1
                except commands.ExtensionError as e:
                    self.logger.warning(f"Failed loading {cog}\nError:{e}")
                    unloaded += 1

        self.logger.info("Done")
        self.logger.info(f"Loaded Cogs: {loaded}")
        self.logger.warn(f"Unloaded Cogs {unloaded}") if unloaded > 0 else self.logger.info(f"Unloaded Cogs {unloaded}")
        super().run(self.config.get("token"))
