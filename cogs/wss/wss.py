import datetime
import itertools
import textwrap
from collections import Counter
from typing import Iterator, List, Optional, Sequence, SupportsInt, Union

from babel.numbers import format_decimal
from discord.ext import commands
from tabulate import tabulate

from .menu import *
from .utils import AsyncIter


def pagify(
    text: str,
    delims: Sequence[str] = ["\n"],
    *,
    priority: bool = False,
    shorten_by: int = 8,
    page_length: int = 2000,
) -> Iterator[str]:
    """Generate multiple pages from the given text."""
    in_text = text
    page_length -= shorten_by
    while len(in_text) > page_length:
        this_page_len = page_length
        closest_delim = (in_text.rfind(d, 1, this_page_len) for d in delims)
        if priority:
            closest_delim = next((x for x in closest_delim if x > 0), -1)
        else:
            closest_delim = max(closest_delim)
        closest_delim = closest_delim if closest_delim != -1 else this_page_len
        to_send = in_text[:closest_delim]
        if len(to_send.strip()) > 0:
            yield to_send
        in_text = in_text[closest_delim:]

    if len(in_text.strip()) > 0:
        yield in_text


def humanize_number(val: Union[int, float], override_locale=None) -> str:
    """
    Convert an int or float to a str with digit separators based on bot locale

    Parameters
    ----------
    val : Union[int, float]
        The int/float to be formatted.
    override_locale: Optional[str]
        A value to override bot's regional format.

    Returns
    -------
    str
        locale aware formatted number.
    """
    return format_decimal(val)


class Wss(commands.Cog):
    """Websocket stats go brrrrrrrrrrrrrrr """

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "socket_stats"):
            bot.socket_stats = Counter()

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        self.bot.socket_stats[msg.get("t", "UNKNOWN") or "UNDEFINED"] += 1

    @commands.is_owner()
    @commands.command(aliases=["wsstats"], hidden=True)
    @commands.bot_has_permissions(embed_links=True, external_emojis=True)
    async def socketstats(self, ctx, add_chart: bool = False):
        """WebSocket stats."""
        # delta = datetime.datetime.utcnow() - ctx.bot.uptime
        minutes = 86400 / 60
        total = sum(self.bot.socket_stats.values())
        cpm = total / minutes
        chart = None
        if not await self.bot.is_owner(ctx.author):
            add_chart = False
        if add_chart:
            chart = await self.bot.loop.run_in_executor(
                None, create_counter_chart, self.bot.socket_stats, "Socket events"
            )
        await WSStatsMenu(
            WSStatsPager(
                AsyncIter(
                    pagify(
                        tabulate(
                            [
                                (n, humanize_number(v), v / minutes)
                                for n, v in self.bot.socket_stats.most_common()
                            ],
                            headers=["Event", "Count", "APM"],
                            floatfmt=".2f" if add_chart else ".5f",
                        ),
                        page_length=2039,
                    )
                ),
                add_image=add_chart,
            ),
            header=f"{humanize_number(total)} socket events observed (<:apm:785823930287128596> {cpm:.2f}):",
            image=chart,
        ).start(ctx)
