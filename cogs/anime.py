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

                meguminpic = (await r.json())["url"]

                await ctx.send(meguminpic)

    @commands.command()
    @commands.guild_only()
    async def shinobu(self, ctx):
        """Shinobu pics from waifu.pics api."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/shinobu") as r:

                shinobupic = (await r.json())["url"]

                await ctx.send(shinobupic)

    @commands.command()
    @commands.guild_only()
    async def neko(self, ctx):
        """Neko pics from waifu.pics api."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/neko"):

                nekopic = (await r.json())["url"]

                await ctx.send(nekopic)

    @commands.command()
    @commands.guild_only()
    async def waifu(self, ctx):
        """Waifus from waifu.pics api."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/waifu") as r:

                waifu = (await r.json())["url"]

                await ctx.send(waifu)


def setup(bot):
    bot.add_cog(Anime(bot))
