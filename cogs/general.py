# just gonna make one command and call it a day
import discord 
from discord.ext import commands

class general(commands.Cog):

    def __init__(self, cog):
        self.bot = bot 

    @commands.command(brief = 'ping command')
    async def ping(self, ctx):
        embed = discord.Embed(
            title="Ping/Latency:",
            description=f"Pong!{round(self.bot.latency * 1000)} ms",
            color=0x000000
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(general(bot))