import platform
import time
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

from config import APPLICATION_ID
from utils.funcs import box, time_notation
from utils.vars import bot_start_time


class Miscellaneous(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_permissions(embed_links=True)
    @commands.command()
    async def ping(
        self,
        ctx,
    ):
        """Just a ping command"""
        latency = self.bot.latency * 1000
        emb = discord.Embed(title="Please wait..", color=discord.Color.red())
        emb.add_field(
            name="Discord WS:", value=box(str(round(latency)) + " ms", "nim"), inline=True
        )
        emb.add_field(name="Typing", value=box("calculating" + " ms", "nim"), inline=True)
        emb.add_field(name="Message", value=box("…", "nim"), inline=True)

        before = time.monotonic()
        message = await ctx.reply(embed=emb, mention_author=False)
        ping = (time.monotonic() - before) * 1000

        emb.title = "Pong! 🏓"
        emb.color = 0xD0B2D8
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
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def invite(self, ctx: commands.Context):
        """Invite the bot to your server."""
        embed = discord.Embed(color=discord.Color.random(), title="<3")
        embed.description = (
            f"Invite Link: https://discord.com/api/oauth2/authorize?client_id={APPLICATION_ID}&scope=bot"
        )
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
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def stats(self, ctx: commands.Context):
        """Some stats about me."""
        text_channels = 0
        voice_channels = 0
        for chan in self.bot.get_all_channels():
            if isinstance(chan, discord.TextChannel):
                text_channels += 1
            if isinstance(chan, discord.VoiceChannel):
                voice_channels += 1
        embed = discord.Embed(title=f"{self.bot.user.name} Stats", color=discord.Color.random())
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
            name="Uptime:", value=f"{time_notation(datetime.now() - bot_start_time)}", inline=True
        )
        embed.add_field(
            name="Creation Date:", value=self.bot.user.created_at.strftime("%c"), inline=True
        )
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        embed.add_field(
            name="Github Repository:",
            value="Find it [here](https://github.com/Yat-o/HimejiBot/tree/rewrite)",
            inline=True,
        )
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        embed.set_footer(
            icon_url=ctx.author.avatar.url, text=f"{self.bot.user.name} was made with love. <3"
        )
        await ctx.send(embed=embed)

    @commands.command(usage="(project name)")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pypi(self, ctx, project: str):
        """Get information of a python project from pypi."""
        async with self.bot.session.get(f"https://pypi.org/pypi/{project}/json") as response:
            try:
                res = await response.json()
            except aiohttp.client_exceptions.ContentTypeError:
                e = discord.Embed(
                    title="404 - Page Not Found",
                    description="We looked everywhere but couldn't find that project",
                    colour=0x0073B7,
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


def setup(bot: commands.Bot):
    bot.add_cog(Miscellaneous(bot))
