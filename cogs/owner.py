from typing import Optional

import discord
from discord.ext import commands
from dpy_button_utils import ButtonConfirmation


class BotOwner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        # remove `foo`
        return content.strip("` \n")

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
            "Are you sure you want me to logout?",
            destructive=True,
            confirm="Yes",
            cancel="No",
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
            await ctx.send(f"Unloaded cogs {extension}")
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
