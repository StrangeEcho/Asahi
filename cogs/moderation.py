import os #needs rewriting/ugly coding
import discord

from discord.ext import commands


class moderation(commands.Cog, name="moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief = 'Kicks a member', aliases = ['k', 'boot'])
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        await member.kick(reason=reason)
        embed = discord.Embed(
            description=f"Sucessfully Kicked {member.mention} for {reason} from {ctx.guild}",
            color=0x000000
        )
        await ctx.send(embed=embed)
        await member.send(f'You were kicked from {context.guild} for {reason}.')

    @commands.command(brief = 'Nickname a member', aliaes = ['nickname'])
    @comamnds.has_permissions(manage_nicknames = True)
    async def nick(self, ctx, member : discord.Member, name : str):
        embed = discord.Embed(
            description=f"Changed {member.mention}'s Nickname to {name}",
            color=0x000000
        )
        await ctx.send(embed=embed)
        await member.change_nickname(name)

    @commands.command(brief = 'Ban People', aliases = ['b'])
    @commands.has_permissions(ban_member = True)
    async def ban(self, ctx, member : discord.Member, *, reason=reason):
        embed = discord.Member(
            description=f"Banned {member.mention} for {reason} from {ctx.guild} ",
            color=0x000000
        )
        await ctx.send(embed=embed)
        await member.send(f'You were banned from {ctx.guild} for {reason}')

    @commands.command()
    @commands.has_permissions(kick_member = True)
    async def warn(self, ctx, member : discord.Member, *, reason=None):
        embed = discord.Embed(
            description=f"{member.mention} has been warned by {ctx.author.mention}",
            color=0x000000
        )
        embed.add_field(
            name="Reason:",
            value=f"{reason}",
            inline=True
        )
        await ctx.send(embed=embed)

    @commands.command(brief = 'clears messages', alises = ['prune', 'clear'])
    async def purge(self, ctx, *, amount = None):
        embed = discord.Embed(
            description=f"Cleared {amount} of messages",
            color=0x000000
        )    
        await ctx.channel.purge(limit=amount)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(moderation(bot))