from __future__ import annotations

import asyncio
from typing import Optional, Coroutine, TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from kurisu import KurisuContext


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
        if payload.component.custom_id == "ACTION_CONFIRMED":
            edit_embed.title = confirm_str
            await msg.edit(embed=edit_embed, components=None)
            await action()
        else:
            edit_embed.title = cancelled_str
            await msg.edit(embed=edit_embed, components=None)
    except asyncio.TimeoutError:
        edit_embed.title = "Timed out."
        await msg.edit(embed=edit_embed, components=None)
