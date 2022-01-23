from typing import Any
import asyncio

from discord.ext import commands
from helpers.confighandler import Config
from exts.functions import color_convert
import discord


class KurisuContext(commands.Context):
    """Subclass for added functionality"""

    config = Config()

    async def send_info(self, content: Any) -> None:
        """Send INFO embed"""
        await super().send(
            embed=discord.Embed(
                description=str(content), color=color_convert(self.config.get("info_color"))
            ).set_footer(text=str(self.author), icon_url=self.author.display_avatar.url)
        )

    async def send_ok(self, content: Any) -> None:
        """Send OK embed"""
        await super().send(
            embed=discord.Embed(description=str(content), color=color_convert(self.config.get("ok_color"))).set_footer(
                text=str(self.author), icon_url=self.author.display_avatar.url
            )
        )

    async def send_error(self, content: Any, *, trash: bool) -> None:
        """Send ERROR embed"""
        msg = await super().send(
            embed=discord.Embed(
                description=str(content), color=color_convert(self.config.get("error_color"))
            ).set_footer(text=str(self.author), icon_url=self.author.display_avatar.url)
        )
        if trash:
            await self._trash(msg)

    async def _trash(self, message: discord.Message):
        await message.add_reaction("🗑️")

        def check(reaction: discord.Reaction, user: discord.User):
            return reaction.message.id == message.id and user == message.author

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)
            await reaction.message.delete()
        except asyncio.TimeoutError:
            pass
