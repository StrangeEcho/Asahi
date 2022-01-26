import io
import os
import traceback

import discord
from discord.ext import commands
from exts.utility import confirm_prompt
from kurisu import Kurisu, KurisuContext


class DevTools(commands.Cog):
    def __init__(self, bot: Kurisu):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def savechat(self, ctx: KurisuContext, limit: int = 15):
        """Save messages from the current text channel"""

        basestr = ""
        async for msg in ctx.channel.history(limit=limit):
            basestr += f"{msg.author}: {msg.content}\n"

        await ctx.send(
            file=discord.File((io.BytesIO(basestr.encode("utf-8"))), f"{ctx.message.created_at.strftime('%c')}.txt")
        )

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def cogmanager(self, ctx: KurisuContext):
        """Cog management commands"""
        await ctx.send_help(ctx.command)

    @cogmanager.command()
    async def load(self, ctx: KurisuContext, *cogs):
        """Load Cogs"""
        succeed = 0
        failed = 0
        error_str = ""
        embed = discord.Embed(description=":ok_hand:", color=self.bot.info_color)

        for ext in cogs:
            try:
                self.bot.load_extension(ext)
                succeed += 1
            except commands.ExtensionError as e:
                failed += 1
                error_str += (
                    f"**Error for {ext}**:\n\n{''.join(traceback.format_exception(None, e, e.__traceback__))}\n"
                )
        if failed > 0:
            embed.set_footer(text=f"Failed to load {failed} cogs. Sending error file...")

        await ctx.send(embed=embed)
        if error_str:
            await ctx.send(file=discord.File(io.BytesIO(error_str.encode("utf-8")), "error.nim"))

    @cogmanager.command()
    async def reload(self, ctx: KurisuContext, *cogs):
        """Reload cogs"""
        succeed = 0
        failed = 0
        error_str = ""
        embed = discord.Embed(description=":ok_hand:", color=self.bot.info_color)

        for ext in cogs:
            try:
                self.bot.reload_extension(ext)
                succeed += 1
            except commands.ExtensionError as e:
                failed += 1
                error_str += (
                    f"**Error for {ext}**:\n\n{''.join(traceback.format_exception(None, e, e.__traceback__))}\n"
                )
        if failed > 0:
            embed.set_footer(text=f"Failed to reload {failed} cogs. Sending error file...")

        await ctx.send(embed=embed)
        if error_str:
            await ctx.send(file=discord.File(io.BytesIO(error_str.encode("utf-8")), "error.nim"))

    @cogmanager.command()
    async def unload(self, ctx: KurisuContext, *cogs):
        """Unload cogs"""
        for ext in cogs:
            self.bot.unload_extension(ext)
        await ctx.send_ok(":ok_hand:")

    @cogmanager.command()
    async def reloadall(self, ctx: KurisuContext):
        """Reload all cogs"""
        errored_out = False

        for i in os.listdir("./src/cogs"):
            if i.endswith(".py"):
                try:
                    self.bot.reload_extension(f"cogs.{i[:-3]}")
                except commands.ExtensionError:
                    errored_out = True

        if errored_out:
            return await ctx.send_error("Errored out somewhere while reloading all cogs. Look at console for feedback")
        else:
            return await ctx.send_ok(":ok_hand:")

    @cogmanager.command()
    async def unloadall(self, ctx: KurisuContext):
        """Unload all cogs"""
        for cog in self.bot.cogs.values():
            cog.cog_unload()

        await ctx.send_ok(":ok_hand:")

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx: KurisuContext):
        await confirm_prompt(
            ctx,
            self.bot.close,
            confirm_str="Restarting now... Cya later :wave:",
            cancelled_str="I guess i'll stay then...",
        )


def setup(bot: Kurisu):
    bot.add_cog(DevTools(bot))
