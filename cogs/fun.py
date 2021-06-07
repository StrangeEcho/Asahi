from random import choice

import discord
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="8ball")
    async def _8ball(self, ctx: commands.Context, *, question):
        answers = [
            "As I see it, yes.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "It is certain.",
            "It is decidedly so.",
            "Most likely.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Outlook good.",
            "Reply hazy, try again.",
            "Signs point to yes.",
            "Very doubtful.",
            "Without a doubt.",
            "Yes.",
            "No",
            "Yes – definitely.",
            "You may rely on it.",
        ]
        await ctx.send(
            embed=discord.Embed(
                title="🎱The Magic 8ball🎱",
                description=f"Question: `{question}`\nAnswer: `{choice(answers)}`",
                color=self.bot.ok_color,
            ).set_footer(text=f"Question asked by {ctx.author}")
        )


def setup(bot):
    bot.add_cog(Fun(bot))
