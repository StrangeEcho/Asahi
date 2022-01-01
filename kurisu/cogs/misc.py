import os
import platform
import time

from discord.ext import commands, vbu
from utils.context import KurisuContext
from utils.funcs import box
from utils.kurisu import KurisuBot
import aiohttp
import discord
import humanize
import psutil


class Miscellaneous(commands.Cog):
    """A module full of many different misc commands."""

    def __init__(self, bot: KurisuBot):
        self.bot = bot

    @commands.has_permissions(embed_links=True)
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(
            self,
            ctx: KurisuContext,
    ):
        """Just a ping command"""
        latency = self.bot.latency * 1000
        emb = discord.Embed(title="Please wait..", color=self.bot.ok_color)
        emb.add_field(
            name="Discord WS:",
            value=box(str(round(latency)) + " ms", "nim"),
            inline=True,
        )
        emb.add_field(
            name="Typing", value=box("calculating" + " ms", "nim"), inline=True
        )
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
                str(
                    int(
                        (
                                message.created_at - ctx.message.created_at
                        ).total_seconds()
                        * 1000
                    )
                )
                + " ms",
                "nim",
            ),
            inline=True,
        )
        emb.set_field_at(
            2,
            name="Typing:",
            value=box(str(round(ping)) + " ms", "nim"),
            inline=True,
        )
        await message.edit(embed=emb)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def invite(self, ctx: KurisuContext):
        """Invite the bot to your server."""
        embed = discord.Embed(color=self.bot.ok_color, title="<3")
        embed.description = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=413893192823&scope=bot"
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
    async def support(self, ctx: KurisuContext):
        await ctx.send(
            embed=discord.Embed(
                description=f"Come see me and my master and the rest of my robotic brothers and sisters [here](https://discord.gg/Cs5RdJF9pb)",
                color=self.bot.ok_color,
            ).set_thumbnail(url=self.bot.user.avatar.url)
        )

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stats(self, ctx: KurisuContext):
        """Some stats about me."""
        text_channels = 0
        voice_channels = 0
        owners = [
            self.bot.get_user(o)
            for o in self.bot.get_config("config", "config", "owner_ids")
        ]
        process = psutil.Process(os.getpid())
        for chan in self.bot.get_all_channels():
            if isinstance(chan, discord.TextChannel):
                text_channels += 1
            if isinstance(chan, discord.VoiceChannel):
                voice_channels += 1
        embed = discord.Embed(
            title=f"{self.bot.user.name} Stats",
            color=self.bot.ok_color,
        )
        embed.set_author(icon_url=self.bot.user.avatar.url, name="General")
        embed.description = "Click [Here](https://discord.com/api/oauth2/authorize?client_id={}&scope=bot) To Invite Me and Click [Here](https://discord.gg/Cs5RdJF9pb) To Join My Support Server".format(
            self.bot.get_config("config", "config", "application_id")
        )
        embed.add_field(
            name="Owner(s)", value="\n".join(map(str, owners)), inline=False
        )
        embed.add_field(
            name="Mention & ID",
            value=f"{self.bot.user.mention}\n`{self.bot.user.id}`",
            inline=False,
        )
        embed.add_field(
            name="I was created at...",
            value=f"<t:{int(self.bot.user.created_at.timestamp())}:F>",
            inline=False,
        )
        embed.add_field(
            name="Prefix",
            value=f"`{self.bot.prefixes.get(str(ctx.guild.id)) or self.bot.get_config('config', 'config', 'prefix')}` or {self.bot.user.mention}",
            inline=False,
        )
        embed.set_footer(
            icon_url=self.bot.user.avatar.url,
            text=f"{self.bot.user.name} was made with love <3",
        )
        embed2 = discord.Embed(
            title=f"{self.bot.user.name} Stats",
            description="Find My Source [Here](https://github.com/Yat-o/Kurisu/tree/rewrite)",
            color=self.bot.ok_color,
        )
        embed2.set_author(icon_url=self.bot.user.avatar.url, name="Statistics")
        embed2.add_field(
            name="On-Board Memory Usage",
            value=f"{round(process.memory_info().rss / 1024 ** 2)} MBs",
            inline=False,
        )
        embed2.add_field(
            name=f"Websocket Latency",
            value=f"{round(self.bot.latency * 1000)} ms",
            inline=False,
        )
        embed2.add_field(name="Shard Count", value=len(self.bot.shards))
        embed2.add_field(
            name="Cached Users & Guilds",
            value=f"Users: {len(self.bot.users)}\nGuilds: {len(self.bot.guilds)}",
            inline=False,
        )
        embed2.add_field(
            name="Channels",
            value=f"Text: {text_channels}\nVoice: {voice_channels}",
            inline=False,
        )
        embed2.add_field(
            name="Uptime",
            value=f"{humanize.time.naturaldelta(discord.utils.utcnow() - self.bot.uptime)}",
            inline=False,
        )
        embed2.add_field(
            name="Commands Executed Since Startup",
            value=self.bot.executed_commands,
            inline=False,
        )
        embed3 = discord.Embed(
            title=f"{self.bot.user.name} Stats", color=self.bot.ok_color
        )
        embed3.set_author(icon_url=self.bot.user.avatar.url, name="About Me")
        embed3.add_field(
            name="Bot Version", value=f"`{self.bot.version}`", inline=False
        )
        embed3.add_field(
            name="Python Version",
            value=f"[{platform.python_version()}](https://python.org)",
            inline=False,
        )
        embed3.add_field(
            name="Novus(Discord.py) Version",
            value=f"[{discord.__version__}](https://discordpy.readthedocs.io/en/master/index.html)",
            inline=False,
        )
        await vbu.Paginator([embed, embed2, embed3], per_page=1).start(ctx)

    @commands.command(usage="(project name)")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pypi(self, ctx: KurisuContext, project: str):
        """Get information of a python project from pypi."""
        async with self.bot.session.get(
                f"https://pypi.org/pypi/{project}/json"
        ) as response:
            try:
                res = await response.json()
            except aiohttp.client_exceptions.ContentTypeError:
                e = discord.Embed(
                    title="404 - Page Not Found",
                    description="We looked everywhere but couldn't find that project",
                    colour=self.bot.error_color,
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
                value="\n".join(
                    [
                        f"[{x}]({y})"
                        for x, y in dict(info["project_urls"]).items()
                    ]
                ),
            )
            e.add_field(
                name="License", value=info["license"] or "`Not specified.`"
            )
            await ctx.reply(embed=e, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def uptime(self, ctx: KurisuContext):
        """Shows bot's uptime."""
        since = self.bot.uptime.strftime("%H:%M:%S UTC | %Y-%m-%d")
        delta = discord.utils.utcnow() - self.bot.uptime
        uptime_text = (
                humanize.time.precisedelta(delta) or "Less than one second."
        )
        embed = discord.Embed(colour=self.bot.ok_color)
        embed.add_field(
            name=f"{self.bot.user.name} has been up for:", value=uptime_text
        )
        embed.set_footer(text=f"Since: {since}")
        await ctx.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
