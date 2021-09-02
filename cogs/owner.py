from configoptions import OK_COLOR
from contextlib import redirect_stdout
from typing import Optional
import asyncio
import inspect
import io
import os
import re
import textwrap
import traceback
import subprocess

from discord.ext import commands
from dpy_button_utils import ButtonConfirmation
import discord

from utils.classes import KurisuBot
from utils.funcs import box
import config

START_CODE_BLOCK_RE = re.compile(r"^((```py(thon)?)(?=\s)|(```))")


class BotOwner(commands.Cog):
    """Bot Owner only commands"""

    def __init__(self, bot: KurisuBot):
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

    @staticmethod
    def get_syntax_error(self, e):
        if e.text is None:
            return f"```py\n{e.__class__.__name__}: {e}\n```"
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @staticmethod
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
    
    @commands.command()
    async def elevate(self, ctx: commands.Context, user: discord.User = None):
        if not ctx.author.id in config.OWNER_IDS:
            return await ctx.send(
                embed=discord.Embed(
                    description="Your ID was not found in the OWNER config.",
                    color=self.bot.error_color
                )
            )
        if not user:
            user = ctx.author

        msg = await ctx.send(
            embed=discord.Embed(
                description="Are you sure you want to do this?\nReact with ✅ to confirm.",
                color=self.bot.ok_color
            ).set_footer(text="⚠️ Elevating people to OWNER privledge will allow them to use owner only commands.")
        )
        await msg.add_reaction("\u2705")
 
        def check(reaction: discord.Reaction, user: discord.User):
            return user.id == ctx.author.id and str(reaction.emoji) == "\u2705"
        
        try:
            await self.bot.wait_for("reaction_add", check=check, timeout=10)
            self.bot.owner_ids.add(user.id)
            filtered = [await self.bot.fetch_user(x) for x in self.bot.owner_ids if not x == 000000000000]
            await ctx.send(
                content=user.mention,
                embed=discord.Embed(
                    description="You have two minutes.",
                    color=self.bot.ok_color
                ).add_field(
                    name="Current Privledged People",
                    value="```\n" + "\n".join(map(str, filtered)) + "\n```" 
                )
            )
            loop = asyncio.get_running_loop()
            def remove_owner():
                self.bot.owner_ids.remove(user.id)
                self.bot.logger.info(f"Removed {user}({user.id}) from the elevated owner privledge set.")
            loop.call_later(10, remove_owner)
        except asyncio.TimeoutError:
            await ctx.message.add_reaction("⏰")
            await ctx.send("`Confirmation Timed Out`")

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
        """Restarts the bot"""
        if await ButtonConfirmation(
            ctx,
            "Are you sure you want me to restart?",
            destructive=True,
            confirm="Yes",
            cancel="No",
            confirm_message="Attempting to restart. See you in a bit. :wave:",
            cancel_message="I guess I will stay then",
        ).run():
            await self.bot.close()

    @commands.command(aliases=["shutdown", "logout", "sleep"])
    @commands.is_owner()
    async def die(self, ctx: commands.Context):
        """Kills the bot process. IF BOT IS RUNNING WITH PM2 IT WILL RESTART REGARDLESS."""
        if await ButtonConfirmation(
            ctx,
            "Are you sure you want me to shutdown?",
            destructive=True,
            confirm="Yes",
            cancel="No",
            confirm_message="Goodbye then :wave:",
            cancel_message="I guess I will stay then",
        ).run():
            await self.bot.full_exit()

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
    async def reloadall(self, ctx: commands.Context):
        """Reloads everysingle cog the bot has"""
        await ctx.send(
            embed=discord.Embed(
                description="Attempting to reload all cogs/extensions",
                color=self.bot.ok_color
            )
        )
        await self.bot.reload_all_extensions(ctx)


    @commands.is_owner()
    @commands.command()
    async def update(self, ctx: commands.Context):
        """Update to the latest version of KurisuBot or whatever the latest commit of your fork is"""
        await ctx.send(
            embed=discord.Embed(
                description="Attempting to update KurisuBot to latest version",
                color=self.bot.ok_color
            )
        )
        process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
        output = process.communicate()[0]
        await ctx.send(
            embed=discord.Embed(
                description=f"Output: ```{str(output[:1800], 'utf-8')}```",
                color=self.bot.ok_color
            )
        )
        process = subprocess.Popen(["git", "describe", "--always"], stdout=subprocess.PIPE)
        output = process.communicate()[0]  
        await ctx.send(
            embed=discord.Embed(
                description="Reloading all modules now.",
                color=self.bot.ok_color
            )
        )
        await asyncio.sleep(1.5)
        await self.bot.reload_all_extensions(ctx)
        await ctx.send(
            embed=discord.Embed(
                description=f"Sucessfully updated KurisuBot Version `{self.bot.version}` to `{str(output, 'utf-8')}`",
                color=self.bot.ok_color
            )
        )

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

    @commands.command()  # Command from RoboDanny https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py
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
        """Direct Message A User"""
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
            ),
            delete_after=5,
        )

    @commands.command()
    @commands.is_owner()
    async def fetch(self, ctx: commands.Context, id: int):
        user = await self.bot.fetch_user(id)

        user_flags = "\n".join(i.replace("_", " ").title() for i, v in user.public_flags if v)

        embed = discord.Embed(
            title=f"User: {user}",
            description=f"Fetched info for user: `{user}`",
            color=self.bot.ok_color,
        )
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="ID", value=f"`{user.id}`")
        embed.add_field(name="Avatar", value=f"[URL]({user.avatar.url})")
        embed.add_field(name="Account Creation", value=f"`{user.created_at.strftime('%c')}`")
        embed.add_field(name="Bot", value="\u2705" if user.bot else ":x:")
        embed.add_field(name="System", value="\u2705" if user.system else ":x:")
        if user.public_flags:
            embed.add_field(name="Public Flags", value=f"```\n{user_flags}\n```")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def leave(self, ctx: commands.Context, guild: discord.Guild):
        await guild.leave()
        await ctx.send(f"Successfully left {guild.name}")


def setup(bot):
    bot.add_cog(BotOwner(bot))
