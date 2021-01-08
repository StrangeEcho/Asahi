import discord
import aiohttp

from discord.ext import commands


class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def megumin(self, ctx):
        """Megumin pics from waifu.pics api."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/megumin") as r:
                await ctx.send((await r.json())["url"])

    @commands.command()
    @commands.guild_only()
    async def shinobu(self, ctx):
        """Shinobu pics from waifu.pics api."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/shinobu") as r:
                await ctx.send((await r.json())["url"])

    @commands.command()
    @commands.guild_only()
    async def neko(self, ctx):
        """Neko pics from waifu.pics api."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/neko"):
                await ctx.send(nekopic)

    @commands.command()
    @commands.guild_only()
    async def waifu(self, ctx):
        """Waifus from waifu.pics api."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/waifu") as r:
                await ctx.send((await r.json())["url"])


def setup(bot):
    bot.add_cog(Anime(bot))
