import logging

import discord
from colorama import Fore, Style
from discord.ext import commands

from config import FOWARD_DMS

log = logging.getLogger(__name__)


class Listeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors caused by commands."""
        # Skips errors that were already handled locally.
        if getattr(ctx, "handled", False):
            return

        ignored = commands.CommandNotFound

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This Command Cannot Be Used In Private DMS")

        elif isinstance(error, commands.TooManyArguments):
            await ctx.send("You Passed In Too Many Arguments")

        elif isinstance(error, commands.NSFWChannelRequired):
            await ctx.send(f"**{ctx.channel}** is not a NSFW channel")

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"You are missing some required arguments\n`{error.param.name}`")

        elif isinstance(error, commands.NotOwner) or isinstance(
            error, commands.MissingPermissions
        ):
            await ctx.send("You are missing the correct permissions to execute this command")

        elif isinstance(error, commands.CommandOnCooldown) or isinstance(
            error, commands.CheckFailure
        ):
            await ctx.send(error)

        elif isinstance(error, commands.DisabledCommand):  # SoonTM
            await ctx.send("This command is disabled")

        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"You passed in a bad argument\n{error}")

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I am missing permissions to execute this command")

        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(f"```py\n{error}\n```")
            log.error(
                Fore.RED + f"**{ctx.command.qualified_name} failed to execute**",
                exc_info=error.original,
            )
            print(Style.RESET_ALL + "-" * 15)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        location = " Direct Message"
        locationID = None
        if ctx.guild:
            location = ctx.guild.name
            locationID = ctx.guild.id
        print(Fore.CYAN, f"\rUsage: {ctx.message.content}")
        print(f"Executed In: {location}({locationID})")
        print(f"Executed By {ctx.author}", Style.RESET_ALL)
        print("-" * 15)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            pass
        elif not message.guild and FOWARD_DMS is True:
            owner = self.bot.get_user(284102119408140289)
            await owner.send(
                embed=discord.Embed(
                    title=f"{message.author} said ...",
                    description=message.content,
                    color=discord.Color.green(),
                )
            )
        else:
            pass


def setup(bot):
    bot.add_cog(Listeners(bot))
