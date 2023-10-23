from datetime import datetime
from typing import Any, Optional
import logging
import os
import tomllib

from discord.ext import commands
import aiosqlite
import discord

from .context import KurisuContext


class ConfigHandler:
    """Core configuration handler for parsing toml config file"""

    def __init__(self):
        with open("./Kurisu/core/config.toml", "rb") as f:
            self.config = tomllib.load(f.read())

    def get(self, config_name: str, category: str = None) -> Optional[Any]:
        """Fetch the specified config from the config.toml file"""
        if category:
            try:
                return self.config[category][config_name]
            except KeyError:
                return None
        return self.config.get(config_name)


class KurisuBot(commands.AutoShardedBot):
    """Subclass adding multiple meta features to the bot"""

    discord.utils.setup_logging(level=logging.INFO)

    def __init__(self):
        super().__init__(
            intents=discord.Intents.all(), command_prefix=self.get_prefix
        )
        self.config = ConfigHandler()
        self.logger = logging.getLogger(__name__)
        self.db = aiosqlite.connect("./Kurisu/core/database/database.db")
        self.ok_color: int = self.config.get("ok_color", "Core")
        self.info_color: int = self.config.get("info_color", "Core")
        self.error_color: int = self.config.get("error_color", "Core")
        self.owner_ids = self.config.get("owner_ids", "Core")
        self.start_time = datetime.now()
        self.version = "4.0.0"
        self.executed_commands = 0
        self.prefixes: dict[int, str] = {}

    async def on_shard_connect(self, shard_id: int):
        self.logger.info(f"Shard ID: {shard_id} | Logged In...")

    async def on_ready(self):
        self.logger.info(
            f"Chunked: Guilds: {len(self.guilds)} | Users: {len(self.users)}",
        )
        self.logger.info(f"Registered Shard Count: {len(self.shards)}")
        self.logger.info(
            f"Recognized Owner(s): {', '.join(map(str, self.config.get('owner_ids', 'Core')))}"
        )
        time_difference = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(
            f"Elapsed Time Since Startup: {time_difference * 1000}ms"
        )
        self.logger.info("ready...")

    async def on_shard_disconnect(self, shard_id):
        self.logger.warning(
            f"Shard {shard_id} is now in a disconnected state from Discord"
        )

    async def on_message(self, message: discord.Message):
        ctx: KurisuContext = await self.get_context(message, cls=KurisuContext)
        await self.invoke(ctx)

    async def start(self):
        await self._load_extensions()
        await self._append_prefixes()
        await super().start(self.config.get("token", "Core"))

    async def close(self):
        """Logs out bot and closes any active connections. Method is used to restart bot."""
        await self.db.close()
        await super().close()

    async def full_exit(self):
        """Completely kills the process and closes all connections. However, it will continue to restart if being ran with PM2"""
        await self.close()  # Followup exit
        exit(26)

    async def get_prefix(self, msg: discord.Message):
        if not msg.guild or not msg.guild.id in self.prefixes:
            return commands.when_mentioned_or(
                self.config.get("prefix", "Core")
            )(self, msg)
        return commands.when_mentioned_or(self.prefixes.get(msg.guild.id))(
            self, msg
        )

    async def _load_extensions(self) -> None:
        """Helper for loading all extensions at once"""
        self.logger.info("Attempting to load all extensions")
        loaded = 0
        unloaded = 0
        for ext in os.listdir("kurisu/cogs"):
            if ext.endswith(".py"):
                _log = logging.getLogger(ext)
                try:
                    await self.load_extension(f"cogs.{ext[:-3]}")
                    loaded += 1
                    _log.info("sucess...")
                except commands.ExtensionError as e:
                    unloaded += 1
                    _log.warning(f"failed... | {e}")
        self.logger.info(
            f"Extensions | Loaded: {loaded} | Unloaded: {unloaded}"
        )

    async def _initialize_db(self) -> None:
        """Initialize the bot's database"""
        with open("./kurisu/core/database/schema.sql") as f:
            await self.db.executescript(f.read())
        logging.getLogger("core.database").info("Initialized Database")

    async def _append_prefixes(self) -> None:
        """Select all custom prefixes from database and load them into cache"""
        for g, p in self.db.execute_fetchall(
            "SELECT guild, prefix FROM GuildSettings",
        ):
            self.prefixes[g] = p
        self.logger.info("Appended custom prefixes to cache")
