import functools
import random

from discord.ext import commands, vbu
from utils.context import KurisuContext
from utils.kurisu import KurisuBot
import discord
import hentai


class Embed(discord.Embed):
    def __init__(self, bot: KurisuBot, timestamp=None, **kwargs):
        super(Embed, self).__init__(
            colour=str(
                bot.get_config("configoptions", "options", "ok_color")
            ).replace("#", "0x"),
            timestamp=timestamp or discord.utils.utcnow(),
            **kwargs,
        )

    @classmethod
    def default(cls, ctx, **kwargs):
        instance = cls(**kwargs)
        instance.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        return instance


class NSFW(commands.Cog):
    """Some kinky yet interesting set of commands meant for those "urges" 😉."""

    def __init__(self, bot: KurisuBot):
        self.bot = bot

    @commands.command()
    @commands.is_nsfw()
    @commands.cooldown(1, 2.5, commands.BucketType.user)
    async def hentai(self, ctx: KurisuContext, tag=None):
        """Hentai command using waifu.im API. Use [p]hentai list for a list of available tags"""
        available_tags = [
            "ass",
            "ecchi",
            "ero",
            "hentai",
            "maid",
            "milf",
            "oppai",
            "oral",
            "paizuri",
            "selfies",
            "uniform",
        ]

        if not tag:
            tag = random.choice(available_tags)

        if tag.lower() == "list":
            return await ctx.send(
                embed=discord.Embed(
                    title="All available tags",
                    description="```\n" + "\n".join(available_tags) + "\n```",
                    color=self.bot.ok_color,
                )
            )

        if tag.lower() in available_tags:
            async with self.bot.session.get(
                    f"https://api.waifu.im/nsfw/{tag}"
            ) as resp:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.ok_color).set_image(
                        url=(await resp.json())["images"][0]["url"]
                    )
                )
        else:
            return await ctx.send("Tag Not Found.")

    @commands.command(hidden=True, aliases=["hb"])
    @commands.is_nsfw()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def hentaibomb(self, ctx: KurisuContext, *, tag: str = None):
        """Post 5 hentai images from Waifu.pics API. Run [p]hentaibomb list for available tags"""
        available_tags = ["waifu", "neko", "trap", "blowjob"]

        if tag is None:
            tag = random.choice(available_tags)

        if tag is not None and tag.lower() == "list":
            tags = "\n".join(available_tags)
            return await ctx.send(
                embed=discord.Embed(
                    title="Available Tags",
                    description=tags,
                    color=self.bot.ok_color,
                )
            )

        if tag is not None and tag.lower() in available_tags:
            async with self.bot.session.post(
                    url=f"https://api.waifu.pics/many/nsfw/{tag}",
                    headers={
                        "Accept": "application/json",
                        "content-type": "application/json",
                    },
                    json={"files": ""},
            ) as resp:
                results = (await resp.json())["files"][:5]
                await ctx.send("\n".join(results))
        else:
            await ctx.send(
                embed=discord.Embed(
                    title="TAG NOT FOUND",
                    description=f"{tag} was not found in the available tag list. Please run `{ctx.clean_prefix}hb list`",
                    color=self.bot.error_color,
                )
            )

    @commands.command(hidden=True, aliases=["hn"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def hentainuke(self, ctx: KurisuContext, *, tag: str = None):
        """Post 30 hentai images from Waifu.pics API. Run [p]hentainuke list for available tags"""
        available_tags = ["waifu", "neko", "trap", "blowjob"]

        if tag is None:
            tag = random.choice(available_tags)

        if tag is not None and tag.lower() == "list":
            tags = "\n".join(available_tags)
            return await ctx.send(
                embed=discord.Embed(
                    title="Available Tags",
                    description=tags,
                    color=self.bot.ok_color,
                )
            )

        if tag is not None and tag.lower() in available_tags:
            async with self.bot.session.post(
                    url=f"https://api.waifu.pics/many/nsfw/{tag}",
                    headers={
                        "Accept": "application/json",
                        "content-type": "application/json",
                    },
                    json={"files": ""},
            ) as resp:
                step = 5  # the amount of files to display at a time
                idx = 5  # set the index to start with
                files = (await resp.json())["files"]
                while idx < len(files):
                    sublist = files[idx - step: idx]  # [0:5], [5:10], etc
                    await ctx.send("\n".join(map(str, sublist)))
                    idx += step
        else:
            await ctx.send(
                embed=discord.Embed(
                    title="TAG NOT FOUND",
                    description=f"{tag} was not found in the available tag list. Please run `{ctx.clean_prefix}hb list`",
                    color=self.bot.error_color,
                )
            )

    @commands.group()
    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.is_nsfw()
    async def nhentai(self, ctx: KurisuContext):
        """Some nhentai related commands."""

    @nhentai.command()
    async def read(self, ctx: KurisuContext, digits):
        """Read doujins."""
        try:
            result = await self.bot.loop.run_in_executor(
                None, functools.partial(hentai.Hentai.exists, digits)
            )
        except Exception as e:
            if await self.bot.is_owner(ctx.author):
                return await ctx.send(str(e))
            else:
                return await ctx.send("The command errored, try again later.")
        if not result:
            return await ctx.send("It doesn't exist you horny weeb")
        try:
            doujin = await self.bot.loop.run_in_executor(
                None, functools.partial(hentai.Hentai, digits)
            )
        except Exception as e:
            if await self.bot.is_owner(ctx.author):
                return await ctx.send(str(e))
            else:
                return await ctx.send("The command errored, try again later.")
        embed_list = []
        for i in doujin.image_urls:
            embed = Embed.default(ctx)
            embed.title = doujin.title(hentai.Format.Pretty)
            embed.set_image(url=i)
            embed_list.append(embed)
        await vbu.Paginator(embed_list, per_page=1).start(ctx)

    @nhentai.command(aliases=["random"])
    async def rnd(self, ctx: KurisuContext):
        """Random hentais from nhentai"""

        try:
            doujin = await self.bot.loop.run_in_executor(
                None,
                functools.partial(hentai.Hentai, hentai.Utils.get_random_id()),
            )
        except Exception as e:
            if await self.bot.is_owner(ctx.author):
                return await ctx.send(str(e))
            else:
                return await ctx.send("The command errored, try again later.")
        embed_list = []
        for i in doujin.image_urls:
            embed = Embed.default(ctx)
            embed.title = doujin.title(hentai.Format.Pretty)
            embed.set_image(url=i)
            embed_list.append(embed)
        await vbu.Paginator(embed_list, per_page=1).start(ctx)

    @nhentai.command(aliases=["info"])
    async def lookup(self, ctx: KurisuContext, doujin: int):
        """Info about a doujin."""

        try:
            result = await self.bot.loop.run_in_executor(
                None, functools.partial(hentai.Hentai.exists, doujin)
            )
        except Exception as e:
            if await self.bot.is_owner(ctx.author):
                return await ctx.send(str(e))
            else:
                return await ctx.send("The command errored, try again later.")
        if not result:
            return await ctx.send("It doesn't exist you horny weeb")
        try:
            doujin = await self.bot.loop.run_in_executor(
                None, functools.partial(hentai.Hentai, doujin)
            )
        except Exception as e:
            if await self.bot.is_owner(ctx.author):
                return await ctx.send(str(e))
            else:
                return await ctx.send("The command errored, try again later.")
        embed = Embed.default(ctx)
        embed.title = doujin.title(hentai.Format.Pretty)
        embed.add_field(name="Holy Digits", value=doujin.id, inline=True)
        embed.add_field(
            name="Languages",
            value=hentai.Tag.get(doujin.language, "name"),
            inline=True,
        )
        embed.add_field(name="Uploaded", value=doujin.upload_date, inline=True)
        embed.add_field(
            name="Number of times liked",
            value=doujin.num_favorites,
            inline=True,
        )
        embed.add_field(name="Tags", value=hentai.Tag.get(doujin.tag, "name"))
        embed.add_field(name="Number of pages", value=doujin.num_pages)
        embed.set_thumbnail(url=doujin.thumbnail)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(NSFW(bot))
