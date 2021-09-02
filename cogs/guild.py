from discord.ext import commands
import discord

from utils.classes import KurisuBot, PrefixManager


class ServerSettings(commands.Cog):
    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.prefix_manager = PrefixManager(bot=self.bot)

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx: commands.Context):
        """Guild prefixes related commands"""
        g_prefix = self.bot.prefixes.get(str(ctx.guild.id)) or self.bot.get_config(
            "config", "config", "prefix"
        )
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
    async def default(self, ctx: commands.Context):
        """Set the current prefix for this server back to default"""
        await self.prefix_manager.remove_prefix(ctx.guild.id)
        await ctx.send(
            embed=discord.Embed(title="Prefix set back to normal", color=self.bot.ok_color)
        )


def setup(bot):
    bot.add_cog(ServerSettings(bot))
