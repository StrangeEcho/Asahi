from __future__ import annotations

from textwrap import wrap
from typing import TYPE_CHECKING, Union
import asyncio

from discord.ext import commands, menus
import discord
import toml

if TYPE_CHECKING:
    from .context import KurisuContext
    from .kurisu import KurisuBot


class EmbedListMenu(menus.ListPageSource):
    """
    Paginated embed menu.
    """

    def __init__(self, data):
        """
        Initializes the EmbedListMenu.
        """
        super().__init__(data, per_page=1)

    async def format_page(self, menu, embeds):
        """
        Formats the page.
        """
        return embeds


def get_color(color: str):
    if color not in ["ok_color", "error_color"]:
        return discord.Color.default()

    t = toml.load("configoptions.toml")
    return int(str(t["options"][color]).replace("#", "0x"), base=16)


class AutoPagiantor:
    def __init__(
        self, bot: KurisuBot, ctx: KurisuContext, text: str, limit: int = 100
    ):
        self.bot: KurisuBot = bot
        self.limit: int = limit
        self.text: str = text
        self.index: int = 0
        self.ctx: Union[KurisuContext, commands.Context] = ctx
        self.emojis: list[Union[str, discord.Emoji]] = ["⬅️", "➡️", "❌"]
        self.embeds: list[discord.Embed] = []

    async def start(self) -> None:
        "Start the paginator"
        if len(self.text) < self.limit:
            await self.ctx.send(self.text)

        wrapped_text: list = wrap(self.text, self.limit)
        for t in wrapped_text:
            self.embeds.append(
                discord.Embed(
                    description=t, color=get_color("ok_color")
                ).set_footer(
                    text=f"Page {wrapped_text.index(t) + 1} out of {len(wrapped_text)}"
                )
            )

        global msg
        msg = await self.ctx.send(embed=self.embeds[0])

        await msg.edit(embed=self.embeds[self.index])
        for e in self.emojis:
            await msg.add_reaction(e)

        def check(reaction: discord.Reaction, user: discord.Member):
            return (
                user == self.ctx.author
                and reaction.message == msg
                and user != self.bot
            )

        while True:
            try:
                reaction: discord.Reaction
                user: discord.Member
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=10
                )

                if str(reaction.emoji) == "⬅️":
                    await self.page_left()

                if str(reaction.emoji) == "➡️":
                    await self.page_right()

                if str(reaction.emoji) == "❌":
                    await msg.clear_reactions()
                    break
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.channel.send("Paginator Timed Out!")
                break

    async def page_left(self) -> None:
        """Decrease the page index by one"""
        if self.index == 0:
            return
        self.index -= 1
        await msg.edit(embed=self.embeds[self.index])

    async def page_right(self) -> None:
        """Increase the page index by one"""
        self.index += 1
        await msg.edit(embed=self.embeds[self.index])
