import io
import traceback

import discord
from data.database import ErrorSuppressionHandler
from discord.ext import commands
from kurisu import Kurisu, KurisuContext


class Listeners(commands.Cog):
    def __init__(self, bot: Kurisu):
        self.bot = bot
        self.esh = ErrorSuppressionHandler(self.bot)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: KurisuContext, error: commands.CommandError):
        """Global Error Handler"""

        if isinstance(error, commands.CommandInvokeError):
            error_content = "".join(traceback.format_exception(None, error, error.__traceback__))
            await ctx.send(
                embed=discord.Embed(
                    title="Oopsie!!!",
                    description="Looks like this command errored out. "
                    "I've contacted this bots ownership about thie issue. "
                    "Hopefully soon the issue will be fixed!!!"
                    f"\n\nError: `{error}`",
                    color=self.bot.error_color,
                )
            )
            suppressed_guilds = await self.esh.fetch_all()
            if not suppressed_guilds or ctx.guild.id not in [item[0] for item in suppressed_guilds]:
                for owner in self.bot.config.get("owner_ids"):
                    try:
                        await self.bot.get_user(owner).send(
                            content=f"**You Idiot!!! A command threw an unhandled exception!!!**\n\n"
                            f"**Command Name**: `{ctx.command.qualified_name}`\n"
                            f"**Usage**: `{ctx.message.content}`\n"
                            f"**Guild**: `{ctx.guild}({ctx.guild.id})`\n"
                            f"**User**: `{ctx.author}({ctx.author.id})`\n"
                            f"**Error Type**: `{error}`\n"
                            "**Traceback**:",
                            file=discord.File(
                                io.BytesIO(error_content.encode("utf-8")),
                                "error.py",
                            ),
                        )
                    except (discord.Forbidden, discord.HTTPException):
                        pass
            self.bot.logger.error(error_content)

        else:
            await ctx.send_error(str(error))

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: KurisuContext):
        self.bot.executed_commands += 1
        location = " Direct Message"
        locationid = None
        if ctx.guild:
            location = ctx.guild.name
            locationid = ctx.guild.id
        self.bot.logger.info(
            f"Command Logger\n"
            f"Usage: {ctx.message.content}\n"
            f"Executed In: {location}({locationid})\n"
            f"Executed By {ctx.author}"
        )


def setup(bot: Kurisu):
    bot.add_cog(Listeners(bot))
