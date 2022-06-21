import discord
from discord.ext import commands

from core import Asahi, AsahiContext


class NSFW(
    commands.Cog, command_attrs={"cooldown": commands.CooldownMapping.from_cooldown(1, 3.5, commands.BucketType.user)}
):
    """NSFW/Hentai related commands"""

    def __init__(self, bot: Asahi):
        self.bot = bot

    @commands.command()
    @commands.is_nsfw()
    async def ass(self, ctx: AsahiContext):
        """Pictures of anime butt/ass"""
        async with self.bot.session.get("https://api.waifu.im/random/?selected_tags=ass") as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
            )

    @commands.command()
    @commands.is_nsfw()
    async def hentai(self, ctx: AsahiContext):
        """If you know, you know."""
        async with self.bot.session.get("https://api.waifu.im/random/?selected_tags=hentai") as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
            )

    @commands.command()
    @commands.is_nsfw()
    async def milf(self, ctx: AsahiContext):
        """A real man's pleasure in life"""
        async with self.bot.session.get("https://api.waifu.im/random/?selected_tags=milf") as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
            )

    @commands.command()
    @commands.is_nsfw()
    async def oral(self, ctx: AsahiContext):
        """Yessirrrrrrrrrrrrrrrrrrrrrrrrrr"""
        async with self.bot.session.get("https://api.waifu.im/random/?selected_tags=oral") as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
            )

    @commands.command()
    @commands.is_nsfw()
    async def paizuri(self, ctx: AsahiContext):
        """Imagine having boob sex"""
        async with self.bot.session.get("https://api.waifu.im/random/?selected_tags=paizuri") as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
            )

    @commands.command()
    @commands.is_nsfw()
    async def ecchi(self, ctx: AsahiContext):
        """Naked anime women, idk."""
        async with self.bot.session.get("https://api.waifu.im/random/?selected_tags=ecchi") as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(url=(await resp.json())["images"][0]["url"])
            )

async def setup(bot: Asahi):
    await bot.add_cog(NSFW(bot))