import discord

from discord.ext import commands


from datetime import timedelta
from datetime import datetime


# Credit Goes To crazygmr101/aoi-bot
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


bot_start_time = datetime.now()


async def check_hierachy(ctx, member):
    try:
        if ctx.author.id == ctx.guild.owner.id:
            return False
        elif member == ctx.author:
            return await ctx.send(f"You can't {ctx.command.name} yourself lmao")
        elif member.id == ctx.bot.user.id:
            return await ctx.send(
                "You'd really use my own moderation commands on me. hmph"
            )
        elif member == ctx.guild.owner:
            return await ctx.send(f"You can't {ctx.command.name} the owner lmao")
        elif ctx.author.top_role <= member.top_role:
            return await ctx.send(
                "You cant use this command on someone equal or higher than yourself"
            )
    except Exception as e:
        pass
