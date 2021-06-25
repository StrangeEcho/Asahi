from contextlib import redirect_stdout
from typing import Optional
import asyncio
import inspect
import io
import re
import textwrap
import traceback

from discord.ext import commands
from dpy_button_utils import ButtonConfirmation
import discord

from utils.classes import HimejiBot
from utils.funcs import box
import config

START_CODE_BLOCK_RE = re.compile(r"^((```py(thon)?)(?=\s)|(```))")


# most stuffs in this owner cog related to development is from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py
class BotOwner(commands.Cog):
    def __init__(self, bot: HimejiBot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return START_CODE_BLOCK_RE.sub("", content)[:-3]

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
    async def _eval(self, ctx: commands.Context, *, body: str):
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
                try:
                    return
                except:
                    paginated_text = self.paginate(value)
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            await ctx.send(f"```py\n{page}\n```")
                            break
                        await ctx.send(f"```py\n{page}\n```")
            else:
                self._last_result = ret
                try:
                    await ctx.send(f"```py\n{value}{ret}\n```")
                except:
                    paginated_text = self.paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            await ctx.send(f"```py\n{page}\n```")
                            break
                        await ctx.send(f"```py\n{page}\n```")

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx: commands.Context):
        """Restarts out the bot"""
        if await ButtonConfirmation(
            ctx,
            "Are you sure you want me to shutdown?",
            destructive=True,
            confirm="Yes",
            cancel="No",
            confirm_message="Goodbye then :wave:",
            cancel_message="I guess I will stay then",
        ).run():
            await self.bot.close()

    @commands.command(aliases=["shutdown", "logout", "sleep"])
    @commands.is_owner()
    async def die(self, ctx: commands.Context):
        """Kills the bot process"""
        if await ButtonConfirmation(
            ctx,
            "Are you sure you want me to shutdown?",
            destructive=True,
            confirm="Yes",
            cancel="No",
            confirm_message="Goodbye then :wave:",
            cancel_message="I guess I will stay then",
        ).run():
            exit(code=26)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, extension):
        """Load bot extensions"""
        try:
            self.bot.load_extension(extension)
            await ctx.send(
                embed=discord.Embed(
                    description=f":inbox_tray: Loaded `{extension}`",
                    color=self.bot.ok_color,
                )
            )
        except commands.ExtensionError as e:
            await ctx.send(embed=discord.Embed(description=e, color=self.bot.error_color))

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, extension):
        """Unload bot extensions"""
        try:
            self.bot.unload_extension(extension)
            await ctx.send(
                embed=discord.Embed(
                    description=f":outbox_tray: Unloaded `{extension}`",
                    color=self.bot.ok_color,
                )
            )
        except commands.ExtensionError as e:
            await ctx.send(embed=discord.Embed(description=e, color=self.bot.error_color))

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, extension):
        """Reload bot extensions"""
        try:
            self.bot.reload_extension(extension)
            await ctx.send(
                embed=discord.Embed(
                    description=f":repeat: Reloaded `{extension}`",
                    color=self.bot.ok_color,
                )
            )
        except commands.ExtensionError as e:
            await ctx.send(embed=discord.Embed(description=e, color=self.bot.error_color))

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
    @commands.is_owner()
    async def repl(self, ctx: commands.Context):
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

    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx: commands.Context, user: discord.User, *, msg):
        try:
            await user.send(
                embed=discord.Embed(
                    title=f"Message from {ctx.author}",
                    description=msg,
                    color=self.bot.ok_color,
                )
            )
            await ctx.send(
                embed=discord.Embed(
                    description=f"Direct Message sent to {user}",
                    color=self.bot.ok_color,
                )
            )
        except (discord.HTTPException, discord.Forbidden) as e:
            await ctx.send(embed=discord.Embed(description=e, color=self.bot.error_color))

    @commands.command(name="frick", aliases=["sho"])
    @commands.is_owner()
    @commands.guild_only()
    async def frick(self, ctx: commands.Context, limit: int = 50) -> None:
        """
        Cleans up the bots messages.
        `limit`: The amount of messages to check back through. Defaults to 50.
        """

        prefix = config.BOT_PREFIX

        if ctx.channel.permissions_for(ctx.me).manage_messages:
            messages = await ctx.channel.purge(
                check=lambda message: message.author == ctx.me
                or message.content.startswith(prefix),
                bulk=True,
                limit=limit,
            )
        else:
            messages = await ctx.channel.purge(
                check=lambda message: message.author == ctx.me, bulk=False, limit=limit
            )

        await ctx.send(
            embed=discord.Embed(
                description=f"Found and deleted `{len(messages)}` of my message(s) out of the last `{limit}` message(s).",
                color=self.bot.ok_color,
            )
        )


def setup(bot):
    bot.add_cog(BotOwner(bot))
