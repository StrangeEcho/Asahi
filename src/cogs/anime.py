import aiohttp
import discord
from discord.ext import commands

from core import Asahi, AsahiContext


class Anime(
    commands.Cog, command_attrs={"cooldown": commands.CooldownMapping.from_cooldown(1, 2.5, commands.BucketType.user)}
):
    def __init__(self, bot: Asahi):
        self.bot = bot

    @commands.command()
    async def maid(self, ctx: AsahiContext):
        async with aiohttp.ClientSession() as sess:
            async with sess.get("https://api.waifu.im/random/?selected_tags=waifu") as resp:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
                )

    @commands.command()
    async def marin(self, ctx: AsahiContext):
        async with aiohttp.ClientSession() as sess:
            async with sess.get("https://api.waifu.im/random/?selected_tags=marin-kitagawa") as resp:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
                )

    @commands.command()
    async def mori(self, ctx: AsahiContext):
        async with aiohttp.ClientSession() as sess:
            async with sess.get("https://api.waifu.im/random/?selected_tags=mori-calliope") as resp:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
                )

    @commands.command()
    async def marin(self, ctx: AsahiContext):
        async with aiohttp.ClientSession() as sess:
            async with sess.get("https://api.waifu.im/random/?selected_tags=marin-kitagawa") as resp:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
                )

    @commands.command()
    async def maid(self, ctx: AsahiContext):
        async with aiohttp.ClientSession() as sess:
            async with sess.get("https://api.waifu.im/random/?selected_tags=maid") as resp:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
                )


async def setup(bot: Asahi):
    await bot.add_cog(Anime(bot))
