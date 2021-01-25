import discord

from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["issue"])
    async def bug(self, ctx):
        """Bug report command."""
        await ctx.send(
            "See a bug or issue with the bot? Please report it at https://github.com/Yat-o/HimejiBot/issues"
        )


def setup(bot):
    bot.add_cog(Misc(bot))
