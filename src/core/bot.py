from datetime import datetime
from typing import Final
import io
import logging
import os
import traceback

from databases import Database
from discord.ext import commands
import aiohttp
import discord
import pomice

from exts._logging import LoggingHandler
from exts.helpers import color_resolver, Config

from .context import AsahiContext


class Asahi(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        for logger in [
            "asahi",
            "discord.client",
            "discord.gateway",
            "discord.http",
            "discord.ext.commands.core",
            "database",
            "music-master",
        ]:
            logging.getLogger(logger).setLevel(logging.DEBUG if logger == "asahi" else logging.INFO)
            logging.getLogger(logger).addHandler(LoggingHandler())
        super().__init__(
            command_prefix=self.get_prefix,
            intents=discord.Intents.all(),
            activity=discord.Activity(type=discord.ActivityType.competing, name="Best Girl"),
            *args,
            **kwargs,
        )
        self.db: Database = Database("sqlite:///src/core/data/asahi.db")
        self.config: Config = Config()
        self.owner_ids: set[int] = set(self.config.get("owner_ids"))
        self.prefixes: dict[int, str] = {}
        self.ok_color: int = color_resolver(self.config.get("ok_color"))
        self.info_color: int = color_resolver(self.config.get("info_color"))
        self.error_color: int = color_resolver(self.config.get("error_color"))
        self.logger = logging.getLogger("asahi")
        self.startup_time: datetime = datetime.now()
        self.node_pool = pomice.NodePool()

    async def on_message(self, msg: discord.Message):
        await self.invoke(await self.get_context(msg, cls=AsahiContext))

    async def on_connect(self) -> None:
        self.logger.info("Finished establishing gateway connection(s).")

    async def on_ready(self) -> None:
        self.logger.info(f"{self.user} is now ready.")

    async def on_command_completion(self, ctx: AsahiContext) -> None:
        location = f"DM Channel | {ctx.author.id}"
        if ctx.guild:
            location = f"Guild {ctx.guild} | {ctx.guild.id}"
        self.logger.info(
            "----------\n"
            "Command Executed\n"
            f"Name: {ctx.command.qualified_name}\n"
            f"User: {ctx.author}\n"
            f"Location: {location}"
            f"Usage: {ctx.message.content}"
        )

    async def close(self) -> None:
        self.logger.info("Recieved signal to terminate bot process.")
        if self.session:
            await self.session.close()
            self.logger.info("Destroyed HTTP session")
        dlog = logging.getLogger("database")
        if self.db.connection:
            await self.db.disconnect()
        dlog.info("Terminated all connections to database within the connection pool.")

        mlog = logging.getLogger("music-master")
        for node in self.node_pool.nodes.values():
            for player in list(node.players.values()):
                await player.disconnect(force=True)
                await mlog.info(f"Disconnected Player for {player.channel.guild}")
        mlog.info("Finished cleaning up Music/LavaLink. Closing now...")
        await super().close()

    async def on_command_error(self, ctx: AsahiContext, error: commands.CommandError) -> None:
        formatted_tb = "".join(traceback.format_exception(None, error, error.__traceback__))

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(
            error,
            (
                commands.MissingPermissions,
                commands.CheckFailure,
                commands.NSFWChannelRequired,
                commands.NotOwner,
                commands.BadArgument,
                commands.MissingRequiredArgument,
                commands.RoleNotFound,
                commands.MemberNotFound,
                commands.BotMissingPermissions,
            ),
        ):
            await ctx.send_error(str(error))

        if isinstance(error, commands.CommandInvokeError):
            await ctx.send_error(
                "There was an internal problem with this command. "
                f"Please refrain from using the command `{ctx.command.qualified_name}` any more. "
                "This issue has also been reported to this bot's ownership/developer team. "
                "If you need any futher assitance join my support server: https://discord.gg/Cs5RdJF9pb"
            )
            self.logger.error(formatted_tb)
            for owner in self.owner_ids:
                try:
                    await self.get_user(owner).send(
                        f"There was an internal error thrown for command {ctx.command.qualified_name}\n"
                        "Info:\n"
                        f"`User`: **{ctx.author}** | `Guild`: **{ctx.guild}** | `Usage`: **{ctx.message.content}**",
                        file=discord.File(
                            io.BytesIO(formatted_tb.encode("utf-8")),
                            f"{ctx.message.created_at.strftime('%m/%d/%Y %H:%M')}.nim",
                        ),
                    )
                except Exception:
                    self.logger.warning(f"Failed to dm {owner}.")
        else:
            self.logger.error(formatted_tb)

    async def startup(self):
        """Startup entry"""
        self.logger.info("Starting Asahi now.")
        self.logger.info(f"Time: {self.startup_time.strftime('%m/%d/%Y %H:%M')}")
        await self.db_entry()
        for ext in os.listdir("src/cogs"):  # Cog loading process
            if ext.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{ext[:-3]}")
                    self.logger.info(f"Loaded extension: {ext}")
                except commands.ExtensionError as exp:
                    self.logger.error(f"Failed to load {ext} : {exp}")
        async with self:
            async with aiohttp.ClientSession() as session:
                self.session: aiohttp.ClientSession = session
                await self.start(self.config.get("token"))

    async def db_entry(self) -> None:
        logger = logging.getLogger("database")
        with open("./src/core/data/schema.sql") as f:  # Setup Database
            for line in f.read().split(";;"):
                await self.db.execute(line)
        logger.info("Finished Building Database")

        for guild, prefix in await self.db.fetch_all("SELECT guild_id, prefix FROM Guild_Settings"):
            self.prefixes.setdefault(guild, prefix)
        logger.info("Finished appending prefixes to on-board memory cache")

    async def get_prefix(self, msg: discord.Message):
        if not msg.guild or msg.guild.id not in self.prefixes:
            return commands.when_mentioned_or(self.config.get("prefix"))(self, msg)
        else:
            return commands.when_mentioned_or(self.prefixes[msg.guild.id])(self, msg)
