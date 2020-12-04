import os #todo finish adding all commands. should i add owner? probably not
import sys
import discord
import config

from discord.ext import commands


class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, context):
        # Note that commands made only for the owner of the bot are not listed here.
        embed = discord.Embed(
            title="Bot",
            description="List of commands are:",
            color=0xE786D7
        )
        embed.add_field(
            name="Invite",
            value=f"Usage: {config.BOT_PREFIX}invite",
            inline=False
        )
        embed.add_field(
            name="Server",
            value=f"Usage: {config.BOT_PREFIX}server",
            inline=False
        )
        embed.add_field(
            name="Poll",
            value=f"Usage: {config.BOT_PREFIX}poll <Idea>",
            inline=False
        )
        embed.add_field(
            name="8ball",
            value=f"Usage: {config.BOT_PREFIX}8ball <Question>",
            inline=False)
        embed.add_field(
            name="Bitcoin",
            value=f"Usage: {config.BOT_PREFIX}bitcoin",
            inline=False
        )
        embed.add_field(
            name="Info",
            value=f"Usage: {config.BOT_PREFIX}info",
            inline=False
        )
        embed.add_field(
            name="Kick",
            value=f"Usage: {config.BOT_PREFIX}kick <User> <Reason>",
            inline=False
        )
        embed.add_field(
            name="Ban",
            value=f"Usage: {config.BOT_PREFIX}ban <User> <Reason>",
            inline=False
        )
        embed.add_field(
            name="Warn",
            value=f"Usage: {config.BOT_PREFIX}warn <User> <Reason>",
            inline=False
        )
        embed.add_field(
            name="Purge",
            value=f"Usage: {config.BOT_PREFIX}purge <Number>",
            inline=False
        )
        embed.add_field(
            name="Help",
            value=f"Usage: {config.BOT_PREFIX}help",
            inline=False
        )
        await context.send(embed=embed)

def setup(bot): #Todo - Finish idk
    bot.add_cog(Help(bot)) 
