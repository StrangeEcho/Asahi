from datetime import datetime
import logging
import os
import platform

from aiohttp import ClientSession
from discord.ext import commands, menus
import discord

import config

from .log import LoggingHandler

embed_color = config.OK_COLOR.replace("#", "0x")


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


class HimejiHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page, color=int(embed_color, base=16))
            await destination.send(embed=embed)


class HimejiBot(commands.AutoShardedBot):
    """Idk"""

    def __init__(self, *args, **kwargs):
        for logger in [
            "himeji",
            "discord.client",
            "discord.gateway",
            "discord.http",
            "discord.ext.commands.core",
            "Listeners",
        ]:
            logging.getLogger(logger).setLevel(
                logging.DEBUG if logger == "himeji" else logging.INFO
            )
            logging.getLogger(logger).addHandler(LoggingHandler())
        self.logger = logging.getLogger("himeji")
        self.logger.info(f"Starting the bot...")
        current_time = datetime.now().strftime("%c")
        self.logger.info(f"Current Time: {current_time}")
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.BOT_PREFIX),
            intents=discord.Intents.all(),
            help_command=HimejiHelpCommand(no_category="Help"),
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
        self.logger.info(
            f"Using Python version *{platform.python_version()}* and using Discord.py version *{discord.__version__}*"
        )
        self.logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")

    async def on_ready(self):
        if bot.uptime is not None:
            return
        bot.uptime = datetime.utcnow()
        self.logger.info(
            f"FINISHED CHUNKING {len(self.guilds)} GUILDS AND CACHING {len(self.users)} USERS",
        )
        self.logger.info(f"Registered Shard Count: {len(self.shards)}")
        self.logger.info(f"Recognized Owner ID(s): {', '.join(map(str, self.owner_ids))}")
        time_difference = ((self.startup_time - datetime.now()) * 1000).total_seconds()
        formatted_time_difference = str(time_difference).replace("-", "")
        self.logger.info(f"Elapsed Time Since Startup: {formatted_time_difference} Ms")
        self.logger.info("PROCEEDING TO COG LOADING PROCESS")
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
        self.logger.info(f"Total unloaded cogs: {unloaded_cogs}")
        self.logger.info("STARTUP COMPLETE. READY!")

    # noinspection PyMethodMayBeStatic
    async def on_shard_connect(self, shard_id):
        self.logger.info(f"Shard {shard_id} Logged Into Discord.")

    # noinspection PyMethodMayBeStatic
    async def on_shard_disconnect(self, shard_id):
        self.logger.warning(f"SHARD {shard_id} IS NOW IN A DISCONNECTED STATE FROM DISCORD")

    async def close(self):
        """Logs out of Discord and closes all connections."""
        await super().close()
        if self._session:
            await self._session.close()


bot = HimejiBot()
