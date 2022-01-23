import io

import discord
from discord.ext import commands
from kurisu import Kurisu, KurisuContext


class DevTools(commands.Cog):
    def __init__(self, bot: Kurisu):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def savechat(self, ctx: KurisuContext, limit: int = 15):
        """Save messages from the current text channel"""

        basestr = ""
        async for msg in ctx.channel.history(limit=limit):
            basestr += f"{msg.author}: {msg.content}\n"

        await ctx.send(
            file=discord.File((io.BytesIO(basestr.encode("utf-8"))), f"{ctx.message.created_at.strftime('%c')}.txt")
        )


def setup(bot: Kurisu):
    bot.add_cog(DevTools(bot))
