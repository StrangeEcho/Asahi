from datetime import datetime
import logging
import os
import platform

from aiohttp import ClientSession
from discord.ext import commands, menus
import discord

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
            command_prefix=commands.when_mentioned_or(config.BOT_PREFIX),
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(roles=False, everyone=False),
            *args,
            **kwargs,
        )
        self.owner_ids = config.OWNER_IDS
        self.ok_color = int(str(f"0x{config.OK_COLOR}").replace("#", ""), base=16)
        self.error_color = int(str(f"0x{config.ERROR_COLOR}").replace("#", ""), base=16)
        self.uptime = None
        self._session = None
        self.startup_time = datetime.now()

    @property
    def session(self) -> ClientSession:
        if self._session is None:
            self._session = ClientSession(loop=self.loop)
        return self._session

    async def on_connect(self):
        self.logger.info(f"Logged in as {self.user.name}(ID: {self.user.id})")

    async def on_ready(self):
        if self.uptime is not None:
            return
        self.uptime = datetime.utcnow()
        self.logger.info(
            f"FINISHED CHUNKING {len(self.guilds)} GUILDS AND CACHING {len(self.users)} USERS",
        )
        self.logger.info(f"Registered Shard Count: {len(self.shards)}")
        self.logger.info(f"Recognized Owner ID(s): {', '.join(map(str, self.owner_ids))}")
        self.logger.info("STARTING COG LOADING PROCESS")
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
        self.logger.info(f"Total loaded cogs: {loaded_cogs}")
        msg = f"Total unloaded cogs: {unloaded_cogs}"
        self.logger.info(msg) if unloaded_cogs == 0 else self.logger.warning(msg)
        time_difference = ((self.startup_time - datetime.now()) * 1000).total_seconds()
        formatted_time_difference = str(time_difference).replace("-", "")
        self.logger.info(f"Elapsed Time Since Startup: {formatted_time_difference} Ms")
        self.logger.info("STARTUP COMPLETE. READY!")

    # noinspection PyMethodMayBeStatic
    async def on_shard_disconnect(self, shard_id):
        self.logger.warning(f"SHARD {shard_id} IS NOW IN A DISCONNECTED STATE FROM DISCORD")

    async def close(self):
        """Logs out of Discord and closes all connections."""
        await super().close()
        if self._session:
            await self._session.close()


bot = KurisuBot()
