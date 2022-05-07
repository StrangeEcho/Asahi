from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .bot import Asahi

import asyncio

import discord
from discord.ext import commands


class AsahiContext(commands.Context):
    bot: Asahi

    async def send_ok(self, content: str) -> discord.Message:
        """Send OK embeds"""
        await self.send(
            embed=discord.Embed(description=content, color=self.bot.ok_color).set_footer(
                icon_url=self.author.avatar.url, text=self.author
            )
        )

    async def send_info(self, content: str) -> discord.Message:
        """Send INFO embeds"""
        await self.send(
            embed=discord.Embed(description=content, color=self.bot.info_color).set_footer(
                icon_url=self.author.avatar.url, text=self.author
            )
        )

    async def send_error(self, content: str) -> discord.Message:
        """Send ERROR embeds"""
        await self.send(
            embed=discord.Embed(description=content, color=self.bot.error_color).set_footer(
                icon_url=self.author.avatar.url, text=self.author
            )
        )

    async def trash(self, msg: discord.Message) -> None:
        """Adds a trash reaction to the messages; when clicked, the bot deletes the message"""
        await msg.add_reaction("🗑️")

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return reaction.message.id == msg.id and user == self.author and not user.bot

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)

            reaction: discord.Reaction
            user: discord.User  # throwaway

            await reaction.message.delete()
        except asyncio.TimeoutError:
            pass
