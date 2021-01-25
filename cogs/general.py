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

    @commands.command()
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """Get the guild information."""
        server = ctx.message.guild
        roles = [x.name for x in server.roles]
        role_length = len(roles)
        if role_length > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)
        channels = len(server.channels)
        time = str(server.created_at)
        time = time.split(" ")
        time = time[0]

        embed = discord.Embed(
            title="**Server Name:**", description=f"{server}", color=0xFFB6C1
        )
        embed.set_thumbnail(url=server.icon_url)
        embed.add_field(name="Owner", value=f"{server.owner}\n{server.owner.id}")
        embed.add_field(name="Server ID", value=server.id)
        embed.add_field(name="Member Count", value=server.member_count)
        embed.add_field(name="Text/Voice Channels", value=f"{channels}")
        embed.add_field(name=f"Roles ({role_length})", value=roles)
        embed.set_footer(text=f"Created at: {time}")
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
    async def invite(self, ctx):
        """Bot invite link."""
        try:
            await ctx.author.send(f"Invite me by clicking here: https://discordapp.com/oauth2/authorize?&client_id={config.APPLICATION_ID}&scope=bot&permissions=8")
            await ctx.send('You Have Mail :envelope:')
        except discord.Forbidden:
            await ctx.send(f'I Cannot Direct Message You **{ctx.author.display_name}**\n'
                            'Go To Your Discord Settings -> Privacy & Safety -> Allow Direct Messages From Sever Members')
            
    @commands.command()
    @commands.guild_only()
    async def support(self, ctx):
        """Sends an invite to the bot support server."""
        try:
            await ctx.author.send("Join my support server by clicking here: https://discord.gg/GAeb2eXW7a")
            await ctx.send('You Have Mail :envelope:')
        except discord.Forbidden:
            await ctx.send(f'I Cannot Direct Message You **{ctx.author.display_name}**')

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

    @commands.group()
    async def avatar(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description=f'[URL]({ctx.author.avatar_url})', color=ctx.author.color)
            embed.set_image(url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        
    @avatar.command()
    async def user(self, ctx, member : discord.Member):
        embed = discord.Embed(description=f'[URL]({member.avatar_url})', color=member.color)
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)
    
    @avatar.command()
    async def server(self, ctx):
        embed = discord.Embed(
            description=f'[URL]({ctx.guild.icon_url})',
            color=ctx.author.color
        )
        embed.set_image(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(General(bot))
