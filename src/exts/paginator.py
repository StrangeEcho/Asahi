from __future__ import annotations

from asyncio import TimeoutError
from typing import TYPE_CHECKING
import re

import discord

if TYPE_CHECKING:
    from core import AsahiContext


class Paginator:
    def __init__(
        self,
        embeds: list[discord.Embed],
        timeout: int = 60,
    ):
        self.embeds = embeds
        self.timeout = timeout
        self._emojis = ["⬅️", "🛑", "➡️"]
        self._index = 0

    async def start(self, ctx: AsahiContext):
        """Start the paginator"""
        msg = await ctx.send(embed=self.embeds[0])
        for e in self._emojis:
            await msg.add_reaction(e)

        def check(reaction: discord.Reaction, user: discord.User):
            return ctx.author == user and reaction.message == msg

        while True:
            try:
                reaction, _ = await ctx.bot.wait_for("reaction_add", timeout=self.timeout, check=check)
                reaction: discord.Reaction
            except TimeoutError:
                break
            match str(reaction.emoji):
                case "⬅️":
                    await self.page_left(msg)
                case "➡️":
                    await self.page_right(msg)
                case "🛑":
                    await msg.clear_reactions()
                    break

    async def page_left(self, msg: discord.Message):
        if self._index == 0:
            return
        self._index -= 1
        await msg.edit(embed=self.embeds[self._index])

    async def page_right(self, msg: discord.Message):
        if self._index == len(self.embeds) - 1:
            return
        else:
            self._index += 1
            print(self._index)
            await msg.edit(embed=self.embeds[self._index])
