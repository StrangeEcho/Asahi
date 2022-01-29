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
        """Global Error Handler Listener"""
        formatted_traceback = "".join(traceback.format_exception(None, error, error.__traceback__))

        if getattr(ctx, "handled", False):
            return

        elif isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(
            error,
            (
                commands.NotOwner,
                commands.MissingPermissions,
                commands.BotMissingAnyRole,
                commands.MissingRole,
                commands.BotMissingPermissions,
                commands.CheckFailure,
                commands.MissingRequiredArgument,
                commands.BadArgument,
                commands.NoPrivateMessage,
                commands.TooManyArguments,
                commands.NSFWChannelRequired,
                commands.CommandOnCooldown,
            ),
        ):
            await ctx.send_error(str(error))

        elif isinstance(error, commands.CommandInvokeError):
            suppressed = await self.esh.fetch_all()
            self.bot.logger.error(formatted_traceback)

            await ctx.send_error(
                "Uh Oh! It would seem that this command threw and unexpected error. "
                "This bot's ownership team has been notified. "
                "Hopefully this problem will be fixed soon. "
                "For now please refrain from using the command that threw this error. "
                "Check back in soon!\n\n"
                f"Error: ```\n{error}\n```"
            )

            if not suppressed or ctx.guild.id not in [i[0] for i in suppressed]:
                for owner in self.bot.owner_ids:
                    try:
                        await self.bot.get_user(owner).send(
                            "**Unexpected exception caught.**\n\n"
                            f"**Command**: {ctx.command.qualified_name}\n"
                            f"**Guild**: {ctx.guild}({ctx.guild.id if ctx.guild else 'None'})\n"
                            f"**Channel**: {ctx.channel}({ctx.channel.id if ctx.channel else 'None'})\n"
                            f"**User**: {ctx.author}\n"
                            f"**Usage**: {ctx.message.content}",
                            file=discord.File(io.BytesIO(formatted_traceback.encode("utf-8")), "error.nim"),
                        )
                    except (discord.Forbidden, discord.HTTPException):
                        pass
        else:
            self.bot.logger.error(formatted_traceback)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: KurisuContext):
        self.bot.executed_commands += 1
        location = "Direct Message Channel"
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
