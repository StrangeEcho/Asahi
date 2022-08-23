from typing import Union

from discord.ext import commands
import discord

from core import Asahi, AsahiContext


class Utility(
    commands.Cog, command_attrs={"cooldown": commands.CooldownMapping.from_cooldown(1, 3.5, commands.BucketType.user)}
):
    """Utility styled commands"""

    def __init__(self, bot: Asahi):
        self.bot = bot

    def asset_formatter(self, asset: discord.Asset) -> dict[str, discord.Asset]:
        x = {}
        for fmt in ["jpg", "jpeg", "webp", "png"]:
            x[fmt] = asset.with_format(fmt)
        if asset.is_animated():
            x["gif"] = asset.with_format("gif")
        return x

    @commands.command(aliases=["memberinfo", "uinfo", "minfo"])
    @commands.guild_only()
    async def userinfo(self, ctx: AsahiContext, *, user: discord.Member = None):
        """Retrieve information about a user on discord"""
        user = user or ctx.author
        flags = [i.name.replace("_", " ").title() for i in user.public_flags.all()]
        roles = [r for r in user.roles if r.id != ctx.guild.id]

        embed = (
            discord.Embed(title=f"Information for {user}", description=f"ID: {user.id}", color=user.top_role.color)
            .add_field(
                name="Status & Activity",
                value=f"Status: {user.status.name.title()}\nActivity: {'' if not user.activity else user.activity.name}",
            )
            .add_field(name="Account Creation", value=discord.utils.format_dt(user.created_at, "F"))
            .add_field(name=f"{ctx.guild} Join Date", value=discord.utils.format_dt(user.joined_at, "F"))
            .set_thumbnail(url=user.avatar.url)
        )
        if roles:
            embed.add_field(name=f"Roles | {len(roles)}", value=", ".join([r.mention for r in roles[:5]]))
        if flags:
            embed.add_field(name="Flags", value=", ".join([f"`{flag}`" for flag in flags]))
        if not user.bot:
            if banner := (await self.bot.fetch_user(user.id)).banner:
                embed.set_image(url=banner.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["sinfo", "guildinfo", "ginfo"])
    @commands.guild_only()
    async def serverinfo(self, ctx: AsahiContext):
        """Retrieve information about this guild"""
        g = ctx.guild
        channels: dict[str, int] = {}
        features: list[str] = [f.replace("_", " ").title() for f in g.features]
        for typ in discord.ChannelType.__members__.keys():
            channels[typ] = 0
        for channel in g.channels:
            channels[str(channel.type)] += 1
        embed = (
            discord.Embed(
                title=f"Information for {g}",
                description=f"ID: {g.id}",
                color=discord.Color.random(),
            )
            .set_thumbnail(url=g.icon.url)
            .add_field(name="Owner", value=f"{g.owner} [{g.owner.id}]")
            .add_field(name="Created at", value=discord.utils.format_dt(g.created_at, "F"), inline=False)
            .add_field(name="Roles", value=len(g.roles) - 1)  # Accounting for @everyone
            .add_field(name="Emote Count", value=f"{len(g.emojis)} of {g.emoji_limit}")
            .add_field(name="Member Count", value=f"{len(g.members)} Total members")
            .add_field(
                name="Channel Breakdown",
                value="\n".join([f"{k.replace('_', ' ').title()}: **{v}**" for k, v in channels.items()]),
                inline=False,
            )
            .add_field(name="Features", value=", ".join([f"`{feature}`" for feature in features]), inline=False)
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["rinfo"])
    @commands.guild_only()
    async def roleinfo(self, ctx: AsahiContext, *, role: discord.Role):
        """Retrieved information about a role"""
        embed = (
            discord.Embed(title=f"Information for {role}", description=f"ID: {role.id}", color=role.color)
            .add_field(name="Posistion", value=role.position)
            .add_field(name="Hoisted", value="✅" if role.hoist else "❌")
            .add_field(name="Created at", value=discord.utils.format_dt(role.created_at, "F"))
            .add_field(name="Manageable", value="✅" if role.managed else "❌")
            .add_field(name="Color Hex", value=str(role.color).replace("0x", "#"))
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["cinfo", "chaninfo"])
    @commands.guild_only()
    async def channelinfo(
        self,
        ctx: AsahiContext,
        *,
        channel: Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel] = None,
    ):
        channel = channel or ctx.channel
        """Retreive information about a guild channel"""
        embed = (
            discord.Embed(title=f"Info for {channel}", description=f"ID: {channel.id}", color=self.bot.info_color)
            .add_field(name="Category", value=channel.category)
            .add_field(name="Permission Synced", value="✅" if channel.permissions_synced else "❌")
            .add_field(name="Created at", value=discord.utils.format_dt(channel.created_at, "F"))
            .add_field(name="Posistion", value=channel.position)
        )
        if isinstance(channel, (discord.TextChannel, discord.CategoryChannel)):
            embed.add_field(name="NSFW", value="✅" if channel.nsfw else "❌")
        if isinstance(channel, discord.VoiceChannel):
            embed.add_field(name="Bitrate", value=f"{channel.bitrate / 1000} Kbps").add_field(
                name="Member limit", value=channel.user_limit
            )
        await ctx.send(embed=embed)

    @commands.command(aliases=["einfo"])
    @commands.guild_only()
    async def emojiinfo(self, ctx: AsahiContext, *, emoji: Union[discord.PartialEmoji, discord.Emoji]):
        """Retreieve information about an emoji"""
        embed = (
            discord.Embed(title=f"Info for {emoji.name}", value=f"{emoji} | ID: {emoji.id}", color=self.bot.info_color)
            .add_field(name="Animated", value="✅" if emoji.animated else "❌")
            .add_field(name="Url", value=emoji.url)
        )
        if isinstance(emoji, discord.Emoji):
            embed.add_field(name="Available", value="✅" if emoji.available else "❌").add_field(
                name="Requires Colons", value="✅" if emoji.require_colons else "❌"
            )
        await ctx.send(embed=embed)

    @commands.command(aliases=["av"])
    @commands.guild_only()
    async def avatar(self, ctx: AsahiContext, *, member: discord.Member = None):
        """Show a user's avatar"""
        member = member or ctx.author
        await ctx.send(
            embed=discord.Embed(
                title=f"Avatar for {member}",
                description=", ".join([f"[{k}]({v.url})" for k, v in self.asset_formatter(member.avatar).items()]),
                color=discord.Color.random(),
            ).set_image(url=member.avatar.url)
        )


async def setup(bot: Asahi):
    await bot.add_cog(Utility(bot))
