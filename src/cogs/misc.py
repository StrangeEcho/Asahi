import discord

from discord.ext import commands
from kurisu import Kurisu
from kurisu import KurisuContext


class Miscellaneous(commands.Cog):
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


def setup(bot: Kurisu):
    bot.add_cog(Miscellaneous(bot))
