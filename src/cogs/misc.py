import platform
from datetime import datetime

import disnake
from disnake.ext import commands
from kurisu import Kurisu
from kurisu import KurisuContext
from kurisu.database import PrefixManager
from exts import humanize_timedelta, get_version_hash


class Miscellaneous(
    commands.Cog, command_attrs={"cooldown": commands.CooldownMapping.from_cooldown(1, 2.5, commands.BucketType.user)}
):
    """Commands that don't fit anywhere else"""

    def __init__(self, bot: Kurisu):
        self.bot = bot
        self.pm = PrefixManager(self.bot)

    @commands.command()
    async def ping(self, ctx: KurisuContext):
        """Get the bot's latency"""
        shards = [f"Shard {_id}: {round(latency * 1000)} ms" for _id, latency in self.bot.latencies]

        embed = (
            disnake.Embed(description="Pong!", color=self.bot.info_color)
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
                embed=disnake.Embed(
                    title="Thank you for inviting me <3",
                    url=f"https://disnake.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=413893192823&scope=bot",  # noqa e501
                    color=self.bot.ok_color,
                ).set_thumbnail(url=self.bot.user.display_avatar.url)
            )
            await ctx.send_ok("DMed you with Invite Link!")
        except (disnake.Forbidden, disnake.HTTPException):
            await ctx.send_error("Could not DM you with my invite link", trash=True)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx: KurisuContext, *, prefix: str = None):
        """Prefix manager command"""
        if not prefix:
            return await ctx.send_info(
                f"Prefix for this guild is: `{self.bot.prefixes.get(ctx.guild.id) or self.bot.config.get('prefix')}`"
            )
        await self.pm.add_prefix(ctx.guild.id, prefix)
        await ctx.send_ok(f"Set this guild's prefix to `{prefix}`")

    @commands.command()
    async def about(self, ctx: KurisuContext):
        """Info about the bot"""

        uptime = humanize_timedelta(datetime.now() - self.bot.start_time)

        await ctx.send(
            embed=disnake.Embed(title=f"Information for {self.bot.user.name}", color=self.bot.info_color)
            .add_field(name="Novus", value=f"`{disnake.__version__}`")
            .add_field(name="Python", value=f"`{platform.python_version()}`")
            .add_field(name=f"{self.bot.user.name} Version", value=f"`{get_version_hash()}`")
            .add_field(name="Uptime", value=f"`{uptime}`")
            .add_field(name="Ping", value=f"`{round(self.bot.latency * 1000)}ms`")
        )


def setup(bot: Kurisu):
    bot.add_cog(Miscellaneous(bot))
