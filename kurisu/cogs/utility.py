from io import BytesIO
from typing import cast, Optional, Union
import io

from PIL import Image, ImageDraw
from discord.ext import commands
from utils.context import KurisuContext
from utils.dbmanagers import TodoManager
from utils.kurisu import KurisuBot
import discord


class Utility(commands.Cog):
    """A module filled with informative commands. Could be info a bout a guild, user, etc"""

    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.tm = TodoManager(self.bot)

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 3.5, commands.BucketType.user)
    async def todo(self, ctx: KurisuContext):
        """TODO management commands"""
        await ctx.send_help(ctx.command)

    @todo.command()
    @commands.cooldown(1, 3.5, commands.BucketType.user)
    async def add(self, ctx: KurisuContext, *, item: str):
        """Add to your list of todos"""
        await self.tm.add_todo(ctx.author.id, item)
        await ctx.send(":ok_hand:")

    @todo.command()
    @commands.cooldown(1, 1.5, commands.BucketType.user)
    async def list(self, ctx: KurisuContext):
        """List all of your todo items"""
        items = await self.tm.fetch_todos(ctx.author.id)
        if not items:
            return await ctx.send_error("No todos found for you.")

        await ctx.send(
            embed=discord.Embed(
                title=f"Todo items for {ctx.author}",
                description="\n".join([f"{n}. {v[0]}" for n, v in enumerate(items, 1)]),
                color=self.bot.ok_color
            )
        )

    @todo.command()
    @commands.cooldown(1, 3.5, commands.BucketType.user)
    async def remove(self, ctx: KurisuContext, item_number: int):
        """Remove a todo item"""
        await self.tm.remove_todo(ctx.author.id, item_number)
        await ctx.send(":ok_hand:")

    @commands.command()
    async def color(self, ctx: KurisuContext, clr: str):
        colors = {
            "aliceblue": ["#f0f8ff", "0xf0f8ff"],
            "antiquewhite": ["#faebd7", "0xfaebd7"],
            "aqua": ["#00ffff", "0x00ffff"],
            "aquamarine": ["#7fffd4", "0x7fffd4"],
            "azure": ["#f0ffff", "0xf0ffff"],
            "beige": ["#f5f5dc", "0xf5f5dc"],
            "bisque": ["#ffe4c4", "0xffe4c4"],
            "black": ["#000000", "0x000000"],
            "blanchedalmond": ["#ffebcd", "0xffebcd"],
            "blue": ["#0000ff", "0x0000ff"],
            "blueviolet": ["#8a2be2", "0x8a2be2"],
            "brown": ["#a52a2a", "0xa52a2a"],
            "burlywood": ["#deb887", "0xdeb887"],
            "cadetblue": ["#5f9ea0", "0x5f9ea0"],
            "chartreuse": ["#7fff00", "0x7fff00"],
            "chocolate": ["#d2691e", "0xd2691e"],
            "coral": ["#ff7f50", "0xff7f50"],
            "cornflowerblue": ["#6495ed", "0x6495ed"],
            "cornsilk": ["#fff8dc", "0xfff8dc"],
            "crimson": ["#dc143c", "0xdc143c"],
            "cyan": ["#00ffff", "0x00ffff"],
            "darkblue": ["#00008b", "0x00008b"],
            "darkcyan": ["#008b8b", "0x008b8b"],
            "darkgoldenrod": ["#b8860b", "0xb8860b"],
            "darkgray": ["#a9a9a9", "0xa9a9a9"],
            "darkgrey": ["#a9a9a9", "0xa9a9a9"],
            "darkgreen": ["#006400", "0x006400"],
            "darkkhaki": ["#bdb76b", "0xbdb76b"],
            "darkmagenta": ["#8b008b", "0x8b008b"],
            "darkolivegreen": ["#556b2f", "0x556b2f"],
            "darkorange": ["#ff8c00", "0xff8c00"],
            "darkorchid": ["#9932cc", "0x9932cc"],
            "darkred": ["#8b0000", "0x8b0000"],
            "darksalmon": ["#e9967a", "0xe9967a"],
            "darkseagreen": ["#8fbc8f", "0x8fbc8f"],
            "darkslateblue": ["#483d8b", "0x483d8b"],
            "darkslategray": ["#2f4f4f", "0x2f4f4f"],
            "darkslategrey": ["#2f4f4f", "0x2f4f4f"],
            "darkturquoise": ["#00ced1", "0x00ced1"],
            "darkviolet": ["#9400d3", "0x9400d3"],
            "deeppink": ["#ff1493", "0xff1493"],
            "deepskyblue": ["#00bfff", "0x00bfff"],
            "dimgray": ["#696969", "0x696969"],
            "dimgrey": ["#696969", "0x696969"],
            "dodgerblue": ["#1e90ff", "0x1e90ff"],
            "firebrick": ["#b22222", "0xb22222"],
            "floralwhite": ["#fffaf0", "0xfffaf0"],
            "forestgreen": ["#228b22", "0x228b22"],
            "fuchsia": ["#ff00ff", "0xff00ff"],
            "gainsboro": ["#dcdcdc", "0xdcdcdc"],
            "ghostwhite": ["#f8f8ff", "0xf8f8ff"],
            "gold": ["#ffd700", "0xffd700"],
            "goldenrod": ["#daa520", "0xdaa520"],
            "gray": ["#808080", "0x808080"],
            "grey": ["#808080", "0x808080"],
            "green": ["#008000", "0x008000"],
            "greenyellow": ["#adff2f", "0xadff2f"],
            "honeydew": ["#f0fff0", "0xf0fff0"],
            "hotpink": ["#ff69b4", "0xff69b4"],
            "indianred": ["#cd5c5c", "0xcd5c5c"],
            "indigo": ["#4b0082", "0x4b0082"],
            "ivory": ["#fffff0", "0xfffff0"],
            "khaki": ["#f0e68c", "0xf0e68c"],
            "lavender": ["#e6e6fa", "0xe6e6fa"],
            "lavenderblush": ["#fff0f5", "0xfff0f5"],
            "lawngreen": ["#7cfc00", "0x7cfc00"],
            "lemonchiffon": ["#fffacd", "0xfffacd"],
            "lightblue": ["#add8e6", "0xadd8e6"],
            "lightcoral": ["#f08080", "0xf08080"],
            "lightcyan": ["#e0ffff", "0xe0ffff"],
            "lightgoldenrodyellow": ["#fafad2", "0xfafad2"],
            "lightgray": ["#d3d3d3", "0xd3d3d3"],
            "lightgrey": ["#d3d3d3", "0xd3d3d3"],
            "lightgreen": ["#90ee90", "0x90ee90"],
            "lightpink": ["#ffb6c1", "0xffb6c1"],
            "lightsalmon": ["#ffa07a", "0xffa07a"],
            "lightseagreen": ["#20b2aa", "0x20b2aa"],
            "lightskyblue": ["#87cefa", "0x87cefa"],
            "lightslategray": ["#778899", "0x778899"],
            "lightslategrey": ["#778899", "0x778899"],
            "lightsteelblue": ["#b0c4de", "0xb0c4de"],
            "lightyellow": ["#ffffe0", "0xffffe0"],
            "lime": ["#00ff00", "0x00ff00"],
            "limegreen": ["#32cd32", "0x32cd32"],
            "linen": ["#faf0e6", "0xfaf0e6"],
            "magenta": ["#ff00ff", "0xff00ff"],
            "maroon": ["#800000", "0x800000"],
            "mediumaquamarine": ["#66cdaa", "0x66cdaa"],
            "mediumblue": ["#0000cd", "0x0000cd"],
            "mediumorchid": ["#ba55d3", "0xba55d3"],
            "mediumpurple": ["#9370db", "0x9370db"],
            "mediumseagreen": ["#3cb371", "0x3cb371"],
            "mediumslateblue": ["#7b68ee", "0x7b68ee"],
            "mediumspringgreen": ["#00fa9a", "0x00fa9a"],
            "mediumturquoise": ["#48d1cc", "0x48d1cc"],
            "mediumvioletred": ["#c71585", "0xc71585"],
            "midnightblue": ["#191970", "0x191970"],
            "mintcream": ["#f5fffa", "0xf5fffa"],
            "mistyrose": ["#ffe4e1", "0xffe4e1"],
            "moccasin": ["#ffe4b5", "0xffe4b5"],
            "navajowhite": ["#ffdead", "0xffdead"],
            "navy": ["#000080", "0x000080"],
            "oldlace": ["#fdf5e6", "0xfdf5e6"],
            "olive": ["#808000", "0x808000"],
            "olivedrab": ["#6b8e23", "0x6b8e23"],
            "orange": ["#ffa500", "0xffa500"],
            "orangered": ["#ff4500", "0xff4500"],
            "orchid": ["#da70d6", "0xda70d6"],
            "palegoldenrod": ["#eee8aa", "0xeee8aa"],
            "palegreen": ["#98fb98", "0x98fb98"],
            "paleturquoise": ["#afeeee", "0xafeeee"],
            "palevioletred": ["#db7093", "0xdb7093"],
            "papayawhip": ["#ffefd5", "0xffefd5"],
            "peachpuff": ["#ffdab9", "0xffdab9"],
            "peru": ["#cd853f", "0xcd853f"],
            "pink": ["#ffc0cb", "0xffc0cb"],
            "plum": ["#dda0dd", "0xdda0dd"],
            "powderblue": ["#b0e0e6", "0xb0e0e6"],
            "purple": ["#800080", "0x800080"],
            "red": ["#ff0000", "0xff0000"],
            "rosybrown": ["#bc8f8f", "0xbc8f8f"],
            "royalblue": ["#4169e1", "0x4169e1"],
            "saddlebrown": ["#8b4513", "0x8b4513"],
            "salmon": ["#fa8072", "0xfa8072"],
            "sandybrown": ["#f4a460", "0xf4a460"],
            "seagreen": ["#2e8b57", "0x2e8b57"],
            "seashell": ["#fff5ee", "0xfff5ee"],
            "sienna": ["#a0522d", "0xa0522d"],
            "silver": ["#c0c0c0", "0xc0c0c0"],
            "skyblue": ["#87ceeb", "0x87ceeb"],
            "slateblue": ["#6a5acd", "0x6a5acd"],
            "slategray": ["#708090", "0x708090"],
            "slategrey": ["#708090", "0x708090"],
            "snow": ["#fffafa", "0xfffafa"],
            "springgreen": ["#00ff7f", "0x00ff7f"],
            "steelblue": ["#4682b4", "0x4682b4"],
            "tan": ["#d2b48c", "0xd2b48c"],
            "teal": ["#008080", "0x008080"],
            "thistle": ["#d8bfd8", "0xd8bfd8"],
            "tomato": ["#ff6347", "0xff6347"],
            "turquoise": ["#40e0d0", "0x40e0d0"],
            "violet": ["#ee82ee", "0xee82ee"],
            "wheat": ["#f5deb3", "0xf5deb3"],
            "white": ["#ffffff", "0xffffff"],
            "whitesmoke": ["#f5f5f5", "0xf5f5f5"],
            "yellow": ["#ffff00", "0xffff00"],
            "yellowgreen": ["#9acd32", "0x9acd32"],
        }
        if clr == "list":
            return await ctx.send(
                embed=discord.Embed(
                    title="Available Color List",
                    description="```apache\n"
                                + ", ".join(sorted(map(str, colors)))
                                + "\n```",
                    color=self.bot.ok_color,
                )
            )
        if not clr.lower() in colors:
            await ctx.send(
                embed=discord.Embed(
                    description="Color Not Found", color=self.bot.error_color
                )
            )
        else:
            try:
                global a, b
                a = colors[clr.lower()][1]
                b = colors[clr.lower()][0]
            except KeyError:
                if clr.startswith("#"):
                    a = f"0x{clr}".replace("#", "")
            finally:
                img = Image.new("RGB", (128, 128))
                aimage = ImageDraw.Draw(img)
                aimage.rectangle(xy=(0, 0, 128, 128), fill=b)
                buf = io.BytesIO()
                img.save(buf, "png")
                buf.seek(0)
                file = discord.File(buf, "color.png")
                await ctx.send(
                    file=file,
                    embed=discord.Embed(
                        description=f"Color: {clr.capitalize()}\n{b}",
                        color=int(a, base=16),
                    ).set_image(url="attachment://color.png"),
                )

    @commands.command(aliases=["sinfo", "ginfo", "guildinfo"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serverinfo(
            self, ctx: KurisuContext, guild: discord.Guild = None
    ):
        """Get information about a certain guild"""
        if guild is None:
            guild = ctx.guild

        weird_stuff = {
            "ANIMATED_ICON": "Animated Icon",
            "BANNER": "Banner Image",
            "COMMERCE": "Commerce",
            "COMMUNITY": "Community",
            "DISCOVERABLE": "Server Discovery",
            "FEATURABLE": "Featurable",
            "INVITE_SPLASH": "Splash Invite",
            "MEMBER_LIST_DISABLED": "Member list disabled",
            "MEMBER_VERIFICATION_GATE_ENABLED": "Membership Screening enabled",
            "MORE_EMOJI": "More Emojis",
            "NEWS": "News Channels",
            "PARTNERED": "Partnered",
            "PREVIEW_ENABLED": "Preview enabled",
            "PUBLIC_DISABLED": "Public disabled",
            "VANITY_URL": "Vanity URL",
            "VERIFIED": "Verified",
            "VIP_REGIONS": "VIP Voice Servers",
            "WELCOME_SCREEN_ENABLED": "Welcome Screen enabled",
            "THREADS_ENABLED": "Threads Enabled",
            "THREADS_ENABLED_TESTING": "Threads Testing",
            "PRIVATE_THREADS": "Private Threads",
            "SEVEN_DAY_THREAD_ARCHIVE": "Seven Days Thread Archive",
            "THREE_DAY_THREAD_ARCHIVE": "Three Days Thread Archive",
            "ROLE_ICONS": "Role Icons",
            "RELAYS": "Relays Enabled",
        }
        guild_features = [
            f"✅ {name}\n"
            for weird_stuff, name in weird_stuff.items()
            if weird_stuff in guild.features
        ]
        embed = discord.Embed(title=guild.name, color=self.bot.ok_color)
        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(
            name="Owner",
            value=f"Name: **{guild.owner}**\nID: **{guild.owner.id}**",
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
            value="**{}**".format(len(guild.roles)),
            inline=True,
        )
        embed.add_field(
            name="Channel Count",
            value=f"Text: **{len(guild.text_channels)}**\n"
                  f"Voice: **{len(guild.voice_channels)}**\n"
                  f"Categories: **{len(guild.categories)}**\n"
                  f"Total **{len(guild.text_channels) + len(guild.voice_channels) + len(guild.categories)}**",
            inline=True,
        )
        embed.add_field(
            name="Emoji Count",
            value="**{}**".format(len(guild.emojis)),
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
    async def userinfo(
            self, ctx: KurisuContext, user: discord.Member = None
    ):
        """Returns info about a user"""
        if user is None:
            user = ctx.author

        user_flags = "\n".join(
            i.replace("_", " ").title() for i, v in user.public_flags if v
        )
        roles = user.roles[-1:0:-1]
        embed = discord.Embed(color=user.color or self.bot.ok_color)
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
                name="Permissions",
                value=f"Click [Here](https://cogs.fixator10.ru/permissions-calculator/?v={role.permissions.value})",
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

    @commands.command(aliases=["se", "bigmoji", "jumbo"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bigemoji(
            self,
            ctx: KurisuContext,
            emoji: Union[discord.Emoji, discord.PartialEmoji, str],
    ):
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
                cdn_fmt = (
                    "https://twemoji.maxcdn.com/2/72x72/{codepoint:x}.png"
                )
                url = cdn_fmt.format(codepoint=ord(str(emoji)))
                filename = "emoji.png"
            except TypeError:
                return await ctx.send(
                    "That doesn't appear to be a valid emoji"
                )
        try:
            async with self.bot.session.get(url) as resp:
                image = BytesIO(await resp.read())
        except Exception:
            return await ctx.send("That doesn't appear to be a valid emoji")
        await ctx.send(file=discord.File(image, filename=filename))

    @commands.command(aliases=["av"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def avatar(
            self, ctx: KurisuContext, user: Optional[discord.Member]
    ):
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
        if not ctx.channel.is_nsfw():
            await ctx.channel.edit(nsfw=True)
            await ctx.send(
                f"`{ctx.channel.name}` NSFW flag has been toggled to True"
            )
        else:
            await ctx.channel.edit(nsfw=False)
            await ctx.send(
                f"`{ctx.channel.name}` NSFW flag has been toggled to False"
            )

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def setafktimeout(self, ctx: KurisuContext, timeout: str):
        """Set the afk timeout for this server. Run [p]setafktimeout timelist for a list for all available times"""
        timeouts = {
            "1m": ["60", "1 Minute"],
            "5m": ["300", "5 Minutes"],
            "15m": ["900", "15 Minutes"],
            "30m": ["1800", "30 Minutes"],
            "1h": ["3600", "1 Hour"],
        }
        if timeout == "timelist":
            return await ctx.send(
                embed=discord.Embed(
                    title="Available timeouts",
                    description="```\n" + "\n".join(timeouts.keys()) + "\n```",
                    color=self.bot.ok_color,
                )
            )
        if timeout.lower() in timeouts.keys():
            await ctx.guild.edit(afk_timeout=int(timeouts[timeout.lower()][0]))
            await ctx.send(
                embed=discord.Embed(
                    description=f"Set AFK timeout to `{timeouts[timeout.lower()][1]}`",
                    color=self.bot.ok_color,
                )
            )

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def setafkchannel(
            self, ctx: KurisuContext, channel: discord.VoiceChannel = None
    ):
        """Set the channel to where people go when they hit the AFK timeout. Pass in None for no Inactive Channel"""
        if channel is None:
            await ctx.guild.edit(afk_channel=channel)
            return await ctx.send(
                embed=discord.Embed(
                    description="Removed AFK channel", color=self.bot.ok_color
                )
            )

        if channel:
            await ctx.guild.edit(afk_channel=channel)
            await ctx.send(
                embed=discord.Embed(
                    description=f"Set AFK timeout channel to `{channel.name}`",
                    color=self.bot.ok_color,
                )
            )

    @commands.command(aliases=["cr"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def createrole(self, ctx: KurisuContext, *, name: str):
        """Create a role"""
        await ctx.guild.create_role(name=name)
        await ctx.send(
            embed=discord.Embed(
                description=f"Successfully created role with name `{name}`",
                color=self.bot.ok_color,
            )
        )

    @commands.command(aliases=["dr"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def deleterole(self, ctx: KurisuContext, *, role: discord.Role):
        """Delete a role"""
        await role.delete()
        await ctx.send(
            embed=discord.Embed(
                description=f"Successfully deleted role called `{role}`",
                color=self.bot.ok_color,
            )
        )


def setup(bot):
    bot.add_cog(Utility(bot))
