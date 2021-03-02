import logging
import discord


from discord.ext import commands

log = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    """Handler for discord.py errors."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
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
            await ctx.send(
                f"You are missing some required arguments\n`{error.param.name}`"
            )

        elif isinstance(error, commands.NotOwner) or isinstance(
            error, commands.MissingPermissions
        ):
            await ctx.send(
                "You are missing the correct permissions to execute this command"
            )

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
            await ctx.send(
                "If you are getting this error, contact Tylerr#6979 for help.\nThis is due to the fact he is a terrible coder"
            )
            log.error(
                f"{ctx.command.qualified_name} failed to execute. ",
                exc_info=error.original,
            )

            embed = discord.Embed(
                title="Baka!",
                description=(
                    f"""
                You idiot coder.\n
                **{ctx.command.name}** in **{ctx.guild}** errored out because you're dumb\n
                error:\n
                ```{error}```       
            """
                ),
                color=discord.Color.red(),
            )
            embed.set_footer(text="Look in console for a more detailed error message")
            await self.bot.get_user(284102119408140289).send(embed=embed)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
