import datetime
import logging

from discord.ext import commands
import discord

from config import FORWARD_DMS
from utils.classes import HimejiBot

log = logging.getLogger("Listeners")


class Listeners(commands.Cog):
    def __init__(self, bot: HimejiBot):
        self.bot = bot
        self.timeout = 60

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
            await ctx.author.send(
                embed=discord.Embed(
                    description="This command cannot be used in Private Messages",
                    color=self.bot.error_color,
                )
            )

        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(
                embed=discord.Embed(
                    description="You passed in a couple unneeded arguments. Please get rid of them and try again",
                    color=self.bot.error_color,
                )
            )

        elif isinstance(error, commands.NSFWChannelRequired):
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.channel.name} is not a NSFW channel.",
                    color=self.bot.error_color,
                ).set_thumbnail(
                    url="https://media1.tenor.com/images/8b78fe252e0fdb748f25a5618da61baa/tenor.gif?itemid=9601429"
                )
            )

        elif isinstance(
            error,
            (
                commands.NotOwner,
                commands.MissingPermissions,
                commands.BotMissingAnyRole,
                commands.MissingRole,
                commands.BotMissingPermissions,
                commands.CommandOnCooldown,
                commands.CheckFailure,
                commands.MissingRequiredArgument,
            ),
        ):
            await ctx.send(embed=discord.Embed(description=str(error), color=self.bot.error_color))

        elif isinstance(error, commands.BadArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="You passed in a bad argument",
                    description=error,
                    color=self.bot.error_color,
                )
            )

        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                embed=discord.Embed(
                    title="Oops!",
                    description=f"It looks like my owner may have messed up some code for this command. ```py\n{error}\n```",
                    color=self.bot.error_color,
                ).set_footer(
                    icon_url=ctx.author.avatar.url, text="This incident was reported to my master."
                )
            )
            for owner in self.bot.owner_ids:
                owner = self.bot.get_user(owner)
                await owner.send(
                    embed=discord.Embed(
                        title="You Baka!",
                        description=f"`{ctx.command}` errored out in `{ctx.guild}({ctx.guild.id})`\n```py\n{error}\n```",
                        color=self.bot.error_color,
                    )
                )
            self.bot.logger.error(
                f"**{ctx.command.qualified_name} failed to execute**", exc_info=error.original
            )

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        location = " Direct Message"
        locationID = None
        if ctx.guild:
            location = ctx.guild.name
            locationID = ctx.guild.id
        self.bot.logger.info(
            f"Command Logger\n"
            f"Usage: {ctx.message.content}\n"
            f"Executed In: {location}({locationID})\n"
            f"Executed By {ctx.author}"
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return
        if message.author.bot:
            return
        if not message.guild and FORWARD_DMS is True:
            for owner in self.bot.owner_ids:
                try:
                    await self.bot.get_user(owner).send(
                        embed=discord.Embed(
                            title=f"{message.author} said ... in dms",
                            description=message.content,
                            color=discord.Color.green(),
                        ).set_footer(
                            text=f"User ID: {message.author.id}",
                            icon_url=message.author.avatar.url,
                        )
                    )
                except discord.HTTPException as e:
                    self.bot.logger.info(f"Failed to forward dms to the owner due to: {e}")

    async def edit_process_commands(self, message: discord.Message):
        """Same as Airi's method (Airi.process_commands), but don't dispatch message_without_command."""
        if not message.author.bot:
            ctx = await self.bot.get_context(message)
            await self.bot.invoke(ctx)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.edited_at:
            return
        if before.content == after.content:
            return
        if (after.edited_at - after.created_at).total_seconds() > self.timeout:
            return
        await self.edit_process_commands(after)


def setup(bot):
    bot.add_cog(Listeners(bot))
