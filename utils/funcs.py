from typing import Optional, SupportsInt
import datetime

from discord.ext import commands
from humanize import naturalsize
import discord


async def check_hierarchy(ctx: commands.Context, member: discord.Member):
    if ctx.me.top_role <= member.top_role:
        return await ctx.send(
            f"I can't {ctx.command.name} someone who higher or equal to me on the role hierarchy."
        )
    if ctx.author.id == ctx.guild.owner.id:
        return False
    if member.id == ctx.bot.user.id:
        return await ctx.send(
            "I can't do this either and you'd really use my own moderation commands on me? >:C"
        )
    if member.id == ctx.guild.owner.id:
        return await ctx.send(
            f"Lol did you just try to {ctx.command} the owner? <:HahaLmao:854837134706999337>"
        )
    if ctx.author.top_role <= member.top_role:
        return await ctx.send(
            f"You can't {ctx.command.name} someone who is equal or higher in power to you on the role hierarchy"
        )


async def parse_llnode_stat(stats, stat_name: str):
    stat = getattr(stats, stat_name)
    if isinstance(stat, int) and stat_name.startswith("memory_"):
        stat = naturalsize(stat, binary=True)
    if stat_name == "uptime":
        stat = humanize_timedelta(seconds=stat / 1000)
    if "load" in stat_name:
        stat = f"{round(stat * 100, 2)} %"
    return stat


def humanize_timedelta(
    *,
    timedelta: Optional[datetime.timedelta] = None,
    seconds: Optional[SupportsInt] = None,
) -> None:
    """
    Get a locale aware human timedelta representation.
    """

    try:
        obj = seconds if seconds is not None else timedelta.total_seconds()
    except AttributeError:
        raise ValueError(
            "You must provide either a timedelta or a number of seconds"
        )


# Credits to https://github.com/Cog-Creators/Red-DiscordBot/blob/ded5aff08cfe443498770e7f27035db694e72c30/redbot/core/utils/chat_formatting.py#L86
def box(text: str, lang: str = "") -> str:
    """Get the given text in a code block.
    Parameters
    ----------
    text : str
        The text to be marked up.
    lang : `str`, optional
        The syntax highlighting language for the codeblock.
    Returns
    -------
    str
        The marked up text.
    """
    ret = "```{}\n{}\n```".format(lang, text)
    return ret
