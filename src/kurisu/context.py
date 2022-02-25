from __future__ import annotations

import asyncio
from typing import Any, Optional, TYPE_CHECKING

from disnake.ext import commands
from exts.functions import color_convert
from helpers.confighandler import Config

if TYPE_CHECKING:
    from .bot import Kurisu
import disnake


class KurisuContext(commands.Context):
    """Subclass for added functionality"""

    bot: Kurisu

    config = Config()

    async def send_info(self, content: Any) -> Optional[disnake.Message]:
        """Send INFO embed"""
        await super().send(
            embed=disnake.Embed(
                description=str(content), color=color_convert(self.config.get("info_color"))
            ).set_footer(text=str(self.author), icon_url=self.author.display_avatar.url)
        )

    async def send_ok(self, content: Any) -> Optional[disnake.Message]:
        """Send OK embed"""
        await super().send(
            embed=disnake.Embed(description=str(content), color=color_convert(self.config.get("ok_color"))).set_footer(
                text=str(self.author), icon_url=self.author.display_avatar.url
            )
        )

    async def send_error(self, content: Any, *, trash: bool = False) -> Optional[disnake.Message]:
        """Send ERROR embed"""
        msg = await super().send(
            embed=disnake.Embed(
                description=str(content), color=color_convert(self.config.get("error_color"))
            ).set_footer(text=str(self.author), icon_url=self.author.display_avatar.url)
        )
        if trash:
            await self._trash(msg)

    async def _trash(self, message: disnake.Message):
        await message.add_reaction("🗑️")

        def check(reaction: disnake.Reaction, user: disnake.User):
            return reaction.message.id == message.id and user == self.author and not user.bot

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)
            await reaction.message.delete()
        except asyncio.TimeoutError:
            pass
