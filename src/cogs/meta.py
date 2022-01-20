from discord.ext import commands
from kurisu.bot import Kurisu


class Meta(commands.Cog):
    def __init__(self, bot: Kurisu):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("Ponggers")

def setup(bot: Kurisu):
    bot.add_cog(Meta(bot))