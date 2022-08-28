from datetime import datetime
import os
import platform

from discord.ext import commands
import discord
import psutil

from core import Asahi, AsahiContext, PrefixHandler
from exts import humanize_timedelta, Paginator


class Meta(
    commands.Cog, command_attrs={"cooldown": commands.CooldownMapping.from_cooldown(1, 3.5, commands.BucketType.user)}
):
    """Base commands"""

    def __init__(self, bot: Asahi):
        self.bot = bot
        self.prefix_handler = PrefixHandler(self.bot)

    @commands.command()
    async def ping(self, ctx: AsahiContext):
        """Obligitory ping command"""
        msg = await ctx.send("Measuring now...")
        await msg.edit(
            content=None,
            embed=discord.Embed(description=f"Ping for {self.bot.user}", color=self.bot.info_color)
            .add_field(name="WebSocket Latency", value=f"{round(self.bot.latency * 1000)}ms")
            .add_field(
                name="Message", value=f"{round((msg.created_at - ctx.message.created_at).total_seconds() * 1000)}ms"
            ),
        )

    @commands.command()
    async def prefix(self, ctx: AsahiContext, *, prefix: str = None):
        """Set a guilds custom prefix. If none provided the set one will be provided"""
        if not prefix:
            return await ctx.send_info(f"This guild's prefix is `{self.bot.get_custom_prefix(ctx.guild.id)}`")
        if ctx.author.guild_permissions.manage_guild:
            self.prefix_handler.add_prefix(prefix[:10], ctx.guild.id)
            await ctx.send_ok("Prefix set!")
        else:
            await ctx.send_error("You are lacking the required permission to run this command: `Manage Server`")

    @commands.command()
    async def credits(self, ctx: AsahiContext):
        """Yes..."""
        await ctx.send(
            embed=discord.Embed(
                title="Credits",
                description=(
                    "Author: [Yat-o](https://github.com/Yat-o)\n"
                    "Contributors: A Full list can be found [here](https://github.com/Yat-o/Asahi/graphs/contributors)\n"
                    f"Registered Bot Owners: {', '.join([str(await self.bot.fetch_user(o)) for o in self.bot.owner_ids])}\n"
                    "Source Code: Can be found [here](https://github.com/Yat-o/Asahi/) "
                ),
            ).set_thumbnail(url=self.bot.user.avatar.url)
        )

    @commands.command()
    async def invite(self, ctx: AsahiContext):
        """Dms you with an invite link to invite the bot with"""
        await ctx.send_info(
            f"Invite me using [this link](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=413893192823&scope=bot)"
        )

    @commands.command()
    async def about(self, ctx: AsahiContext):
        """Information about the bot"""
        pid = os.getpid()
        memory_usage = round(psutil.Process(pid).memory_info().rss / 1024**2)
        total_memory = round(psutil.virtual_memory().total / 1024**2)
        cpu_usage = psutil.Process(pid).cpu_percent(interval=2)

        embed = (
            discord.Embed(
                title="About Me", description=f"{self.bot.user} | {self.bot.user.id}", color=self.bot.info_color
            )
            .add_field(name="Creation Date", value=discord.utils.format_dt(self.bot.user.created_at, "F"))
            .add_field(
                name="Registered Owner(s)",
                value=", ".join([f"`{await self.bot.getch_user(u)}`" for u in self.bot.owner_ids]),
            )
            .add_field(
                name="Uptime",
                value=humanize_timedelta(datetime.now() - self.bot.startup_time, precise=True),
                inline=False,
            )
            .add_field(name="Discord WebSocket Latency", value=f"{round(self.bot.latency * 1000)}ms")
            .add_field(
                name="Library & Language",
                value=f"Python: {platform.python_version()} | Discord.py: {discord.__version__}",
                inline=False,
            )
            .set_thumbnail(url=self.bot.user.avatar.url)
            .set_footer(text=f"Asahi Version {self.bot.__version__}")
        )

        embed2 = (
            discord.Embed(title="Statistics", color=self.bot.info_color)
            .add_field(name="Guild Count", value=len(self.bot.guilds))
            .add_field(name="User Count", value=len(self.bot.users))
            .add_field(
                name="Command Usage",
                value=f"Total Commands: {len(self.bot.commands)} | Used Since Startup: {self.bot.commands_ran}",
                inline=False,
            )
        )

        embed3 = (
            discord.Embed(title="Process Information", color=self.bot.info_color)
            .add_field(name="CPU Usage", value=f"{cpu_usage}%")
            .add_field(name="Memory Usage", value=f"{memory_usage}Mb of {total_memory}Mb")
        )
        await Paginator([embed, embed2, embed3]).start(ctx)


async def setup(bot: Asahi):
    await bot.add_cog(Meta(bot))
