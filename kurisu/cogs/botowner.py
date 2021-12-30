from contextlib import redirect_stdout
from typing import Optional
import asyncio
import io
import re
import subprocess
import textwrap
import traceback

from discord.errors import HTTPException
from discord.ext import commands
from utils.dbmanagers import ErrorSuppressionHandler
from utils.kurisu import KurisuBot
from utils.context import KurisuContext
import discord

START_CODE_BLOCK_RE = re.compile(r"^((```py(thon)?)(?=\s)|(```))")


class Bot_Owner(commands.Cog):
    """Commands meant to be only used by whoever has owner privileges on the bot."""

    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.esh = ErrorSuppressionHandler(self.bot)
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
        return (
            f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'
        )

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
    async def elevate(self, ctx: KurisuContext, user: discord.User = None):
        """Elevate a user or yourself to ownership privilege"""
        if not ctx.author.id in self.bot.get_config(
            "config", "config", "owner_ids"
        ):
            return await ctx.send(
                embed=discord.Embed(
                    description="Your ID was not found in the OWNER config.",
                    color=self.bot.error_color,
                )
            )
        if not user:
            user = ctx.author
        if user.id in self.bot.owner_ids:
            return await ctx.send(
                embed=discord.Embed(
                    description=f"{user} is already in the ownership privilege set",
                    color=self.bot.error_color,
                )
            )
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="yes", style=discord.ui.ButtonStyle.green
                )
            )
        )

        msg = await ctx.send(
            embed=discord.Embed(
                description="Are you sure you want to do this?\nClick yes to confirm.",
                color=self.bot.ok_color,
            ).set_footer(
                text="⚠️ Elevating people to OWNER privilege will allow them to use owner only commands."
            ),
            components=components,
        )

        def check(payload: discord.Interaction):
            if payload.message.id != msg.id:
                return False
            if payload.user.id not in self.bot.get_config(
                "config", "config", "owner_ids"
            ):
                self.bot.loop.create_task(
                    payload.response.send_message(
                        "You aren't in the bots owners!",
                        ephemeral=True,
                    )
                )
                return False
            return True

        try:
            payload = await self.bot.wait_for(
                "component_interaction", check=check, timeout=10
            )
        except asyncio.TimeoutError:
            await msg.edit(components=None)
            await ctx.message.add_reaction("⏰")
            await ctx.send("`Confirmation Timed Out`")
            return
        await payload.response.defer_update()
        await msg.edit(components=None)
        self.bot.owner_ids.add(user.id)
        filtered = [
            await self.bot.fetch_user(x)
            for x in self.bot.owner_ids
            if not x == 000000000000
        ]
        await ctx.send(
            content=user.mention,
            embed=discord.Embed(
                description="You have two minutes.", color=self.bot.ok_color
            ).add_field(
                name="Current privileged People",
                value="```\n" + "\n".join(map(str, filtered)) + "\n```",
            ),
        )
        loop = asyncio.get_running_loop()

        def remove_owner():
            if user.id not in self.bot.owner_ids:
                pass
            self.bot.owner_ids.remove(user.id)
            self.bot.logger.info(
                f"Removed {user}({user.id}) from the elevated owner privilege set."
            )

        loop.call_later(120, remove_owner)

    @commands.command()
    async def delevate(self, ctx: KurisuContext, user: discord.User = None):
        """Delevate a users ownership privilege"""
        if not ctx.author.id in self.bot.get_config(
            "config", "config", "owner_ids"
        ):
            return await ctx.send(
                embed=discord.Embed(
                    description="You are not authorized to complete this action",
                    color=self.bot.error_color,
                )
            )
        if not user:
            user = ctx.author
        if user.id not in self.bot.owner_ids:
            return await ctx.send(
                embed=discord.Embed(
                    description=f"{user} is currently does not have ownership privilege",
                    color=self.bot.error_color,
                )
            )
        self.bot.owner_ids.remove(user.id)
        await ctx.message.add_reaction("\u2705")

    @commands.command(hidden=True, name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

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

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx: KurisuContext):
        """Restarts the bot"""
        embed = discord.Embed(
            title="Are you sure you want me to restart?",
            color=self.bot.ok_color,
        )
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Yes",
                    style=discord.ui.ButtonStyle.green,
                    custom_id="YES_RESTART",
                ),
                discord.ui.Button(
                    label="No",
                    style=discord.ui.ButtonStyle.red,
                    custom_id="NO_RESTART",
                ),
            )
        )
        msg = await ctx.send(embed=embed, components=components)

        def check(payload: discord.Interaction):
            if payload.message.id != msg.id:
                return False
            if payload.user.id not in ctx.bot.owner_ids:
                self.bot.loop.create_task(
                    payload.response.send_message(
                        "You can't respond to this message!",
                        ephemeral=True,
                    )
                )
                return False
            return True

        try:
            payload = await self.bot.wait_for(
                "component_interaction", check=check, timeout=60
            )
        except asyncio.TimeoutError:
            embed.title = "Timed out... I guess I will stay then"
            return await msg.edit(embed=embed, components=None)
        if payload.component.custom_id == "YES_RESTART":
            embed.title = "Attempting to restart. See you in a bit. :wave:"
            await msg.edit(embed=embed, components=None)
            await self.bot.close()
        else:
            embed.title = "I guess I will stay then"
            await msg.edit(embed=embed, components=None)

    @commands.command(aliases=["shutdown", "logout", "sleep"])
    @commands.is_owner()
    async def die(self, ctx: KurisuContext):
        """Kills the bot process. IF BOT IS RUNNING WITH PM2 IT WILL RESTART REGARDLESS."""

        embed = discord.Embed(title="Are you sure you want me to shutdown?")
        embed.color = self.bot.ok_color
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Yes",
                    style=discord.ui.ButtonStyle.green,
                    custom_id="YES_SHUT",
                ),
                discord.ui.Button(
                    label="No",
                    style=discord.ui.ButtonStyle.red,
                    custom_id="NO_SHUT",
                ),
            )
        )
        msg = await ctx.send(embed=embed, components=components)

        def check(payload: discord.Interaction):
            if payload.message.id != msg.id:
                return False
            if payload.user.id not in ctx.bot.owner_ids:
                self.bot.loop.create_task(
                    payload.response.send_message(
                        "You can't respond to this message!",
                        ephemeral=True,
                    )
                )
                return False
            return True

        try:
            payload = await self.bot.wait_for(
                "component_interaction", check=check, timeout=60
            )
        except asyncio.TimeoutError:
            embed.title = "Timed out... I guess I will stay then"
            return await msg.edit(embed=embed, components=None)
        if payload.component.custom_id == "YES_SHUT":
            embed.title = "Goodbye then :wave:"
            await msg.edit(embed=embed, components=None)
            await self.bot.full_exit()
        else:
            embed.title = "I guess I will stay then"
            await msg.edit(embed=embed, components=None)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: KurisuContext, *extensions):
        """Load bot extensions"""
        success_list: list[str] = []
        failed_extensions: list[str] = []
        for ext in extensions:
            try:
                self.bot.load_extension(ext)
                success_list.append(f":inbox_tray: `{ext[5:].capitalize()}`")
            except commands.ExtensionError as e:
                failed_extensions.append(
                    f":x: `{ext[5:].capitalize()}` - `{e}`"
                )
        await ctx.send(
            embed=discord.Embed(title="Summary", color=self.bot.ok_color)
            .add_field(
                name="Loaded Successfully",
                value="\n".join(success_list) or "`None`",
            )
            .add_field(
                name="Failed To Load",
                value="\n".join(failed_extensions) or "`None`",
                inline=False,
            )
        )

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: KurisuContext, *extensions):
        """Unload bot extensions"""
        success_list: list[str] = []
        failed_extensions: list[str] = []
        for ext in extensions:
            try:
                self.bot.unload_extension(ext)
                success_list.append(f":outbox_tray: `{ext[5:].capitalize()}`")
            except commands.ExtensionError as e:
                failed_extensions.append(
                    f":x: `{ext[5:].capitalize()}` - `{e}`"
                )
        await ctx.send(
            embed=discord.Embed(title="Summary", color=self.bot.ok_color)
            .add_field(
                name="Unloaded Successfully",
                value="\n".join(success_list) or "None",
            )
            .add_field(
                name="Failed To Unload",
                value="\n".join(failed_extensions) or "None",
                inline=False,
            )
        )

    @commands.command(name="reload")
    @commands.is_owner()
    async def _reload(self, ctx: KurisuContext, *extensions):
        """Reload bot extensions"""
        success_list: list[str] = []
        failed_extensions: list[str] = []
        for ext in extensions:
            try:
                self.bot.reload_extension(ext)
                success_list.append(f":repeat: `{ext[5:].capitalize()}`")
            except commands.ExtensionError as e:
                failed_extensions.append(
                    f":x: `{ext[5:].capitalize()}` - `{e}`"
                )
        await ctx.send(
            embed=discord.Embed(title="Summary", color=self.bot.ok_color)
            .add_field(
                name="Reloaded Successfully",
                value="\n".join(success_list) or "None",
            )
            .add_field(
                name="Failed To Reload",
                value="\n".join(failed_extensions) or "None",
                inline=False,
            )
        )

    @commands.command()
    @commands.is_owner()
    async def reloadall(self, ctx: KurisuContext):
        """Reloads everysingle cog the bot has"""
        await ctx.send(
            embed=discord.Embed(
                description="Attempting to reload all cogs/extensions",
                color=self.bot.ok_color,
            )
        )
        await self.bot.reload_all_extensions(ctx)

    @commands.is_owner()
    @commands.command()
    async def update(self, ctx: KurisuContext):
        """Update to the latest version of the master repo or whatever the latest commit of your fork is"""
        await ctx.send(
            embed=discord.Embed(
                description=f"Attempting to update {self.bot.user.name} to the latest commit/version.",
                color=self.bot.ok_color,
            )
        )
        process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
        output = process.communicate()[0]
        await ctx.send(
            embed=discord.Embed(
                description=f"Output: ```{str(output[:1800], 'utf-8')}```",
                color=self.bot.ok_color,
            )
        )
        process = subprocess.Popen(
            ["git", "describe", "--always"], stdout=subprocess.PIPE
        )
        output = process.communicate()[0]
        await ctx.send(
            embed=discord.Embed(
                description="Reloading all modules now.",
                color=self.bot.ok_color,
            )
        )
        await asyncio.sleep(1.5)
        await self.bot.reload_all_extensions(ctx)
        await ctx.send(
            embed=discord.Embed(
                description=f"Sucessfully updated {self.bot.user.name} Version `{self.bot.version}` to `{str(output, 'utf-8')}`",
                color=self.bot.ok_color,
            )
        )

    @commands.command()
    @commands.is_owner()
    async def say(
        self, ctx, chan: Optional[discord.TextChannel] = None, *, msg
    ):
        """Say something with the bot."""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass
        if chan is None:
            await ctx.send(msg)
        else:
            await chan.send(msg)

    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx: KurisuContext, user: discord.User, *, msg):
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
            await ctx.send(
                embed=discord.Embed(description=e, color=self.bot.error_color)
            )

    @commands.command(name="frick", aliases=["sho"])
    @commands.is_owner()
    @commands.guild_only()
    async def frick(self, ctx: KurisuContext, limit: int = 50) -> None:
        """
        Cleans up the bots messages.
        `limit`: The amount of messages to check back through. Defaults to 50.
        """

        prefix = self.bot.get_config("config", "config", "prefix")

        if ctx.channel.permissions_for(ctx.me).manage_messages:
            messages = await ctx.channel.purge(
                check=lambda message: message.author == ctx.me
                or message.content.startswith(prefix),
                bulk=True,
                limit=limit,
            )
        else:
            messages = await ctx.channel.purge(
                check=lambda message: message.author == ctx.me,
                bulk=False,
                limit=limit,
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
    async def fetch(self, ctx: KurisuContext, id: int):
        user = await self.bot.fetch_user(id)

        user_flags = "\n".join(
            i.replace("_", " ").title() for i, v in user.public_flags if v
        )

        embed = discord.Embed(
            title=f"User: {user}",
            description=f"Fetched info for user: `{user}`",
            color=self.bot.ok_color,
        )
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="ID", value=f"`{user.id}`")
        embed.add_field(name="Avatar", value=f"[URL]({user.avatar.url})")
        embed.add_field(
            name="Account Creation",
            value=f"`{user.created_at.strftime('%c')}`",
        )
        embed.add_field(name="Bot", value="\u2705" if user.bot else ":x:")
        embed.add_field(
            name="System", value="\u2705" if user.system else ":x:"
        )
        if user.public_flags:
            embed.add_field(
                name="Public Flags", value=f"```\n{user_flags}\n```"
            )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def leaveguild(self, ctx: KurisuContext, id: int):
        try:
            await self.bot.get_guild(id).leave()
            await ctx.send(":ok_hand:")
        except HTTPException as e:
            await ctx.send(e)

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def suppress(self, ctx: KurisuContext):
        """Guild error suppression commands"""
        await ctx.send_help(ctx.command)

    @suppress.command()
    async def add(self, ctx: KurisuContext, guild: int):
        """Add a guild to the suppressed guilds list"""
        await self.esh.insert(guild)
        await ctx.send(":ok_hand:")

    @suppress.command()
    async def list(self, ctx: KurisuContext):
        """Add a guild to the suppressed guilds list"""
        await ctx.send(
            "\n".join(
                [
                    f"{n}. {v}"
                    for n, v in enumerate((await self.esh.fetch_all())[0], 1)
                ]
                if await self.esh.fetch_all()
                else "None"
            )
        )

    @suppress.command()
    async def remove(self, ctx: KurisuContext, guild: int):
        """Add a guild to the suppressed guilds list"""
        await self.esh.remove(guild)
        await ctx.send(":ok_hand:")


def setup(bot):
    bot.add_cog(Bot_Owner(bot))
