from __future__ import annotations

import asyncio
from typing import Optional, Coroutine, TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from kurisu import KurisuContext, Kurisu


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


async def clean_closeout(bot: Kurisu) -> None:
    """Utility function for a clean process exit"""
    for ext in tuple(bot.__extensions):
        bot.unload_extension(ext)
    for cog in tuple(bot.__cogs):
        bot.remove_cog(cog)
    for vc in bot.voice_clients:
        await vc.disconnect(force=True)

    if bot._session:
        await bot._session.close()
    if bot._db.connection:
        await bot._db.disconnect()
    if bot.ws and bot.ws.open:
        await bot.ws.close(2000)

    await bot.http.close()
    bot._ready.clear()
    exit(26)
