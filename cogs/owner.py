from typing import Optional

import discord
from discord.ext import commands
from dpy_button_utils import ButtonConfirmation

class BotOwner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["shutdown", "logout", "sleep"])
    @commands.is_owner()
    async def die(self, ctx: commands.Context):
        """Log out the bot"""
        if await ButtonConfirmation(
            ctx,
            "Are you sure you want me to logout?",
            destructive=True,
            confirm="Yes",
            cancel="No"
        ):
            await ctx.send("Goodbye then :wave:")
            await self.bot.logout()
        else:
            await ctx.send("I guess I will stay then.")
    
    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, extension):
        """Load bot extensions"""
        try:
            await self.bot.load_extension(extension)
            await ctx.send(f"Loaded cogs {extension}")
        except commands.ExtensionError as e:
            await ctx.send(e)
    
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, extension):
        """Unload bot extensions"""
        try:
            await self.bot.unload_extension(extension)
            await ctx.send(f"Unlaoded cogs {extension}")
        except commands.ExtensionError as e:
            await ctx.send(e)
    
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, extension):
        """Reload bot extensions"""
        try:
            await self.bot.reload_extension(extension)
            await ctx.send(f"Reloaded cogs {extension}")
        except commands.ExtensionError as e:
            await ctx.send(e)

    @commands.command()  # ill probably make this command public soon? say/embed once I filter out the default role mentions
    @commands.is_owner()
    async def say(self, ctx, chan: Optional[discord.TextChannel] = None, *, msg):
        """Say something with the bot."""
        await ctx.message.delete()
        if chan is None:
            await ctx.send(msg)
        else:
            await chan.send(msg)


def setup(bot: commands.Bot):
    bot.add_cog(BotOwner(bot))
