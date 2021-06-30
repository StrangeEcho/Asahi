from io import BytesIO
from typing import cast, Union

from discord.ext import commands
import discord

from utils.classes import HimejiBot


class Utility(commands.Cog):
    """Some utility commands"""

    def __init__(self, bot: HimejiBot):
        self.bot = bot

    @commands.command(aliases=["sinfo", "ginfo", "guildinfo"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serverinfo(self, ctx: commands.Context, guild: discord.Guild = None):
        """Get information about a certain guild"""
        if guild is None:
            guild = ctx.guild

        weird_stuff = {
            "ANIMATED_ICON": ("Animated Icon"),
            "BANNER": ("Banner Image"),
            "COMMERCE": ("Commerce"),
            "COMMUNITY": ("Community"),
            "DISCOVERABLE": ("Server Discovery"),
            "FEATURABLE": ("Featurable"),
            "INVITE_SPLASH": ("Splash Invite"),
            "MEMBER_LIST_DISABLED": ("Member list disabled"),
            "MEMBER_VERIFICATION_GATE_ENABLED": ("Membership Screening enabled"),
            "MORE_EMOJI": ("More Emojis"),
            "NEWS": ("News Channels"),
            "PARTNERED": ("Partnered"),
            "PREVIEW_ENABLED": ("Preview enabled"),
            "PUBLIC_DISABLED": ("Public disabled"),
            "VANITY_URL": ("Vanity URL"),
            "VERIFIED": ("Verified"),
            "VIP_REGIONS": ("VIP Voice Servers"),
            "WELCOME_SCREEN_ENABLED": ("Welcome Screen enabled"),
        }
        guild_features = [
            f"✅ {name}\n"
            for weird_stuff, name in weird_stuff.items()
            if weird_stuff in guild.features
        ]
        embed = discord.Embed(title=guild.name, color=self.bot.ok_color)
        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(
            name="Owner", value=f"Name: **{guild.owner}**\nID: **{guild.owner.id}**", inline=True
        )
        embed.add_field(name="Server ID", value=f"**{guild.id}**", inline=True)
        embed.add_field(name="Creation Time", value=guild.created_at.strftime("%c"), inline=False)
        embed.add_field(name="Region", value=str(guild.region).upper(), inline=True)
        embed.add_field(name="Member Count", value=f"**{guild.member_count}**", inline=True)
        embed.add_field(name="Role Count", value="**{}**".format(len(guild.roles)), inline=False)
        embed.add_field(
            name="Channel Count",
            value=f"Categories: **{len(guild.categories)}**\nText: **{len(guild.text_channels)}**\nVoice: **{len(guild.voice_channels)}**\nTotal: **{len(guild.text_channels) + len(guild.voice_channels)}**",
            inline=True,
        )
        embed.add_field(name="Emoji Count", value="**{}**".format(len(guild.emojis)), inline=True)
        if guild_features:
            embed.add_field(name="Features", value="".join(guild_features), inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["uinfo", "memberinfo", "minfo"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def userinfo(self, ctx: commands.context, user: discord.Member = None):
        """Returns info about a user"""
        if user is None:
            user = ctx.author

        user_flags = "\n".join(i.replace("_", " ").title() for i, v in user.public_flags if v)
        roles = user.roles[-1:0:-1]
        embed = discord.Embed(color=user.color or self.bot.ok_color)
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Name", value=user)
        embed.add_field(name="ID", value=user.id)
        embed.add_field(
            name="Status & Activity", value=f"Status: {user.status}\nActivity: {user.activity}"
        )
        embed.add_field(
            name="Account Creation",
            value=user.created_at.strftime("%c"),
        )
        embed.add_field(
            name=f"{ctx.guild} Join Date", value=user.joined_at.strftime("%c"), inline=False
        )
        if roles:
            embed.add_field(
                name=f"Roles **{(len(user.roles) - 1)}**",
                value=", ".join([x.mention for x in roles[:10]]),
                inline=False,
            )
        if user_flags:
            embed.add_field(name="Public User Flags", value=user_flags.upper(), inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["rinfo"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def roleinfo(self, ctx: commands.Context, *, role: discord.Role):
        """Returns info about a role"""
        await ctx.send(
            embed=discord.Embed(title=f"Role info for {role.name}", color=role.color)
            .add_field(name="ID", value=role.id, inline=True)
            .add_field(name="Color", value=role.color, inline=True)
            .add_field(name="Creation Time", value=role.created_at.strftime("%c"), inline=True)
            .add_field(name="Members", value=len(role.members), inline=True)
            .add_field(name="Hoisted", value=role.hoist, inline=True)
            .add_field(name="Mentionable", value=role.mentionable, inline=True)
            .add_field(name="Position", value=role.position, inline=True)
            .add_field(
                name="Permissions",
                value=f"Click [Here](https://cogs.fixator10.ru/permissions-calculator/?v={role.permissions.value})",
                inline=True,
            )
        )

    @commands.command(aliases=["einfo", "emoteinfo"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def emojiinfo(self, ctx: commands.Context, emoji: discord.Emoji):
        """Returns information about a emoji/emote(Within the current guild)"""
        await ctx.send(
            embed=discord.Embed(title="Emoji Information", color=self.bot.ok_color)
            .add_field(name="ID", value=emoji.id, inline=False)
            .add_field(name="Animated", value=emoji.animated, inline=False)
            .add_field(name="Link", value=emoji.url, inline=False)
            .set_image(url=emoji.url)
        )

    @commands.command(aliases=["se", "bigmoji", "jumbo"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bigemoji(
        self,
        ctx: commands.Context,
        emoji: Union[discord.Emoji, discord.PartialEmoji, str],
    ) -> None:
        """
        Get a emoji in big size lol
        """
        await ctx.channel.trigger_typing()
        if type(emoji) in [discord.PartialEmoji, discord.Emoji]:
            aa_emoji = cast(discord.Emoji, emoji)
            ext = "gif" if aa_emoji.animated else "png"
            url = "https://cdn.discordapp.com/emojis/{id}.{ext}?v=1".format(
                id=aa_emoji.id, ext=ext
            )
            filename = "{name}.{ext}".format(name=aa_emoji.name, ext=ext)
        else:
            try:
                """https://github.com/glasnt/emojificate/blob/master/emojificate/filter.py"""
                cdn_fmt = "https://twemoji.maxcdn.com/2/72x72/{codepoint:x}.png"
                url = cdn_fmt.format(codepoint=ord(str(emoji)))
                filename = "emoji.png"
            except TypeError:
                return await ctx.send("That doesn't appear to be a valid emoji")
        try:
            async with self.bot.session.get(url) as resp:
                image = BytesIO(await resp.read())
        except Exception:
            return await ctx.send("That doesn't appear to be a valid emoji")
        await ctx.send(file=discord.File(image, filename=filename))


def setup(bot):
    bot.add_cog(Utility(bot))
