from __future__ import annotations

from textwrap import wrap
from typing import TYPE_CHECKING, Union

from discord.ext import commands, menus, vbu
import aiohttp
import discord
import toml

from .funcs import box
from .errors import UrbanDictionaryError

if TYPE_CHECKING:
    from .context import KurisuContext


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


def get_color(color: str) -> int:
    if color not in ["ok_color", "error_color"]:
        return discord.Color.default()

    t = toml.load("configoptions.toml")
    return int(str(t["options"][color]).replace("#", "0x"), base=16)


async def autopaginate(
        text: str,
        limit: int,
        ctx: Union[commands.Context, KurisuContext],
        codeblock: bool = False,
):
    """Automatic Paginator"""
    wrapped_text: list[str] = wrap(text, limit)
    embeds: list[discord.Embed] = []

    for t in wrapped_text:
        embeds.append(
            discord.Embed(
                description=box(t, "py") if codeblock else t,
                color=get_color("ok_color"),
            ).set_footer(
                text=f"Page {wrapped_text.index(t) + 1} out of {len(wrapped_text)}"
            )
        )
    await vbu.Paginator(embeds, per_page=1).start(ctx)


async def get_ud_results(term: str, max: int = 5):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.urbandictionary.com/v0/define?term={term}") as resp:
            try:
                return (await resp.json())["list"][:max]
            except (IndexError, KeyError) as e:
                raise UrbanDictionaryError("Error while querying Urban Dictionary API with that term")
