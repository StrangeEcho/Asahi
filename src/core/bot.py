from datetime import datetime
import os
from typing import Final

import discord
from discord.ext import commands
from databases import Database
from exts.helpers import Config, color_resolver
from .context import AsahiContext

class Asahi(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or("a!"),
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
        self.startup_time = Final[datetime] = datetime.now()

    async def on_message(self, msg: discord.Message):
        await self.invoke(await self.get_context(msg, cls=AsahiContext))
    
    async def on_connect(self) -> None:
        print("Finished establishing gateway connection.")

    async def on_ready(self) -> None:
        print(f"{self.user} now ready!")

    async def startup(self):
        """Startup entry"""
        await self.db_entry()
        for ext in os.listdir("src/cogs"): # Cog loading process
            if ext.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{ext[:-3]}")
                    print(f"Loaded extension: {ext}")
                except commands.ExtensionError:
                    print(f"Failed to load {ext}")
        
        await self.start(self.config.get("token")) # lgtm

    async def db_entry(self) -> None:
        with open("./src/core/data/schema.sql") as f: # Setup Database
            for line in f.read().split(";;"):
                await self.db.execute(line)
        
        for guild, prefix in await self.db.fetch_all("SELECT guild_id, prefix FROM Guild_Settings"):
            self.prefixes.setdefault(guild, prefix)