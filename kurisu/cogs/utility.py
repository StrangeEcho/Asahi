from typing import Optional

from core import KurisuBot, KurisuContext, PrefixManager
from discord.ext import commands
from utilities import convert_permission_integer
import discord


class Utility(commands.Cog):
    """A module filled with informative commands. Could be info a bout a guild, user, etc"""

    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.prefixer = PrefixManager(self.bot)

    @commands.command(aliases=["sinfo", "ginfo", "guildinfo"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serverinfo(
        self, ctx: KurisuContext, guild: discord.Guild = None
    ):
        """Get information about a certain guild"""
        if guild is None:
            guild = ctx.guild
        guild_features = [
            f"✅ `{f.replace('_', ' ').title()}`" for f in guild.features
        ]
        embed = discord.Embed(title=guild.name, color=self.bot.info_color)
        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(
            name="Owner",
            value=f"Name: `{guild.owner}({guild.owner_id})`",
            inline=True,
        )
        embed.add_field(
            name="Creation Time",
            value=f"<t:{int(guild.created_at.timestamp())}:F>",
            inline=False,
        )
        embed.add_field(
            name="Member Count", value=f"**{guild.member_count}**", inline=True
        )
        embed.add_field(
            name="Role Count",
            value=f"`{len(guild.roles)}`",
            inline=True,
        )
        embed.add_field(
            name="Channel Count",
            value=f"Text: `{len(guild.text_channels)}`\n"
            f"Voice: `{len(guild.voice_channels)}`\n"
            f"Categories: `{len(guild.categories)}`\n"
            f"Total `{len(guild.text_channels) + len(guild.voice_channels) + len(guild.categories)}`",
            inline=True,
        )
        embed.add_field(
            name="Emoji Count",
            value=f"**{len(guild.emojis)}**",
            inline=True,
        )
        if guild_features:
            embed.add_field(
                name="Features", value="".join(guild_features), inline=False
            )
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        elif guild.splash:
            embed.set_image(url=guild.splash.url)

        embed.set_footer(text=f"ID: {guild.id}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["uinfo", "memberinfo", "minfo"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def userinfo(self, ctx: KurisuContext, user: discord.Member = None):
        """Returns info about a user"""
        if user is None:
            user = ctx.author

        user_flags = "\n".join(
            i.replace("_", " ").title() for i, v in user.public_flags if v
        )
        roles = user.roles[-1:0:-1]
        embed = discord.Embed(color=user.color or self.bot.info_color)
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Name", value=user)
        embed.add_field(name="ID", value=user.id)
        embed.add_field(
            name="Status & Activity",
            value=f"Status: {str(user.status).title()}\nActivity: {user.activity.name if user.activity else 'No Activity'}",
            inline=False,
        )
        embed.add_field(
            name="Account Creation",
            value=f"<t:{int(user.created_at.timestamp())}:F>",
        )
        embed.add_field(
            name=f"{ctx.guild} Join Date",
            value=f"<t:{int(user.joined_at.timestamp())}:F>"
            if user.joined_at
            else "Unknown.",
            inline=False,
        )
        if roles:
            embed.add_field(
                name=f"Roles **{(len(user.roles) - 1)}**",
                value=", ".join([x.mention for x in roles[:10]]),
                inline=False,
            )
        if user_flags:
            embed.add_field(
                name="Public User Flags",
                value=user_flags,
                inline=False,
            )
        if not user.bot:
            if banner := (await self.bot.fetch_user(user.id)).banner:
                embed.set_image(url=banner.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["rinfo"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def roleinfo(self, ctx: KurisuContext, *, role: discord.Role):
        """Returns info about a role"""
        await ctx.send(
            embed=discord.Embed(
                title=f"Role info for {role.name}", color=role.color
            )
            .add_field(name="ID", value=role.id, inline=True)
            .add_field(name="Color", value=role.color, inline=True)
            .add_field(
                name="Creation Time",
                value=role.created_at.strftime("%c"),
                inline=True,
            )
            .add_field(name="Members", value=len(role.members), inline=True)
            .add_field(name="Hoisted", value=role.hoist, inline=True)
            .add_field(name="Mentionable", value=role.mentionable, inline=True)
            .add_field(name="Position", value=role.position, inline=True)
            .add_field(
                name="Permissions (5)",
                value=f"\n".join(
                    [
                        p.replace("_", " ").title()
                        for p in convert_permission_integer(
                            role.permissions.value
                        )[:5]
                    ]
                ),
                inline=True,
            )
        )

    @commands.command(aliases=["einfo", "emoteinfo"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def emojiinfo(self, ctx: KurisuContext, emoji: discord.Emoji):
        """Returns information about a emoji/emote(Within the current guild)"""
        await ctx.send(
            embed=discord.Embed(
                title="Emoji Information", color=self.bot.ok_color
            )
            .add_field(name="ID", value=emoji.id, inline=False)
            .add_field(name="Animated", value=emoji.animated, inline=False)
            .add_field(name="Link", value=emoji.url, inline=False)
            .set_image(url=emoji.url)
        )

    @commands.command(aliases=["av"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def avatar(self, ctx: KurisuContext, user: Optional[discord.Member]):
        """Check your avatars."""
        await ctx.channel.trigger_typing()
        if user is None:
            user = ctx.author
        av = user.avatar
        e = discord.Embed(
            title=f"{user.name}'s avatar", color=self.bot.ok_color
        )
        e.add_field(
            name="File Formations",
            value=f"[jpg]({av.with_format('jpg')}), "
            f"[png]({av.with_format('png')}), "
            f"[webp]({av.with_format('webp')}){',' if av.is_animated() else ''} "
            f"{f'[gif]({av})' if av.is_animated() else ''}",
        )
        e.add_field(
            name="Animated", value="\u2705" if av.is_animated() else ":x:"
        )
        e.set_image(url=av.with_size(4096))
        e.set_footer(text=f"ID: {user.id}")
        await ctx.send(embed=e)

    @commands.command(aliases=["setnsfw"])
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def nsfw(self, ctx: KurisuContext):
        """Toggle nsfw flag on the current channel"""
        await ctx.channel.edit(nsfw=not ctx.channel.is_nsfw())
        await ctx.send_ok("there you go buddy...")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def setafkchannel(
        self, ctx: KurisuContext, channel: discord.VoiceChannel
    ):
        """Set the channel to where people go when they hit the AFK timeout. Pass in None for no Inactive Channel"""
        if not channel:
            return await ctx.send_ok("Invalid Voice Channel was passed")

        await ctx.guild.edit(afk_channel=channel)
        await ctx.send(f"Set AFK channel to {channel.name}")

    @commands.command(aliases=["cr"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def createrole(self, ctx: KurisuContext, *, name: str):
        """Create a role"""
        await ctx.guild.create_role(name=name)
        await ctx.send_ok(f"Created role with name '{name}'")

    @commands.command(aliases=["dr"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def deleterole(self, ctx: KurisuContext, *, role: discord.Role):
        """Delete a role"""
        await role.delete()
        await ctx.send_ok(f"Deleted role with name '{role.name}'")

    @commands.command(aliases=["commandprefix", "serverprefix"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def prefix(self, ctx: KurisuContext, prefix: str = None):
        """Set the guild's prefix"""
        if not prefix:
            return await ctx.send_info(
                f"Prefix for this guild {self.bot.prefixes.get(ctx.guild.id) or self.bot.config.get('prefix', 'Core')}"
                f" or {self.bot.user.mention}"
            )
        if len(prefix) > 10:
            return await ctx.send_error(
                "Prefix too long. Try again with a prefix under 10 characters"
            )
        await self.prefixer.add_prefix(ctx.guild.id, prefix)


def setup(bot):
    bot.add_cog(Utility(bot))
