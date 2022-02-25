from __future__ import annotations

from typing import Optional, Coroutine, TYPE_CHECKING
from random import shuffle

import disnake
import pomice

if TYPE_CHECKING:
    from kurisu import KurisuContext


class Player(pomice.Player):
    """Subclass of Pomice Player, adding a queue implementation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._queue: list[pomice.Track] = []

    @property
    def queue(self) -> list[pomice.Track]:
        return self._queue

    def shuffle_queue(self) -> None:
        shuffle(self.queue)


async def confirm_prompt(
    ctx: KurisuContext,
    action: Coroutine,
    *,
    prompt: str = "Are you sure you want to do this?",
    confirm_str: str = "Action Confirmed",
    cancelled_str: str = "Action Cancelled",
) -> Optional[disnake.Message]:
    """Confirmation prompt"""

    # TODO: view


async def do_music(ctx: KurisuContext, query: str) -> Optional[disnake.Message]:  # noqa c901
    """Handle Music Interaction"""

    player: Player = ctx.voice_client
    results = await player.get_tracks(query, ctx=ctx)

    if not results:
        return await ctx.send_error(f"No results found for the term `{query}`")

    if isinstance(results, pomice.Playlist):
        for track in results.tracks:
            player.queue.append(track)
        await ctx.send_ok(f"Added {results.track_count} tracks to the queue")
        if not player.current:
            ttp = player.queue.pop(0)
            await player.play(ttp)
            await ctx.send_info(f"Now playing [{ttp.title}]({ttp.uri}) by {ttp.author}")
        return

    if isinstance(results, list):
        if len(results) == 1:
            ttp = results[0]
            if player.current:
                player.queue.append(ttp)
            else:
                await player.play(ttp)
            await ctx.send_info(f"Now playing [{ttp.title}]({ttp.uri}) by {ttp.author}")
            return

        # TODO: view
