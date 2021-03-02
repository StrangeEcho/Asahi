import discord
import aiohttp  # requests are gey. dey blocking
import nekos
import random

from utils import lists

from typing import Optional

from discord.ext import commands

npa = " "  # default value for the args param if not passed in by a user


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()  # copy and pasting time bois
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def pat(self, ctx, *, args=npa):
        """Pats a user!"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/pat") as r:

                pat = (await r.json())["url"]

                embed = discord.Embed(
                    description=f"{ctx.author.mention} pats {args}", color=0xFFB6C1
                )
                embed.set_image(url=pat)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def kiss(self, ctx, *, args=npa):
        """Kiss a user!"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/kiss") as r:

                kiss = (await r.json())["url"]

                embed = discord.Embed(
                    description=f"{ctx.author.mention} kisses {args}", color=0xFFB6C1
                )
                embed.set_footer(text="owo")
                embed.set_image(url=kiss)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def hug(self, ctx, *, args=npa):
        """Hug someone!"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/hug") as r:

                hug = (await r.json())["url"]

                embed = discord.Embed(
                    description=f"{ctx.author.mention} hugs {args}", color=0xFFB6C1
                )
                embed.set_image(url=hug)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def cuddle(self, ctx, *, args=npa):
        """Cuddle with someone!"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/cuddle") as r:

                cuddle = (await r.json())["url"]

                embed = discord.Embed(
                    description=f"{ctx.author.mention} cuddles {args}", color=0xFFB6C1
                )
                embed.set_image(url=cuddle)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def lick(self, ctx, *, args=npa):
        """Lick someone."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/lick") as r:

                lick = (await r.json())["url"]

                embed = discord.Embed(
                    description=f"{ctx.author.mention} licks {args}", color=0xFFB6C1
                )
                embed.set_image(url=lick)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def bully(self, ctx, *, args=npa):
        """Bully someone :imp:"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/bully") as r:

                bully = (await r.json())["url"]

                embed = discord.Embed(
                    description=f"{ctx.author.mention} bullies {args}", color=0xFFB6C1
                )
                embed.set_image(url=bully)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def poke(self, ctx, *, args=npa):
        """Boop Boop."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/poke") as r:

                poke = (await r.json())["url"]

                embed = discord.Embed(
                    description=f"{ctx.author.mention} pokes {args}", color=0xFFB6C1
                )
                embed.set_image(url=poke)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def baka(self, ctx, *, args=npa):
        """Call someone BAKA"""

        baka = nekos.img("baka")

        embed = discord.Embed(color=0xFFB6C1)
        embed.description = f"{ctx.author.mention} calls {args} a baka"
        embed.set_image(url=baka)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def slap(self, ctx, *, args=npa):
        """Slap someone."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/slap") as r:

                slap = (await r.json())["url"]

                embed = discord.Embed(
                    description=f"{ctx.author.mention} slaps {args}", color=0xFFB6C1
                )
                embed.set_image(url=slap)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def tickle(self, ctx, *, args=npa):
        """Tickles Tickles Tickles."""

        tickle = nekos.img("tickle")

        embed = discord.Embed(color=0xFFB6C1)
        embed.description = f"{ctx.author.mention} tickles {args}"
        embed.set_image(url=tickle)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def smug(self, ctx):
        """Be smug ig.."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://waifu.pics/api/sfw/smug") as r:

                smug = (await r.json())["url"]

                embed = discord.Embed(
                    description=f"{ctx.author.mention} has a smug look", color=0xFFB6C1
                )
                embed.set_image(url=smug)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def feed(self, ctx, *, args=npa):
        """Feed thyself."""

        feed = nekos.img("feed")

        embed = discord.Embed(color=0xFFB6C1)
        embed.description = f"{ctx.author.mention} feeds {args}"
        embed.set_image(url=feed)
        embed.set_footer(text="Eat Up!")
        await ctx.send(embed=embed)

    @commands.command(name="8ball")
    async def _8ball(self, ctx, *, question):
        embed = discord.Embed(
            title="🎱The Magic 8ball🎱",
            description=f"Question: {question}\nAnswer: {random.choice(lists.eightball)}",
            color=ctx.author.top_role.color,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def compliment(self, ctx, member: Optional[discord.Member]):
        if member is None:
            embed = discord.Embed(
                description=f"{ctx.author.mention} {random.choice(lists.compliments)}",
                color=ctx.author.top_role.color,
            )
        else:
            embed = discord.Embed(
                description=f"{member.mention} {random.choice(lists.compliments)}",
                color=member.top_role.color,
            )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
