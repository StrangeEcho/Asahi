import discord
from discord.ext import commands
from core.context import AsahiContext
from core.bot import Asahi

class Meta(commands.Cog):
    def __init__(self, bot: Asahi):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx: AsahiContext):
        """Obligitory command"""
        await ctx.send_info(f"WebSocket Latency: {round(self.bot.latency * 1000)}ms")

async def setup(bot: Asahi):
    await bot.add_cog(Meta(bot))