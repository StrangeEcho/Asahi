import discord
from discord.ext import commands

from core import Asahi, AsahiContext

throwawaytarget = ""

class Roleplay(
    commands.Cog, command_attrs={"cooldown": commands.CooldownMapping.from_cooldown(1, 4.5, commands.BucketType.user)}
):
    """Roleplay related commands to use with your friends"""

    def __init__(self, bot: Asahi):
        self.bot = bot

    @commands.command()
    async def hug(self, ctx: AsahiContext, *, target=throwawaytarget):
        """Hug someone"""
        async with self.bot.session.get(
                url="https://api.waifu.pics/sfw/hug"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} hugs {target}",
                    color=ctx.author.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )

    @commands.command()
    async def kiss(self, ctx: AsahiContext, *, target=throwawaytarget):
        """Kiss someone"""
        async with self.bot.session.get(
                url="https://api.waifu.pics/sfw/hug"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} kisses {target}",
                    color=ctx.author.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )

    @commands.command()
    async def pat(self, ctx: AsahiContext, *, target=throwawaytarget):
        """Pat someone"""
        async with self.bot.session.get(
                url="https://api.waifu.pics/sfw/pat"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} pats {target}",
                    color=ctx.author.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )

    @commands.command()
    async def cuddle(self, ctx: AsahiContext, *, target=throwawaytarget):
        """Cuddle with someone"""
        async with self.bot.session.get(
                url="https://api.waifu.pics/sfw/cuddle"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} cuddles {target}",
                    color=ctx.author.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )

    @commands.command()
    async def lick(self, ctx: AsahiContext, *, target=throwawaytarget):
        """Lick someone"""
        async with self.bot.session.get(
                "https://api.waifu.pics/sfw/lick"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} licks {target}",
                    color=ctx.author.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )

    @commands.command(aliases=["bulli"])
    async def bully(self, ctx: AsahiContext, *, target=throwawaytarget):
        """Bully someone"""
        async with self.bot.session.get(
                url="https://api.waifu.pics/sfw/bully"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} bullies {target}",
                    color=ctx.author.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )

    @commands.command()
    async def poke(self, ctx: AsahiContext, *, target=throwawaytarget):
        """Poke someone"""
        async with self.bot.session.get(
                url="https://api.waifu.pics/sfw/poke"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} pokes {target}",
                    color=ctx.author.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )

    @commands.command()
    async def slap(self, ctx: AsahiContext, *, target=throwawaytarget):
        """Slap someone"""
        async with self.bot.session.get(
                url="https://api.waifu.pics/sfw/slap"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} slaps {target}",
                    color=ctx.author.color or self.bot.ok_color,
                )
                    .set_image(url=(await resp.json())["url"])
                    .set_footer(text="ouch")
            )

    @commands.command()
    async def smug(self, ctx: AsahiContext):
        """Smugly look at someone"""
        async with self.bot.session.get(
                url="https://api.waifu.pics/sfw/smug"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} has a smug look on their face.",
                    color=ctx.author.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )

    @commands.command()
    async def baka(self, ctx: AsahiContext, *, target=throwawaytarget):
        """Call someone an idiot"""
        async with self.bot.session.get(
                url="https://nekos.life/api/v2/img/baka"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{target} YOU BAKA!",
                    color=ctx.author.color or self.bot.ok_color,
                )
                    .set_image(url=(await resp.json())["url"])
                    .set_footer(text=f"{ctx.author.name} says so themselves")
            )

    @commands.command()
    async def feed(self, ctx: AsahiContext, *, target=throwawaytarget):
        """Feed someone"""
        async with self.bot.session.get(
                url="https://nekos.life/api/v2/img/feed"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} feeds {target}",
                    color=ctx.author.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )

    @commands.command()
    async def tickle(self, ctx: AsahiContext, *, target=throwawaytarget):
        """Tickle someone"""
        async with self.bot.session.get(
                "https://nekos.life/api/v2/img/tickle"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} tickles {target}",
                    color=ctx.author.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )


async def setup(bot):
    await bot.add_cog(Roleplay(bot))