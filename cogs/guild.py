from discord.ext import commands
import discord

from config import BOT_PREFIX
from utils.classes import KurisuBot, PrefixManager


class ServerSettings(commands.Cog):
    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.prefix_manager = PrefixManager(bot=self.bot)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx: commands.Context, prefix: str = None):
        """Change prefix of bot"""
        if prefix is None:
            guild_prefix = self.bot.prefixes.get(str(ctx.guild.id))
            return await ctx.send(
                embed=discord.Embed(
                    description=f"The current prefix for this guild is `{guild_prefix or BOT_PREFIX}`",
                    color=self.bot.ok_color,
                )
            )
        elif prefix:
            self.prefix_manager.add_prefix(guild=ctx.guild.id, prefix=prefix)
            await ctx.send(
                embed=discord.Embed(
                    title="New Prefix Set!",
                    description=f"New Prefix: `{prefix}`",
                    color=self.bot.ok_color,
                )
            )


def setup(bot):
    bot.add_cog(ServerSettings(bot))
