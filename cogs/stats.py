import discord
import config
import platform
import psutil
import os

from datetime import datetime
from utils.misc import time_notation
from utils.misc import bot_start_time

from discord.ext import commands
from EZPaginator import Paginator


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["botstats", "info"])
    @commands.bot_has_permissions(embed_links=True)
    async def stats(self, ctx):
        """Shows different bot statistics."""

        bot_memory_usage = round(
            psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
        )

        embed = discord.Embed(title="Himeji Stats", color=0xFFB6C1)
        embed.set_author(name="Basics")
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Mention:", value=self.bot.user.mention, inline=True)
        embed.add_field(name="Owner:", value="Tylerr#6979", inline=True)
        embed.add_field(
            name="Prefix:",
            value=f"`{config.BOT_PREFIX}` or {self.bot.user.mention}",
            inline=True,
        )
        embed.add_field(
            name="Uptime:",
            value=time_notation(datetime.now() - bot_start_time),
            inline=True,
        )
        embed.add_field(
            name="Latency:",
            value=f"{self.bot.latency * 1000} Milliseconds",
            inline=True,
        )
        embed.add_field(
            name="Memory Usage:", value=f"{bot_memory_usage} Mb", inline=True
        )
        embed.add_field(
            name="Using Discord.py Version:",
            value=f"[{discord.__version__}](https://discordpy.readthedocs.io/en/latest/)",
            inline=True,
        )
        embed.add_field(
            name=" Using Python Version:",
            value=f"[{platform.python_version()}](https://www.python.org)",
            inline=True,
        )
        embed.set_footer(
            icon_url=ctx.author.avatar_url,
            text=f"Information Requested By {ctx.author.display_name}",
        )

        text_channels = 0
        voice_channels = 0
        for channel in self.bot.get_all_channels():
            if isinstance(channel, discord.TextChannel):
                text_channels += 1
            if isinstance(channel, discord.VoiceChannel):
                voice_channels += 1
        embed2 = discord.Embed(title="Himeji Stats", color=0xFFB6C1)
        embed2.set_author(name="Presence")
        embed2.set_thumbnail(url=self.bot.user.avatar_url)
        embed2.add_field(
            name="Cached Guilds:", value=(len(self.bot.guilds)), inline=True
        )
        embed2.add_field(name="Total Text Channels:", value=text_channels, inline=True)
        embed2.add_field(
            name="Total Voice Channels:", value=voice_channels, inline=True
        )
        embed2.add_field(name="Cached Users:", value=(len(self.bot.users)), inline=True)
        embed2.set_footer(
            icon_url=ctx.author.avatar_url,
            text=f"Information Requested By {ctx.author.display_name}",
        )
        # VPS Stats Variables
        # Ram & CPU Usage Variables
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent

        # Network Variables
        nbs = psutil.net_io_counters().bytes_sent
        nbr = psutil.net_io_counters().bytes_recv
        nps = psutil.net_io_counters().packets_sent
        npr = psutil.net_io_counters().packets_recv

        embed3 = discord.Embed(title="Himeji Stats", color=0xFFB6C1)
        embed3.set_author(name="VPS Statistics")
        embed3.set_thumbnail(url=self.bot.user.avatar_url)
        embed3.add_field(name="CPU Usage:", value=f"{cpu_usage}%", inline=True)
        embed3.add_field(name="Ram Usage:", value=f"{ram_usage}%", inline=True)
        embed3.add_field(
            name="Network Statistics",
            value=f"Bytes Sent: {nbs}\nBytes Recieved: {nbr}\nPackets Sent: {nps}\nPackets Recieved: {npr}",
            inline=True,
        )
        embed3.set_footer(
            icon_url=ctx.author.avatar_url,
            text=f"Information Requested By {ctx.author.display_name}",
        )

        embeds = [embed, embed2, embed3]

        msg = await ctx.send(embed=embed)
        page = Paginator(self.bot, msg, embeds=embeds)
        await page.start()


def setup(bot):
    bot.add_cog(Stats(bot))
