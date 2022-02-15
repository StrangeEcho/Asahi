from __future__ import annotations

import asyncio
from typing import Optional, Coroutine, TYPE_CHECKING
from random import shuffle

import discord
import pomice
from discord.ui import MessageComponents, ActionRow, SelectMenu, SelectOption

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
) -> Optional[discord.Message]:
    """Confirmation prompt"""
    edit_embed = discord.Embed(title=prompt, color=ctx.bot.info_color)
    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(emoji="✅", custom_id="ACTION_CONFIRMED"),
            discord.ui.Button(
                emoji="❌",
            ),
        )
    )
    msg = await ctx.send(embed=edit_embed, components=components)

    def check(payload: discord.Interaction):
        if payload.message.id != msg.id:
            return False

        if payload.user.id != ctx.author.id:
            ctx.bot.loop.create_task(payload.response.send_message("You can't respond to this prompt!", ephemeral=True))
            return False
        else:
            return True

    try:
        payload = await ctx.bot.wait_for("component_interaction", check=check, timeout=15.0)
    except asyncio.TimeoutError:
        edit_embed.title = "Timed out."
        await msg.edit(embed=edit_embed, components=None)

    if payload.component.custom_id == "ACTION_CONFIRMED":
        edit_embed.title = confirm_str
        await msg.edit(embed=edit_embed, components=None)
        await action()
    else:
        edit_embed.title = cancelled_str
        await msg.edit(embed=edit_embed, components=None)


async def do_music(ctx: KurisuContext, query: str) -> Optional[discord.Message]:  # noqa c901
    """Handle Music Interaction"""

    player: Player = ctx.voice_client
    results = await player.get_tracks(query, ctx=ctx)
    dropdown_options = []

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

        else:
            for num, track in enumerate(results[:5], 1):
                dropdown_options.append(
                    SelectOption(label=track.title[:50], description=track.author[:50], value=num - 1)
                )
            components = MessageComponents(
                ActionRow(
                    SelectMenu(options=dropdown_options, placeholder=f"{len(dropdown_options)} Options Available.")
                )
            )
            embed = discord.Embed(description="Select Your Song Here!", color=ctx.bot.info_color).set_footer(
                icon_url=ctx.author.display_avatar.url, text=ctx.author
            )

            msg = await ctx.send(embed=embed, components=components)

            def check(p: discord.Interaction):
                return p.user.id == ctx.author.id and p.message.id == msg.id

            try:
                payload = await ctx.bot.wait_for("component_interaction", check=check, timeout=30)
            except asyncio.TimeoutError:
                embed.description = "Timed Out!"
                await msg.edit(embed=embed, components=None)
                return

            ttp = results[int(payload.values[0])]
            embed.description = f"{'Enqueued' if player.is_playing else 'Now playing'} [{ttp.title}]({ttp.uri})"
            await msg.edit(embed=embed, components=None)
            if not player.current:
                await player.play(ttp)
            else:
                player.queue.append(ttp)
