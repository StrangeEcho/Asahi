import logging
import os


from discord.ext import commands
from typing import Any, Optional
import discord
import tomllib
import aiosqlite

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
            intents=discord.Intents.all(),
        )
        self.config = ConfigHandler()
        self.logger = logging.getLogger(__name__)
        self.db = aiosqlite.connect("./Kurisu/core/database/database.db")
        self.ok_color: int = self.config.get("ok_color", "Core")
        self.error_color: int = self.config.get("error_color", "Core")
        self.owner_ids = self.config.get("owner_ids", "Core")
        self.start_time = discord.utils.utcnow()
        self.version = "3.2.2"
        self.executed_commands = 0
        self.prefixes: dict[int, str] = {}

    async def on_shard_connect(self, shard_id: int):
        self.logger.info(f"Shard ID: {shard_id} | Logged In...")


    async def on_ready(self):
        if self.uptime is not None:
            return
        self.uptime = discord.utils.utcnow()
        self.logger.info(
            f"FINISHED CHUNKING {len(self.guilds)} GUILDS AND CACHING {len(self.users)} USERS",
        )
        self.logger.info(f"Registered Shard Count: {len(self.shards)}")
        owners = [
            await self.fetch_user(o)
            for o in self.get_config("config", "config", "owner_ids")
        ]
        self.logger.info(f"Recognized Owner(s): {', '.join(map(str, owners))}")
        self.logger.info(
            f"NO_PRIVLIEDGED_OWNERS config was set to {self.get_config('configoptions', 'options', 'no_priviledged_owners')}"
        )
        self.logger.info("ATTEMPTING TO MOUNT COG EXTENSIONS!")
        loaded_cogs = 0
        unloaded_cogs = 0
        for cog in os.listdir("./kurisu/cogs"):
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
        self.logger.info(msg) if unloaded_cogs == 0 else self.logger.warning(
            msg
        )
        time_difference = (
                (self.startup_time - discord.utils.utcnow()) * 1000
        ).total_seconds()
        formatted_time_difference = str(time_difference).replace("-", "")
        self.logger.info(
            f"Elapsed Time Since Startup: {formatted_time_difference} Ms"
        )
        self.logger.info("STARTUP COMPLETE. READY!")

    # noinspection PyMethodMayBeStatic
    async def on_shard_disconnect(self, shard_id):
        self.logger.warning(
            f"SHARD {shard_id} IS NOW IN A DISCONNECTED STATE FROM DISCORD"
        )

    async def on_message(self, message: discord.Message):
        ctx: KurisuContext = await self.get_context(message, cls=KurisuContext)
        await self.invoke(ctx)

    async def close(self):
        """Logs out bot and closes any active connections. Method is used to restart bot."""
        for g in self.guilds:
            if g.voice_client:
                await g.voice_client.destroy()
        self.logger.info("Destroyed all active LL players")
        if self._session:
            self._session.close()
            self.logger.info("Terminated HTTP sessions.")
        await self.db.disconnect()
        self.logger.info("Closed all connections in the DB connection pool.")
        self.logger.info("Proceeding to normal shutdown")
        await super().close()

    async def full_exit(self):
        """Completely kills the process and closes all connections. However, it will continue to restart if being ran with PM2"""
        for g in self.guilds:
            if g.voice_client:
                await g.voice_client.destroy()
        self.logger.info("Destroyed all active LL players")
        if self._session:
            self._session.close()
            self.logger.info("Terminated HTTP sessions.")
        await self.db.disconnect()
        self.logger.info("Closed all connections in the DB connection pool.")
        self.logger.info("Proceeding to normal shutdown")
        exit(26)

    async def reload_all_extensions(self, ctx: commands.Context = None):
        self.logger.info("Signal recieved to reload all bot extensions")
        success = 0
        failed = 0
        for cog in os.listdir("./kurisu/cogs"):
            if cog.endswith(".py"):
                try:
                    self.reload_extension(f"cogs.{cog[:-3]}")
                    self.logger.info(f"Reloaded {cog}")
                    success += 1
                except Exception as e:
                    self.logger.warning(f"Failed reloading {cog}\n{e}")
                    failed += 1
        if ctx:
            await ctx.send(
                embed=discord.Embed(
                    description=f"Successfully reloaded {success} cog(s)\n Failed reloading {failed - 1} cog(s)",
                    color=self.ok_color,
                ).set_footer(
                    text="If any cogs failed to reload, check console for feedback."
                )
            )
