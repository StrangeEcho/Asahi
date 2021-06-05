

import discord
from discord.ext import commands

class Miscellaneous(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send(embed=discord.Embed(
            title=":ping_pong: Pong!",
            description=f"Websocket: {round(self.bot.latency * 1000)}ms",
            color=discord.Color.green()
        )
        .set_thumbnail(url=self.bot.user.avatar_url)
        )
        

def setup(bot: commands.Bot):
    bot.add_cog(Miscellaneous(bot))