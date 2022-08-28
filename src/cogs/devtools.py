from contextlib import redirect_stdout
from datetime import datetime
from subprocess import PIPE
from typing import Optional
import asyncio
import io
import os
import re
import textwrap
import traceback

from discord.ext import commands
import discord

from core import Asahi, AsahiContext

START_CODE_BLOCK_RE = re.compile(r"^((```py(thon)?)(?=\s)|(```))")


class DevTools(commands.Cog):
    """Developer Tools"""

    def __init__(self, bot: Asahi):
        self.bot = bot
        self._last_result = None

    @staticmethod
    def cleanup_code(content) -> str:
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return START_CODE_BLOCK_RE.sub("", content)[:-3]

        # remove `foo`
        return content.strip("` \n")

    @commands.command(name="eval", aliases=["evaluate", "ev"])
    @commands.is_owner()
    async def _eval(self, ctx: AsahiContext, *, body: str):
        """Evaluate Python Code"""
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self,
        }
        env.update(globals())
        stdout = io.StringIO()
        body = self.cleanup_code(body)
        to_compile = f"async def func():\n{textwrap.indent(body, '  ')}"
        before = datetime.now()

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send_error("".join(traceback.format_exception(None, e, e.__traceback__)))

        func = env["func"]

        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send_error(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except discord.Forbidden:
                pass
            difference = datetime.now() - before

            if not ret:
                if value:
                    await ctx.send(
                        embed=discord.Embed(
                            title=f"Eval executed after {difference.seconds}.{difference.microseconds // 1000}",
                            description=f"```py\n{value[:1500]}\n```",
                            color=self.bot.ok_color,
                        )
                    )
            else:
                self._last_result = ret
                await ctx.send(
                    embed=discord.Embed(
                        title=f"Eval executed after {difference.seconds}.{difference.microseconds // 1000}",
                        description=f"```py\n{value}{ret}```"[:1500],
                        color=self.bot.ok_color,
                    )
                )

    @commands.command()
    @commands.is_owner()
    async def savechat(self, ctx: AsahiContext, limit: int = 15):
        """Save messages from the current text channel"""

        basestr = ""
        async for msg in ctx.channel.history(limit=limit):
            basestr += f"{msg.author}: {msg.content}\n"

        await ctx.send(
            file=discord.File((io.BytesIO(basestr.encode("utf-8"))), f"{ctx.message.created_at.strftime('%c')}.txt")
        )

    @commands.command()
    async def load(self, ctx: AsahiContext, *cogs):
        """Load Cogs"""
        succeed = 0
        failed = 0
        error_str = ""
        embed = discord.Embed(description=":ok_hand:", color=self.bot.info_color)

        for ext in cogs:
            try:
                await self.bot.load_extension(ext)
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

    @commands.command()
    async def reload(self, ctx: AsahiContext, *cogs):
        """Reload cogs"""
        succeed = 0
        failed = 0
        error_str = ""
        embed = discord.Embed(description=":ok_hand:", color=self.bot.info_color)

        for ext in cogs:
            try:
                await self.bot.reload_extension(ext)
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

    @commands.command()
    async def unload(self, ctx: AsahiContext, *cogs):
        """Unload cogs"""
        for ext in cogs:
            await self.bot.unload_extension(ext)
        await ctx.send_ok(":ok_hand:")

    @commands.command()
    async def reloadall(self, ctx: AsahiContext):
        """Reload all cogs"""
        errored_out = False

        for i in os.listdir("./src/cogs"):
            if i.endswith(".py"):
                try:
                    await self.bot.reload_extension(f"cogs.{i[:-3]}")
                except commands.ExtensionError:
                    errored_out = True

        if errored_out:
            return await ctx.send_error("Errored out somewhere while reloading all cogs. Look at console for feedback")
        else:
            return await ctx.send_ok(":ok_hand:")

    @commands.command()
    async def unloadall(self, ctx: AsahiContext):
        """Unload all cogs"""
        for cog in self.bot.cogs.values():
            await cog.cog_unload()

        await ctx.send_ok(":ok_hand:")

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx: AsahiContext):
        """Restart the bot"""
        await ctx.send_ok("Attempting to restart now. Cya later...")
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx: AsahiContext):
        """Update the bot"""
        before = datetime.now()
        await ctx.trigger_typing()
        old_version = str(
            (await (await asyncio.create_subprocess_shell("git describe --always", stdout=PIPE)).communicate())[0],
            "utf-8",
        ).replace("\n", "")
        await ctx.send_info(f"Now attempting to update {self.bot.user.name} to the latest version.")
        await ctx.trigger_typing()
        pull_output = str(
            (await (await asyncio.create_subprocess_shell("git pull", stdout=PIPE)).communicate())[0][:1000], "utf-8"
        )
        await ctx.send_info(f"```\n{pull_output}\n```")
        new_version = str(
            (await (await asyncio.create_subprocess_shell("git describe --always", stdout=PIPE)).communicate())[0],
            "utf-8",
        ).replace("\n", "")
        after = datetime.now()
        difference = after - before
        await ctx.send_ok(
            f"Finished `{old_version} -> {new_version}`\n"
            f"Took: `{difference.seconds}.{difference.microseconds // 1000}`"
        )

    @commands.command()
    @commands.is_owner()
    async def say(self, ctx: AsahiContext, chan: Optional[discord.TextChannel], *, msg):
        """Say something with the bot"""
        chan = chan or ctx.channel
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await chan.send(msg)

    @commands.command(aliases=["frick"])
    @commands.is_owner()
    async def sho(self, ctx: AsahiContext, limit: int = 50):
        """Cleans the bots messages"""
        messages = await ctx.channel.purge(
            check=lambda message: message.author == ctx.me, bulk=True if limit > 20 else False, limit=limit
        )
        await ctx.send_ok(f"Deleted {len(messages)} of my message(s) out of the last {limit} messages")

    @commands.command()
    @commands.is_owner()
    async def fetch(self, ctx: AsahiContext, _id: int):
        """Fetch information about a specific discord user"""
        user = await self.bot.fetch_user(_id)
        flags = [v.replace("_", " ").title() for v, b in user.public_flags if b]
        if not user:
            raise commands.BadArgument(f"Failed converting {_id} to user.")
        await ctx.send(
            embed=discord.Embed(title=f"Information for {user}", color=self.bot.info_color)
            .set_thumbnail(url=user.display_avatar.url)
            .add_field(name="ID", value=user.id)
            .add_field(name="Avatar URL", value=f"[url]({user.display_avatar.url})")
            .add_field(name="Account Creation", value=discord.utils.format_dt(user.created_at, style="R"))
            .add_field(name="Bot", value=":white_check_mark:" if user.bot else ":x:")
            .add_field(name="Flags", value="".join(flags) if flags else "None")
        )

    @commands.command()
    @commands.is_owner()
    async def leaveguild(self, ctx: AsahiContext, guild_id: int):
        """Force the bot to leave a guild"""
        try:
            await self.bot.get_guild(guild_id).leave()
            await ctx.send_ok("Left that guild.")
        except discord.HTTPException as error:
            await ctx.send_error(error)


async def setup(bot: Asahi):
    await bot.add_cog(DevTools(bot))
