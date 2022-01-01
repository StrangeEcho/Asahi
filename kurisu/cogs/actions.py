from discord.ext import commands
from utils.context import KurisuContext
from utils.kurisu import KurisuBot
import discord

np = ""


class Actions(commands.Cog):
    """Roleplay with your friends with this modules assortment of different commands."""

    def __init__(self, bot: KurisuBot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hug(self, ctx: KurisuContext, *, target=np):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kiss(self, ctx: KurisuContext, *, target=np):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pat(self, ctx: KurisuContext, *, target=np):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cuddle(self, ctx: KurisuContext, *, target=np):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lick(self, ctx: KurisuContext, *, target=np):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bully(self, ctx: KurisuContext, *, target=np):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def poke(self, ctx: KurisuContext, *, target=np):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slap(self, ctx: KurisuContext, *, target=np):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def smug(self, ctx: KurisuContext):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def baka(self, ctx: KurisuContext, *, target=np):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def feed(self, ctx: KurisuContext, *, target=np):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tickle(self, ctx: KurisuContext, *, target=np):
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


def setup(bot):
    bot.add_cog(Actions(bot))
