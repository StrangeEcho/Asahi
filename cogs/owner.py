import asyncio
import inspect
import io
import textwrap
import traceback
from contextlib import redirect_stdout
from typing import Optional

import discord
from discord.ext import commands
from dpy_button_utils import ButtonConfirmation

from utils.funcs import box


# most stuffs in this owner cog related to development is from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py
class BotOwner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        # remove `foo`
        return content.strip("` \n")

    def get_syntax_error(self, e):
        if e.text is None:
            return f"```py\n{e.__class__.__name__}: {e}\n```"
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    def paginate(self, text: str):
        """Fix the limit since tyler gay."""
        last = 0
        pages = []
        for curr in range(0, len(text)):
            if curr % 1980 == 0:
                pages.append(text[last:curr])
                last = curr
                appd_index = curr
        if appd_index != len(text) - 1:
            pages.append(text[last:curr])
        return list(filter(lambda a: a != "", pages))

    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates python code"""

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f"```py\n{value}\n```")
            else:
                self._last_result = ret
                await ctx.send(f"```py\n{value}{ret}\n```")

    @commands.command(aliases=["shutdown", "logout", "sleep"])
    @commands.is_owner()
    async def die(self, ctx: commands.Context):
        """Log out the bot"""
        if await ButtonConfirmation(
            ctx,
            "Are you sure you want me to shutdown?",
            destructive=True,
            confirm="Yes",
            cancel="No",
        ).run():
            await ctx.send("Goodbye then :wave:")
            await self.bot.close()
        else:
            await ctx.send("I guess I will stay then.")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, extension):
        """Load bot extensions"""
        try:
            self.bot.load_extension(extension)
            await ctx.send(f":inbox_tray: Loaded extension: `{extension}`")
        except commands.ExtensionError as e:
            await ctx.send(e)

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, extension):
        """Unload bot extensions"""
        try:
            self.bot.unload_extension(extension)
            await ctx.send(f":outbox_tray: Unloaded extension: `{extension}`")
        except commands.ExtensionError as e:
            await ctx.send(e)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, extension):
        """Reload bot extensions"""
        try:
            self.bot.reload_extension(extension)
            await ctx.send(f"<a:cog_reload:850891346910773248> Reloaded extension: `{extension}`")
        except commands.ExtensionError as e:
            await ctx.send(e)

    @commands.command()
    @commands.is_owner()
    async def say(self, ctx, chan: Optional[discord.TextChannel] = None, *, msg):
        """Say something with the bot."""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass
        if chan is None:
            await ctx.send(msg)
        else:
            await chan.send(msg)

    @commands.command(pass_context=True, hidden=True)
    async def repl(self, ctx):
        """Launches an interactive REPL session."""
        variables = {
            "ctx": ctx,
            "bot": self.bot,
            "message": ctx.message,
            "guild": ctx.guild,
            "channel": ctx.channel,
            "author": ctx.author,
            "_": None,
        }

        if ctx.channel.id in self.sessions:
            await ctx.send("Already running a REPL session in this channel. Exit it with `quit`.")
            return

        self.sessions.add(ctx.channel.id)
        await ctx.send("Enter code to execute or evaluate. `exit()` or `quit` to exit.")

        def check(m):
            return (
                m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id
                and m.content.startswith("`")
            )

        while True:
            try:
                response = await self.bot.wait_for("message", check=check, timeout=10.0 * 60.0)
            except asyncio.TimeoutError:
                await ctx.send("Exiting REPL session.")
                self.sessions.remove(ctx.channel.id)
                break

            cleaned = self.cleanup_code(response.content)

            if cleaned in ("quit", "exit", "exit()"):
                await ctx.send("Exiting.")
                self.sessions.remove(ctx.channel.id)
                return

            executor = exec
            if cleaned.count("\n") == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, "<repl session>", "eval")
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, "<repl session>", "exec")
                except SyntaxError as e:
                    await ctx.send(self.get_syntax_error(e))
                    continue

            variables["message"] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                fmt = f"\n{value}{traceback.format_exc()}\n"
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = f"\n{value}{result}\n"
                    variables["_"] = result
                elif value:
                    fmt = f"\n{value}\n"

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        paginated_text = self.paginate(fmt)
                        for page in paginated_text:
                            if page == paginated_text[-1]:
                                await ctx.send(box(f"\n{page}\n", "py"))
                                break
                            await ctx.send(box(f"\n{page}\n", "py"))
                    else:
                        await ctx.send(box(fmt, "py"))
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await ctx.send(f"Unexpected error: `{e}`")


def setup(bot: commands.Bot):
    bot.add_cog(BotOwner(bot))
