import discord

from discord.ext import commands
from kurisu import Kurisu
from kurisu import KurisuContext


class Miscellaneous(commands.Cog):
    """Commands that don't fit anywhere else"""

    def __init__(self, bot: Kurisu):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: KurisuContext):
        """Get the bot's latency"""
        shards = [f"Shard {_id}: {round(latency * 1000)} ms" for _id, latency in self.bot.latencies]

        embed = (
            discord.Embed(description="Pong!", color=self.bot.info_color)
            .add_field(name="Discord WebSocket", value=f"`{round(self.bot.latency * 1000)} ms`")
            .add_field(name="Message", value="`Calculating...`")
        )
        msg = await ctx.send(embed=embed)
        embed.set_field_at(
            1, name="Message", value=f"`{round((msg.created_at - ctx.message.created_at).total_seconds() * 1000)} ms`"
        )
        embed.add_field(name="Shards", value="```nim\n" + "\n".join(shards) + "\n```", inline=False)
        await msg.edit(embed=embed)

    @commands.command(aliases=["inv"])
    async def invite(self, ctx: KurisuContext):
        """Invite me to your server!"""
        try:
            await ctx.author.send(
                embed=discord.Embed(
                    title="Thank you for invite me <3",
                    url=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=413893192823&scope=bot",  # noqa e501
                    color=self.bot.ok_color,
                ).set_thumbnail(url=self.bot.user.display_avatar.url)
            )
            await ctx.send_ok("DMed you with Invite Link!")
        except (discord.Forbidden, discord.HTTPException):
            await ctx.send_error("Could not DM you with my invite link", trash=True)


def setup(bot: Kurisu):
    bot.add_cog(Miscellaneous(bot))
