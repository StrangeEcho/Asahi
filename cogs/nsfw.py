from random import choice
import datetime

from discord.ext import commands, menus
from hentai import Format, Hentai, Tag, Utils
import discord

from config import OK_COLOR
from utils.classes import EmbedListMenu, HimejiBot

embed_color = OK_COLOR.replace("#", "0x")


class Embed(discord.Embed):
    def __init__(self, colour=int(embed_color, base=16), timestamp=None, **kwargs):
        super(Embed, self).__init__(
            colour=colour, timestamp=timestamp or datetime.datetime.utcnow(), **kwargs
        )

    @classmethod
    def default(cls, ctx, **kwargs):
        instance = cls(**kwargs)
        instance.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        return instance


class NSFW(commands.Cog):
    def __init__(self, bot: HimejiBot):
        self.bot = bot

    @commands.command()
    @commands.is_nsfw()
    async def hentai(self, ctx: commands.Context):
        """Retrieves a hentai gif/image from nekos.life api endpoint"""
        endpoints = [
            "Random_hentai_gif",
            "pussy",
            "nsfw_neko_gif",
            "lewd",
            "les",
            "kuni",
            "cum",
            "classic",
            "boobs",
            "bj",
            "anal",
            "yuri",
            "trap",
            "tits",
            "solog",
            "solo",
            "pwankg",
            "pussy_jpg",
            "lewdkemo",
            "lewdk",
            "keta",
            "hololewd",
            "holoero",
            "hentai",
            "femdom",
            "feetg",
            "erofeet",
            "feet",
            "ero",
            "erok",
            "erokemo",
            "cum_jpg",
            "gasm",
        ]
        async with self.bot.session.get(
            f"https://nekos.life/api/v2/img/{choice(endpoints)}"
        ) as resp:
            if resp.status == 200:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.ok_color).set_image(
                        url=(await resp.json())["url"]
                    )
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        description=f"API returned a {resp.status} status. Try again...",
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
        """ Info about a doujin."""
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
