from discord.ext import commands
from utils.context import KurisuContext
from utils.dbmanagers import AFKManager
from utils.errors import UserNotFound
from utils.kurisu import KurisuBot
import discord


class AFK(commands.Cog):
    """Relay a "afk message" back to your friends when they mention you are you are away."""

    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.am = AFKManager(self.bot)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        for i in [u.id for u in message.mentions]:
            try:
                data = await self.am.fetch_afk(i)
            except UserNotFound:
                return
            if data[1] == 1:
                await message.channel.send(
                    delete_after=5,
                    embed=discord.Embed(
                        title=f"{self.bot.get_user(i)} is currently away.",
                        description=data[0],
                        color=self.bot.ok_color,
                    ),
                )

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def setafk(self, ctx: KurisuContext, *, msg: str):
        """Set your afk message"""
        if len(msg) > 200:
            return await ctx.send_error(
                "AFK message cannot be longer than 200 characters!"
            )
        await self.am.insert_or_update(ctx.author.id, msg)
        await ctx.send_ok(
            "Set your afk message to:\n" + "```\n" + msg + "\n```"
        )

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def afktoggle(self, ctx: KurisuContext):
        """Toggle your afk message on or off"""
        try:
            await self.am.toggle_afk(ctx.author.id)
        except UserNotFound:
            await ctx.send_error(
                f"User Not Found in Database. Setup your afk message first with `{ctx.clean_prefix}setafk`"
            )
        await ctx.send_ok("Successfully toggled your afk message.")

    @commands.command()
    @commands.cooldown(1, 2.5, commands.BucketType.user)
    async def afkstatus(self, ctx: KurisuContext):
        """Shows you what your current afk status is"""
        afkdata = await self.am.fetch_afk(ctx.author.id)

        await ctx.send(
            embed=discord.Embed(
                title=f"Current AFK Status For {ctx.author.name}",
                color=self.bot.ok_color,
            )
                .add_field(name="Toggled", value=bool(afkdata[1]), inline=True)
                .add_field(
                name="Message",
                value="```\n" + str(afkdata[0]) + "\n```",
                inline=True,
            )
        )


def setup(bot):
    bot.add_cog(AFK(bot))
