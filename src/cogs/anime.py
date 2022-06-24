from discord.ext import commands
import discord

from core import Asahi, AsahiContext


class Anime(
    commands.Cog, command_attrs={"cooldown": commands.CooldownMapping.from_cooldown(1, 2.5, commands.BucketType.user)}
):
    """Anime related commands"""

    def __init__(self, bot: Asahi):
        self.bot = bot

    @commands.command()
    async def waifu(self, ctx: AsahiContext):
        "Random anime waifu images"
        async with self.bot.session.get("https://api.waifu.im/random/?selected_tags=waifu") as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
            )

    @commands.command()
    async def mori(self, ctx: AsahiContext):
        "Random images of VTuber Mori Calliope"
        async with self.bot.session.get("https://api.waifu.im/random/?selected_tags=mori-calliope") as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
            )

    @commands.command()
    async def marin(self, ctx: AsahiContext):
        """Pictures of Dress Up Darling character Marin Kitagawa"""
        async with self.bot.session.get("https://api.waifu.im/random/?selected_tags=marin-kitagawa") as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
            )

    @commands.command()
    async def maid(self, ctx: AsahiContext):
        """Random pictures of anime maids"""
        async with self.bot.session.get("https://api.waifu.im/random/?selected_tags=maid") as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
            )

    @commands.command()
    async def selfie(self, ctx: AsahiContext):
        """Random anime selfies"""
        async with self.bot.session.get("https://api.waifu.im/random/?selected_tags=selfie") as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
            )


async def setup(bot: Asahi):
    await bot.add_cog(Anime(bot))
