import logging
import io
import traceback
import os
from typing import Final, Optional
from datetime import datetime

import discord
from discord.ext import commands
from databases import Database
from exts.helpers import Config, color_resolver
from exts._logging import LoggingHandler
from .context import AsahiContext

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
            activity=discord.Activity(type=discord.ActivityType.competing, name="Best Girl"),
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
    
    async def on_command_completion(self, ctx: AsahiContext) -> None:
        self.logger.info(
            "----------\n"
            "Command Executed\n"
            f"Name: {ctx.command.qualified_name}\n"
            f"User: {ctx.author}\n"
            f"Location: Guild {ctx.guild}({ctx.guild.id}) | Channel: {ctx.channel}({ctx.channel.id})\n"
            f"Usage: {ctx.message.content}"
        )
    
    async def on_command_error(self, ctx: AsahiContext, error: commands.CommandError) -> None:
        if isinstance(
            error,
            (
                commands.MissingPermissions,
                commands.CheckFailure,
                commands.NSFWChannelRequired,
                commands.NotOwner,
                commands.BadArgument,
                commands.MissingRequiredArgument
            )
        ):
            await ctx.send_error(str(error))
        
        if isinstance(error, commands.CommandInvokeError):
            formatted_tb = "".join(traceback.format_exception(None, error, error.__traceback__))
            await ctx.send_error(
                "There was an internal problem with this command. "
                f"Please refrain from using the command `{ctx.command.qualified_name}` any more. "
                "This issue has also been reported to this bot's ownership/developer team."
            )
            for owner in self.owner_ids:
                try:
                    await self.get_user(owner).send(
                        f"There was an internal error thrown for command {ctx.command.qualified_name}\n"
                        "Info:\n"
                        f"`User`: **{ctx.author}** | `Guild`: **{ctx.guild}** | `Usage`: **{ctx.message.content}**",
                        file=discord.File(io.BytesIO(formatted_tb.encode("utf-8")), f"{ctx.message.created_at.strftime('%m/%d/%Y %H:%M')}.nim")
                    )
                except Exception:
                    pass
        else:
            self.logger.info(formatted_tb)


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
        logger = logging.getLogger("database")
        with open("./src/core/data/schema.sql") as f: # Setup Database
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