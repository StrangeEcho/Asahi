from discord.ext import commands
from utils.dbmanagers import PrefixManager
from utils.kurisu import KurisuBot
from utils.kurisu import KurisuContext
import discord


class Server_Settings(commands.Cog):
    """A module meant to help manage your servers settings in correlation to this bot."""

    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.prefix_manager = PrefixManager(bot=self.bot)

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx: KurisuContext):
        """Guild prefixes related commands"""
        g_prefix = self.bot.prefixes.get(
            str(ctx.guild.id)
        ) or self.bot.get_config("config", "config", "prefix")
        await ctx.send(
            embed=discord.Embed(
                description=f"The current prefix for this guild is `{g_prefix}`",
                color=self.bot.ok_color,
            )
        )

    @prefix.command(name="set")
    @commands.has_permissions(manage_guild=True)
    async def _set(self, ctx, prefix: str):
        """Set a new prefix for this server"""
        if len(prefix) > 10:
            return await ctx.send("Prefix can't be longer than 10 characters.")
        await self.prefix_manager.add_prefix(ctx.guild.id, prefix)
        await ctx.send(
            embed=discord.Embed(
                title="New Prefix Set",
                description=f"New Prefix: `{prefix}`",
                color=self.bot.ok_color,
            )
        )

    @prefix.command(aliases=["reset"])
    @commands.has_permissions(manage_guild=True)
    async def default(self, ctx: KurisuContext):
        """Set the current prefix for this server back to default"""
        await self.prefix_manager.remove_prefix(ctx.guild.id)
        await ctx.send(
            embed=discord.Embed(
                title="Prefix set back to normal", color=self.bot.ok_color
            )
        )


def setup(bot):
    bot.add_cog(Server_Settings(bot))
