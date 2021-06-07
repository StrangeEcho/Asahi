import platform
import time
from datetime import datetime
from io import BytesIO
from typing import Optional, Union, cast

import aiohttp
import discord
import humanize
from discord.ext import commands

from config import APPLICATION_ID
from utils.funcs import box


class Miscellaneous(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_permissions(embed_links=True)
    @commands.command()
    async def ping(
        self,
        ctx: commands.Context,
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

        emb.title = "Pong! 🏓"
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
                        (message.created_at - ctx.message.created_at).total_seconds()
                        * 1000
                    )
                )
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
        embed = discord.Embed(color=self.bot.ok_color, title="<3")
        embed.description = f"Invite Link: https://discord.com/api/oauth2/authorize?client_id={APPLICATION_ID}&scope=bot"
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
        embed = discord.Embed(
            title=f"{self.bot.user.name} Stats", color=self.bot.ok_color
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name="Author:", value="Tylerr#6979", inline=True)
        embed.add_field(
            name="Python Versions:",
            value=f"Python Version: {platform.python_version()}\nDiscord.py Version: {discord.__version__}",
            inline=True,
        )
        embed.add_field(
            name="Websocket Latency", value=f"{round(self.bot.latency * 1000)}ms"
        )
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
            name="Uptime:",
            value=f"{humanize.time.naturaldelta(datetime.utcnow() - self.bot.uptime)}",
            inline=True,
        )
        embed.add_field(
            name="Creation Date:",
            value=self.bot.user.created_at.strftime("%c"),
            inline=True,
        )
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        embed.add_field(
            name="Github Repository:",
            value="Find it [here](https://github.com/Yat-o/HimejiBot/tree/rewrite)",
            inline=True,
        )
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        embed.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"{self.bot.user.name} was made with love. <3",
        )
        await ctx.send(embed=embed)

    @commands.command(usage="(project name)")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pypi(self, ctx: commands.Context, project: str):
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
                    colour=self.bot.ok_color,
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
                    [f"[{x}]({y})" for x, y in dict(info["project_urls"]).items()]
                ),
            )
            e.add_field(name="License", value=info["license"] or "`Not specified.`")
            await ctx.reply(embed=e, mention_author=False)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.bot_has_permissions(embed_links=True)
    async def avatar(self, ctx: commands.Context, user: Optional[discord.Member]):
        """Check your avatars."""
        await ctx.channel.trigger_typing()
        if user is None:
            user = ctx.author
        ext = "gif" if user.avatar.is_animated() else "png"
        e = discord.Embed(
            title=f"{user.name}'s avatar.", color=user.color, url=user.avatar.url
        )
        e.set_image(url=f"attachment://aaaaaaaaaaaaaaaaaaaaaaaaa.{ext}")
        e.set_footer(text=f"ID: {user.id}")
        await ctx.send(
            embed=e,
            file=discord.File(
                BytesIO(await user.avatar.with_size(4096).read()),
                f"aaaaaaaaaaaaaaaaaaaaaaaaa.{ext}",
            ),
        )

    @commands.command()
    @commands.bot_has_permissions(embed_links=True, attach_files=True)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def osu(self, ctx: commands.Context, *, user):
        """Get osu information about someone."""
        try:
            async with self.bot.session.get(
                "https://api.martinebot.com/v1/imagesgen/osuprofile",
                params={
                    "player_username": user,
                },
                raise_for_status=True,
            ) as r:
                pic = BytesIO(await r.read())
        except aiohttp.ClientResponseError as e:
            emb = discord.Embed(
                description=f"Cannot contact the api due to error: [{e.status}] {e.message}",
                color=self.bot.ok_color,
            )
            return await ctx.send(embed=emb)
        e = discord.Embed(
            title=f"Here's the osu profile for {user}", color=self.bot.ok_color
        )
        if isinstance(pic, BytesIO):
            e.set_image(url="attachment://osu.png")
        elif isinstance(pic, str):
            e.set_footer(text="Api is currently down.")

        await ctx.send(
            embed=e,
            file=discord.File(pic, filename="osu.png") if pic else None,
        )
        if isinstance(pic, BytesIO):
            pic.close()

    @commands.command(aliases=["se", "bigmoji", "jumbo"])
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

    @commands.command()
    async def uptime(self, ctx: commands.Context):
        """Shows bot's uptime."""
        since = self.bot.uptime.strftime("%H:%M:%S UTC | %Y-%m-%d")
        delta = datetime.utcnow() - self.bot.uptime
        uptime_text = humanize.time.precisedelta(delta) or ("Less than one second.")
        embed = discord.Embed(colour=self.bot.ok_color)
        embed.add_field(
            name=f"{self.bot.user.name} has been up for:", value=uptime_text
        )
        embed.set_footer(text=f"Since: {since}")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["sinfo", "ginfo", "guildinfo"])
    async def serverinfo(self, ctx: commands.Context, guild: discord.Guild = None):
        """Get information about a certain guild"""
        if guild is None:
            guild = ctx.guild

        guild_features = (
            str(guild.features)
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .replace(",", "\n")
            or "None"
        )

        try:
            await ctx.send(
                embed=discord.Embed(title=guild.name, color=self.bot.ok_color)
                .set_thumbnail(url=guild.icon.url)
                .add_field(
                    name="Owner", value=f"{guild.owner}\n{guild.owner.id}", inline=True
                )
                .add_field(name="Server ID", value=guild.id, inline=True)
                .add_field(name="Region", value=str(guild.region).upper(), inline=True)
                .add_field(name="Member Count", value=guild.member_count, inline=True)
                .add_field(name="Role Count", value=len(guild.roles), inline=True)
                .add_field(
                    name="Channel Count",
                    value=f"Categories: {len(guild.categories)}\nText: {len(guild.text_channels)}\nVoice: {len(guild.voice_channels)}\nTotal: {len(guild.text_channels) + len(guild.voice_channels)}",
                    inline=True,
                )
                .add_field(name="Emoji Count", value=len(guild.emojis), inline=True)
                .add_field(name="Features", value=guild_features, inline=True)
                .add_field(name="Creation Time", value=guild.created_at.strftime("%c"))
            )
        except discord.Forbidden:
            await ctx.send(
                "Cannot pull up statistics for this server because its not in my cache."
            )


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
