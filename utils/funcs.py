import discord
from discord.ext import commands


async def check_hierachy(ctx: commands.Context, member: discord.Member):
    try:
        if ctx.author.id == ctx.guild.owner.id:
            return False
        elif member == ctx.author:
            return await ctx.send(f"You cant {ctx.command.name} yourself.")
        elif member.id == ctx.bot.user.id:
            return await ctx.send(f"You'd really {ctx.command.name} me? :animehmph:")
        elif member.id == ctx.guild.owner.id:
            return await ctx.send("Even if I wanted to do this. It's literally impossible")
        elif ctx.author.top_role <= member.top_role:
            return await ctx.send(
                f"You cant use {ctx.command.name} on someone whos equal or higher than you in the role hierarchy"
            )
    except Exception as e:
        pass


def can_execute_action(ctx, user, target):
    return (
            user.id == ctx.bot.owner_id
            or user == ctx.guild.owner
            or user.top_role > target.top_role
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
