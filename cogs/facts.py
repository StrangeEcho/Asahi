import discord
import aiohttp

from discord.ext import commands


class Facts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def catfact(self, ctx):
        """Get a random cat fact"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/facts/cat") as r:

                await ctx.send((await r.json())["fact"])

    @commands.command()
    async def dogfact(self, ctx):
        """Get a random dog fact"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/facts/dog") as r:

                await ctx.send((await r.json())["fact"])

    @commands.command()
    async def pandafact(self, ctx):
        """Get a random panda fact"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/facts/panda") as r:

                await ctx.send((await r.json())["fact"])

    @commands.command()
    async def birdfact(self, ctx):
        """Get a random bird fact"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/facts/bird") as r:

                await ctx.send((await r.json())["fact"])


    @commands.command()
    async def koalafact(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/facts/koala") as r:
                
                await ctx.send(await r.json()["url"])

def setup(bot):
    bot.add_cog(Facts(bot))
