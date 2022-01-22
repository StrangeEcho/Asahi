import discord

from discord.ext import commands
from kurisu.bot import Kurisu
from kurisu.context import KurisuContext


class Meta(commands.Cog):
    def __init__(self, bot: Kurisu):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: KurisuContext):
        shards = [f"Shard {id}: {latency} ms" for id, latency in self.bot.latencies]
        
        embed = discord.Embed(
            description="Pong!",
            color=self.bot.info_color
        ).add_field(
            name="Discord WebSocket",
            value=f"{round(self.bot.latency * 1000)} ms"
        ).add_field(
            name="Message",
            value="Calculating..."
        )
        msg = await ctx.send(embed=embed)
        embed.set_field_at(
            1,
            name="Message",
            value=f"{(msg.created_at - ctx.message.created_at).total_seconds() * 1000} ms"
        )
        embed.add_field(
            name="Shards",
            value="```nim\n" + "\n".join(shards) + "\n```"
        )
        await msg.edit(embed=embed)

def setup(bot: Kurisu):
    bot.add_cog(Meta(bot))
