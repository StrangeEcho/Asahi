import discord
import platform
import sys
import json
import aiohttp
import random
import config

from utils import lists
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["sinfo"])
    @commands.guild_only()
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def serverinfo(self, ctx):
        embed = discord.Embed(title=ctx.guild.name, color=0xFFB6C1)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(
            name="Server Owner",
            value=f"{ctx.guild.owner}\nID: {ctx.guild.owner.id}",
            inline=True,
        )
        embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
        embed.add_field(name="Member Count", value=ctx.guild.member_count, inline=True)
        embed.add_field(name="Role Count", value=len(ctx.guild.roles), inline=True)
        embed.add_field(
            name="Total Voice/Text Channels", value=len(ctx.guild.channels), inline=True
        )
        embed.add_field(name="Creation Time", value=ctx.guild.created_at, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def fetch(self, ctx, id: int):
        user = await self.bot.fetch_user(id)
        flags = [f.name for f in user.public_flags.all()]
        embed = discord.Embed(
            description=(
                f"""
            Username: {user}
            ID: {user.id}
            Account Creation: {user.created_at}
            Public Flags: 
            {flags}
            """
            ),
            color=0xFFB6C1,
        )
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def ping(self, ctx):
        """The obligatory ping command"""
        embed = discord.Embed(color=0xFFB6C1)
        embed.add_field(
            name="Pong!",
            value=f":ping_pong:{round(self.bot.latency * 1000)}ms",
            inline=True,
        )
        embed.set_footer(text=f"Pong request by {ctx.message.author}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx, *args):
        """Make a simple poll."""
        poll_title = " ".join(args)
        embed = discord.Embed(
            title="A new poll has been created!",
            description=f"{poll_title}",
            color=0xFFB6C1,
        )
        embed.set_footer(text=f"Poll created by: {ctx.message.author} • React to vote!")
        embed_message = await ctx.send(embed=embed)
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("👎")
        await embed_message.add_reaction("🤷")

    @commands.command()
    @commands.guild_only()
    async def bitcoin(self, ctx):
        """Get information about bitcoin."""
        url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
        # Async HTTP request
        async with aiohttp.ClientSession() as session:
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            embed = discord.Embed(
                title=":information_source: Info",
                description=f"Bitcoin price is: ${response['bpi']['USD']['rate']}",
                color=0xFFB6C1,
            )
            await ctx.send(embed=embed)

    # looking to rewrite this soon
    @commands.group()
    async def avatar(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                description=f"[URL]({ctx.author.avatar_url})", color=ctx.author.color
            )
            embed.set_image(url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @avatar.command()
    async def user(self, ctx, member: discord.Member):
        embed = discord.Embed(
            description=f"[URL]({member.avatar_url})", color=member.color
        )
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)

    @avatar.command()
    async def server(self, ctx):
        embed = discord.Embed(
            description=f"[URL]({ctx.guild.icon_url})", color=ctx.author.color
        )
        embed.set_image(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
