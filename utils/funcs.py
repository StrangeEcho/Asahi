from datetime import timedelta

import discord
from discord.ext import commands

async def check_hierachy(ctx: commands.Context, member: discord.Member):
    try:
        if ctx.author.id == ctx.guild.owner.id:
            return False
        elif member == ctx.author:
            return await ctx.send(f"You cant {ctx.command.name} yourself.")
        elif member.id == ctx.bot.user.id:
            return await ctx.send(
                f"You'd really {ctx.command.name} me? :animehmph:"
            )
        elif member.id == ctx.guild.owner.id:
            return await ctx.send(
                "Even if I wanted to do this. It's literally impossible"
            )
        elif ctx.author.top_role <= member.top_role:
            return await ctx.send(
                f"You cant use {ctx.command.name} on someone whos equal or higher than you in the role hierarchy"
            )
    except Exception as e:
        pass

#Credit for this goes to crazygmr101/https://github.com/aoi-bot/Aoi
def time_notation(td: timedelta, sep="", full=False):
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    return sep.join(
        [
            f"{td.days}{'days' if full else 'd '}",
            f"{hours}{'hours' if full else 'h '}",
            f"{minutes}{'minutes' if full else 'm '}",
        ]
    )