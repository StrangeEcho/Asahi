import platform
from datetime import datetime

import discord
from discord.ext import commands
from config import APPLICATION_ID
from utils.funcs import time_notation
from utils.vars import bot_start_time
class Miscellaneous(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Obligitory ping command that shows Websocket latency"""
        await ctx.send(
            embed=discord.Embed(
                title=":ping_pong: Pong!",
                description=f"Websocket: {round(self.bot.latency * 1000)}ms",
                color=discord.Color.random(),
            ).set_thumbnail(url=self.bot.user.avatar.url)
        )

    @commands.command()
    async def invite(self, ctx: commands.Context):
        try:
            await ctx.author.send(embed=discord.Embed(
                title="<3",
                description=f"Invite link: https://discord.com/api/oauth2/authorize?client_id={APPLICATION_ID}&scope=bot",
                color=discord.Color.random()
            )
            .set_footer(text="Thank you for inviting Himeji Bot <3")
            )
            await ctx.send("Sent!")
        except discord.Forbidden:
            await ctx.send("Invite message failed. Please check your accounts privacy settings.")

    @commands.command()
    async def stats(self, ctx: commands.Context):
        text_channels = 0
        voice_channels = 0
        for chan in self.bot.get_all_channels():
            if isinstance(chan, discord.TextChannel):
                text_channels += 1
            if isinstance(chan, discord.VoiceChannel):
                voice_channels += 1
        await ctx.send(embed=discord.Embed(
            title="Himeji Stats",
            color=discord.Color.random()
        )
        .set_thumbnail(url=self.bot.user.avatar.url)
        .add_field(name="Author:", value="Tylerr#6979", inline=True)
        .add_field(name="Python Versions:", value=f"Python Version: {platform.python_version()}\nDiscord.py Version: {discord.__version__}", inline=True)
        .add_field(name="Websocket Latency", value=f"{round(self.bot.latency * 1000)}ms")
        .add_field(name="Bot ID:", value=self.bot.user.id, inline=True)
        .add_field(name="Guild Count:", value=len(self.bot.guilds), inline=True)
        .add_field(name="Cached Users:", value=len(self.bot.users), inline=True)
        .add_field(name="Channels:", value=f"Text: {text_channels}\nVoice: {voice_channels}\nTotal: {text_channels + voice_channels}", inline=True)
        .add_field(name="Uptime:", value=f"{time_notation(datetime.now() - bot_start_time)}", inline=True)
        .add_field(name="Creation Date:", value=self.bot.user.created_at.strftime("%c"), inline=True)
        .add_field(name="\u200B", value="\u200B", inline=True)
        .add_field(name="Github Repository:", value="Find it [here](https://github.com/Yat-o/HimejiBot/tree/rewrite)", inline=True)
        .add_field(name="\u200B", value="\u200B", inline=True)
        .set_footer(icon_url=ctx.author.avatar.url, text=f"{self.bot.user.name} was move with love. <3")
        )


def setup(bot: commands.Bot):
    bot.add_cog(Miscellaneous(bot))
