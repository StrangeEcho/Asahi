import asyncio

import discord
from discord.ext import commands


class OnEdit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timeout = 60

    async def edit_process_commands(self, message: discord.Message):
        """Same as Airi's method (Airi.process_commands), but dont dispatch message_without_command."""
        if not message.author.bot:
            ctx = await self.bot.get_context(message)
            await self.bot.invoke(ctx)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.edited_at:
            return
        if before.content == after.content:
            return
        if (after.edited_at - after.created_at).total_seconds() > self.timeout:
            return
        await self.edit_process_commands(after)


def setup(bot):
    bot.add_cog(OnEdit(bot))
