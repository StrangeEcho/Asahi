from discord.ext import commands
from utils.kurisu import KurisuBot


class Testing(commands.Cog):
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx: commands.Context):
        await ctxx.send("Hi")


def setup(bot):
    bot.add_cog(Testing(bot))
