import discord

import config

from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["issue"])
    async def bug(self, ctx):
        """Bug report command."""
        await ctx.send(
            "See a bug or issue with the bot? Please report it at https://github.com/Yat-o/HimejiBot/issues"
        )

    @commands.command()
    async def support(self, ctx):
        """Sends an invite to the bot support server."""
        try:
            await ctx.author.send(
                "Join my support server by clicking here: https://discord.gg/GAeb2eXW7a"
            )
            await ctx.send("You Have Mail :envelope:")
        except discord.Forbidden:
            await ctx.send(
                f"I Cannot Direct Message You **{ctx.author.display_name}**\n"
                "Go To Your Discord Settings -> Privacy & Safety -> Allow Direct Messages From Sever Members"
            )

    @commands.command()
    @commands.guild_only()
    async def invite(self, ctx):
        """Bot invite link."""
        try:
            await ctx.author.send(
                f"Invite me by clicking here: https://discordapp.com/oauth2/authorize?&client_id={config.APPLICATION_ID}&scope=bot&permissions=8"
            )
            await ctx.send("You Have Mail :envelope:")
        except discord.Forbidden:
            await ctx.send(
                f"I Cannot Direct Message You **{ctx.author.display_name}**\n"
                "Go To Your Discord Settings -> Privacy & Safety -> Allow Direct Messages From Sever Members"
            )


def setup(bot):
    bot.add_cog(Misc(bot))
