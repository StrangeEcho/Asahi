import discord
import aiohttp 

from discord.ext import commands

class Misc(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def megumin(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/api/sfw/megumin') as r:

                meguminpic = (await r.json())['url']

                await ctx.send(meguminpic)


    @commands.command()
    async def shinobu(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/api/sfw/shinobu') as r:
                
                shinobupic = (await r.json())['url']

                await ctx.send(shinobupic)

    @commands.command()
    async def neko(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/api/sfw/neko'):

                nekopic = (await r.json())['url']

                await ctx.send(nekopic)

 

    

    