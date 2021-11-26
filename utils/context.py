from discord.ext import commands
import discord

from .helpers import get_color


class KurisuContext(commands.Context):
    """Custom Context"""

    async def send_ok(self, content: str):
        await self.send(
            embed=discord.Embed(
                description=content, color=get_color("ok_color")
            )
        )

    async def send_error(self, content: str):
        await self.send(
            embed=discord.Embed(
                description=content, color=get_color("error_color")
            )
        )
