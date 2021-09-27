import random
from random import choice
import datetime

from discord.ext import commands, menus
from hentai import Format, Hentai, Tag, Utils
import discord

from utils.helpers import EmbedListMenu
from utils.kurisu import KurisuBot


class Embed(discord.Embed):
    def __init__(self, bot: KurisuBot, timestamp=None, **kwargs):
        super(Embed, self).__init__(
            colour=str(bot.get_config("configoptions", "options", "ok_color")).replace("#", "0x"),
            timestamp=timestamp or datetime.datetime.utcnow(),
            **kwargs,
        )

    @classmethod
    def default(cls, ctx, **kwargs):
        instance = cls(**kwargs)
        instance.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        return instance


class NSFW(commands.Cog):
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    @commands.command()
    @commands.is_nsfw()
    @commands.cooldown(1, 2.5, commands.BucketType.user)
    async def hentai(self, ctx: commands.Context, tag=None):
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
            async with self.bot.session.get(f"https://api.waifu.im/nsfw/{tag}") as resp:
                await ctx.send(
                    embed=discord.Embed(
                        color=int(
                            str((await resp.json())["dominant_color"]).replace("#", "0x"), base=16
                        )
                        or self.bot.ok_color
                    ).set_image(url=(await resp.json())["url"])
                )
        else:
            return await ctx.send("Tag Not Found.")

    @commands.command(aliases=["hb"])
    @commands.is_nsfw()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hentaibomb(self, ctx: commands.Context, *, tag: str = None):
        """Post 5 hentai images from Waifu.pics API. Run [p]hentaibomb list for available tags"""
        available_tags = ["waifu", "neko", "trap", "blowjob"]

        if tag is None:
            tag = choice(available_tags)

        if tag is not None and tag.lower() == "list":
            tags = "\n".join(available_tags)
            return await ctx.send(
                embed=discord.Embed(
                    title="Available Tags", description=tags, color=self.bot.ok_color
                )
            )

        if tag is not None and tag.lower() in available_tags:
            async with self.bot.session.post(
                url=f"https://api.waifu.pics/many/nsfw/{tag}",
                headers={"Accept": "application/json", "content-type": "application/json"},
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

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hentainuke(self, ctx: commands.Context, *, tag: str = None):
        """Post 30 hentai images from Waifu.pics API. Run [p]hentainuke list for available tags"""
        available_tags = ["waifu", "neko", "trap", "blowjob"]

        if tag is None:
            tag = choice(available_tags)

        if tag is not None and tag.lower() == "list":
            tags = "\n".join(available_tags)
            return await ctx.send(
                embed=discord.Embed(
                    title="Available Tags", description=tags, color=self.bot.ok_color
                )
            )

        if tag is not None and tag.lower() in available_tags:
            async with self.bot.session.post(
                url=f"https://api.waifu.pics/many/nsfw/{tag}",
                headers={"Accept": "application/json", "content-type": "application/json"},
                json={"files": ""},
            ) as resp:
                step = 5  # the amount of files to display at a time
                idx = 5  # set the index to start with
                files = (await resp.json())["files"]
                while idx < len(files):
                    sublist = files[idx - step : idx]  # [0:5], [5:10], etc
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
    async def nhentai(self, ctx: commands.Context):
        """Some nhentai related commands."""

    @nhentai.command()
    async def read(self, ctx: commands.Context, digits):
        """Read doujins."""
        if not digits.isdigit():
            return await ctx.send("Only digits allowed.")
        if not Hentai.exists(digits):
            return await ctx.send("Doesn't exist.")
        doujin = Hentai(digits)
        embed_list = []
        for i in doujin.image_urls:
            embed = Embed.default(ctx)
            embed.title = doujin.title(Format.Pretty)
            embed.set_image(url=i)
            embed_list.append(embed)
        await menus.MenuPages(
            source=EmbedListMenu(embed_list),
            clear_reactions_after=True,
        ).start(ctx=ctx, wait=False)

    @nhentai.command(aliases=["random"])
    async def rnd(self, ctx: commands.Context):
        """Random one"""
        doujin = Hentai(Utils.get_random_id())
        embed_list = []
        for i in doujin.image_urls:
            embed = Embed.default(ctx)
            embed.title = doujin.title(Format.Pretty)
            embed.set_image(url=i)
            embed_list.append(embed)
        await menus.MenuPages(
            source=EmbedListMenu(embed_list),
            clear_reactions_after=True,
        ).start(ctx=ctx, wait=False)

    @nhentai.command(aliases=["info"])
    async def lookup(self, ctx: commands.Context, doujin):
        """Info about a doujin."""
        if not doujin.isdigit():
            return await ctx.send("Only digits allowed.")
        if not Hentai.exists(doujin):
            return await ctx.send("Doesn't exist.")
        doujin = Hentai(doujin)
        embed = Embed.default(ctx)
        embed.title = doujin.title(Format.Pretty)
        embed.add_field(name="Holy Digits", value=doujin.id, inline=True)
        embed.add_field(name="Languages", value=Tag.get(doujin.language, "name"), inline=True)
        embed.add_field(name="Uploaded", value=doujin.upload_date, inline=True)
        embed.add_field(name="Number of times liked", value=doujin.num_favorites, inline=True)
        embed.add_field(name="Tags", value=Tag.get(doujin.tag, "name"))
        embed.add_field(name="Number of pages", value=doujin.num_pages)
        embed.set_thumbnail(url=doujin.thumbnail)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(NSFW(bot))
