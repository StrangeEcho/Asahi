import re

from discord.ext import commands
import discord

from utils.context import KurisuContext
from utils.dbmanagers import AFKManager
from utils.errors import UserNotFound
from utils.kurisu import KurisuBot


class AFK(commands.Cog):
    """Afk Cog"""
    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.am = AFKManager(self.bot)

    @commands.Cog.listener()
    async def on_message(self, m: discord.Message):
        for u in [u.mention for u in self.bot.users]:
            if u in [x.mention for x in m.mentions]:
                to_fetch = int(re.sub(r"<|>|@|!", "", u))
                try:
                    data = await self.am.fetch_afk(to_fetch)
                except UserNotFound:
                    return
                if data[1] == 1:
                    usr = await self.bot.fetch_user(to_fetch)
                    await m.channel.send(
                        embed=discord.Embed(
                            title=f"{usr.name} is currently AFK",
                            description=data[0],
                            color=self.bot.ok_color,
                        )
                    )

    @commands.command()
    async def setafk(self, ctx: KurisuContext, *, msg: str):
        """Set your afk message"""
        if len(msg) > 200:
            return await ctx.send_error("AFK message cannot be longer than 200 characters.")
        await self.am.insert_or_update(ctx.author.id, msg)
        await ctx.send_ok(f"Set your afk message to:\n" + "```\n" + msg + "\n```")

    @commands.command()
    async def afktoggle(self, ctx: KurisuContext):
        """Toggle your afk message"""
        try:
            await self.am.toggle_afk(ctx.author.id)
            await ctx.send_ok("Toggled your AFK status.")
        except UserNotFound:
            await ctx.send_error(f"User Not Found In DB. Try setting AFK message and try again.")


def setup(bot):
    bot.add_cog(AFK(bot))
