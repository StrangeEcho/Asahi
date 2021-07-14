from datetime import datetime
import platform
import time

from discord.ext import commands
import aiohttp
import discord
import humanize

from config import APPLICATION_ID
from utils.classes import KurisuBot
from utils.funcs import box


class Miscellaneous(commands.Cog):
    """Miscellaneous commands"""

    def __init__(self, bot: KurisuBot):
        self.bot = bot

    @commands.has_permissions(embed_links=True)
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(
        self,
        ctx: commands.Context,
    ):
        """Just a ping command"""
        latency = self.bot.latency * 1000
        emb = discord.Embed(title="Please wait..", color=self.bot.ok_color)
        emb.add_field(
            name="Discord WS:",
            value=box(str(round(latency)) + " ms", "nim"),
            inline=True,
        )
        emb.add_field(name="Typing", value=box("calculating" + " ms", "nim"), inline=True)
        emb.add_field(name="Message", value=box("…", "nim"), inline=True)

        before = time.monotonic()
        message = await ctx.reply(embed=emb, mention_author=False)
        ping = (time.monotonic() - before) * 1000

        emb.title = "Pong! :ping_pong:"
        emb.color = self.bot.ok_color
        shards = [
            f"Shard {shard + 1}/{self.bot.shard_count}: {round(pingt * 1000)}ms\n"
            for shard, pingt in self.bot.latencies
        ]
        emb.add_field(name="Shards:", value=box("".join(shards), "nim"))
        emb.set_field_at(
            1,
            name="Message:",
            value=box(
                str(int((message.created_at - ctx.message.created_at).total_seconds() * 1000))
                + " ms",
                "nim",
            ),
            inline=True,
        )
        emb.set_field_at(
            2, name="Typing:", value=box(str(round(ping)) + " ms", "nim"), inline=True
        )
        await message.edit(embed=emb)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def invite(self, ctx: commands.Context):
        """Invite the bot to your server."""
        embed = discord.Embed(color=self.bot.ok_color, title="<3")
        embed.description = f"Invite Link: https://discord.com/api/oauth2/authorize?client_id={APPLICATION_ID}&scope=bot"
        embed.set_footer(
            text=f"Thank you for inviting {self.bot.user.name} <3",
            icon_url=self.bot.user.avatar.url,
        )
        try:
            await ctx.author.send(embed=embed)
            await ctx.reply("Sent!", mention_author=False)
        except discord.Forbidden:
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def support(self, ctx: commands.Context):
        await ctx.send(
            embed=discord.Embed(
                description=f"Come see me and my master and the rest of my robotic brothers and sisters [here](https://discord.gg/Cs5RdJF9pb)",
                color=self.bot.ok_color,
            ).set_thumbnail(url=self.bot.user.avatar.url)
        )

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stats(self, ctx: commands.Context):
        """Some stats about me."""
        text_channels = 0
        voice_channels = 0
        for chan in self.bot.get_all_channels():
            if isinstance(chan, discord.TextChannel):
                text_channels += 1
            if isinstance(chan, discord.VoiceChannel):
                voice_channels += 1
        embed = discord.Embed(
            title=f"{self.bot.user.name} Stats",
            description=f"Invite me [here](https://discord.com/api/oauth2/authorize?client_id=784474257832804372&scope=bot) and join my Support Server [here](https://discord.gg/Cs5RdJF9pb)",
            color=self.bot.ok_color,
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name="Author:", value="Tylerr#6979", inline=True)
        embed.add_field(
            name="Python Versions:",
            value=f"Python Version: {platform.python_version()}\nDiscord.py Version: {discord.__version__}",
            inline=True,
        )
        embed.add_field(name="Websocket Latency", value=f"{round(self.bot.latency * 1000)}ms")
        embed.add_field(name="Shards", value=self.bot.shard_count)
        embed.add_field(name="Bot ID:", value=self.bot.user.id, inline=True)
        embed.add_field(name="Guild Count:", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Cached Users:", value=len(self.bot.users), inline=True)
        embed.add_field(
            name="Channels:",
            value=f"Text: {text_channels}\nVoice: {voice_channels}\nTotal: {text_channels + voice_channels}",
            inline=True,
        )
        embed.add_field(
            name="Uptime:",
            value=f"{humanize.time.naturaldelta(datetime.utcnow() - self.bot.uptime)}",
            inline=True,
        )
        embed.add_field(
            name="Creation Date:",
            value=self.bot.user.created_at.strftime("%c"),
            inline=True,
        )
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        embed.add_field(
            name="Github Repository:",
            value="Find it [here](https://github.com/Yat-o/Kurisu/tree/rewrite)",
            inline=True,
        )
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        embed.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"{self.bot.user.name} was made with love. <3",
        )
        await ctx.send(embed=embed)

    @commands.command(usage="(project name)")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pypi(self, ctx: commands.Context, project: str):
        """Get information of a python project from pypi."""
        async with self.bot.session.get(f"https://pypi.org/pypi/{project}/json") as response:
            try:
                res = await response.json()
            except aiohttp.client_exceptions.ContentTypeError:
                e = discord.Embed(
                    title="404 - Page Not Found",
                    description="We looked everywhere but couldn't find that project",
                    colour=self.bot.ok_color,
                )
                e.set_thumbnail(
                    url="https://cdn-images-1.medium.com/max/1200/1%2A2FrV8q6rPdz6w2ShV6y7bw.png"
                )
                return await ctx.reply(embed=e)

            info = res["info"]
            e = discord.Embed(
                title=f"{info['name']} · PyPI",
                description=info["summary"],
                colour=0x0073B7,
            )
            e.set_thumbnail(
                url="https://cdn-images-1.medium.com/max/1200/1%2A2FrV8q6rPdz6w2ShV6y7bw.png"
            )
            e.add_field(
                name="Author Info",
                value=f"**Name**: {info['author']}\n"
                + f"**Email**: {info['author_email'] or '`Not provided.`'}",
            )
            e.add_field(name="Version", value=info["version"])
            e.add_field(
                name="Project Links",
                value="\n".join([f"[{x}]({y})" for x, y in dict(info["project_urls"]).items()]),
            )
            e.add_field(name="License", value=info["license"] or "`Not specified.`")
            await ctx.reply(embed=e, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def uptime(self, ctx: commands.Context):
        """Shows bot's uptime."""
        since = self.bot.uptime.strftime("%H:%M:%S UTC | %Y-%m-%d")
        delta = datetime.utcnow() - self.bot.uptime
        uptime_text = humanize.time.precisedelta(delta) or "Less than one second."
        embed = discord.Embed(colour=self.bot.ok_color)
        embed.add_field(name=f"{self.bot.user.name} has been up for:", value=uptime_text)
        embed.set_footer(text=f"Since: {since}")
        await ctx.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
