import discord

import typing

from utils.misc import check_hierachy

from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, reason=None):
        """Kicks a user"""
        if await check_hierachy(ctx, member):
            return

        try:
            await member.kick(reason=f"{reason} - {ctx.author.name}")
            await ctx.send(f"⚠️{member.name} was kicked for {reason}")
            await member.send(f"⚠️You were kicked from {ctx.guild} for {reason}")
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans a user"""
        if await check_hierachy(ctx, member):
            return

        try:
            await member.ban(reason=f"{reason} - {ctx.author.name}")
            await ctx.send(f"🔴{member.name} was banned for {reason}")
            await member.send(f"🔴You were banned from {ctx.guild} for {reason}")
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, nickname=None):
        """Nicknames a user"""
        if await check.hierachy(ctx, member):
            return

        try:
            if nickname is None:
                await member.edit(nick=member.name)
                await ctx.send(f"{ctx.author.name} your nickname was reset")
            else:
                await member.edit(nick=nickname)
                await ctx.send(f"{member.name}'s nickname was changed to {nickname}")
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, id: int = None):
        if id is None:
            await ctx.send("Please pass in a ID")
        else:
            try:
                user = await self.bot.fetch_user(id)

                await ctx.guild.unban(user)
                await ctx.send(f"🟢Successfully unbanned `{user}`")
            except Exception as e:
                await ctx.send(e)

    @commands.command()
    async def purge(self, ctx, limit=0):
        if limit == 0:
            await ctx.send("Please pass in a valid amount to purge.")
        else:
            await ctx.channel.purge(limit=limit + 1)
            await ctx.send(f"Done. {limit} messages deleted", delete_after=5)


def setup(bot):
    bot.add_cog(Moderation(bot))
