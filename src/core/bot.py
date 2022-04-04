import logging
import os
from typing import Final
from datetime import datetime

import discord
from discord.ext import commands
from databases import Database
from exts.helpers import Config, color_resolver
from exts._logging import LoggingHandler
from .context import AsahiContext
from humanize import naturaldate

class Asahi(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        for logger in [
            "asahi",
            "discord.client",
            "discord.gateway",
            "discord.http",
            "discord.ext.commands.core",
            "database"
        ]:
            logging.getLogger(logger).setLevel(logging.DEBUG if logger == "asahi" else logging.INFO)
            logging.getLogger(logger).addHandler(LoggingHandler())
        super().__init__(
            command_prefix=self.get_prefix,
            intents=discord.Intents.all(),
            *args,
            **kwargs
        )
        self.db: Final[Database] = Database("sqlite:///src/core/data/asahi.db")
        self.config: Final[Config] = Config()
        self.owner_ids: set[int] = set(self.config.get("owner_ids"))
        self.prefixes: dict[int, str] = {}
        self.ok_color: Final[int] = color_resolver(self.config.get("ok_color"))
        self.info_color: Final[int] = color_resolver(self.config.get("info_color"))
        self.error_color: Final[int] = color_resolver(self.config.get("error_color"))
        self.logger = logging.getLogger("asahi")
        self.startup_time: Final[datetime] = datetime.now()

    async def on_message(self, msg: discord.Message):
        await self.invoke(await self.get_context(msg, cls=AsahiContext))
    
    async def on_connect(self) -> None:
        self.logger.info("Finished establishing gateway connection(s).")

    async def on_ready(self) -> None:
        self.logger.info(f"{self.user} is now ready.")

    async def startup(self):
        """Startup entry"""
        self.logger.info("Starting Asahi now.")
        self.logger.info(f"Time: {self.startup_time.strftime('%m/%d/%Y %H:%M')}")
        await self.db_entry()
        for ext in os.listdir("src/cogs"): # Cog loading process
            if ext.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{ext[:-3]}")
                    self.logger.info(f"Loaded extension: {ext}")
                except commands.ExtensionError as exp:
                    self.logger.error(f"Failed to load {ext} : {exp}")
        
        await self.start(self.config.get("token")) # lgtm

    async def db_entry(self) -> None:
        with open("./src/core/data/schema.sql") as f: # Setup Database
            for line in f.read().split(";;"):
                await self.db.execute(line)
        self.logger.info("Finished Building Database")
        
        for guild, prefix in await self.db.fetch_all("SELECT guild_id, prefix FROM Guild_Settings"):
            self.prefixes.setdefault(guild, prefix)
        self.logger.info("Finished appending prefixes to on-board memory cache")
    
    async def get_prefix(self, msg: discord.Message):
        if not msg.guild or msg.guild.id not in self.prefixes:
            return commands.when_mentioned_or(self.config.get("prefix"))(self, msg)
        else:
            return commands.when_mentioned_or(self.prefixes[msg.guild.id])(self, msg)