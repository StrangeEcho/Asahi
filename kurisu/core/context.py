from discord.ext import commands
import discord

from .kurisu import ConfigHandler, KurisuBot

config = ConfigHandler()


class KurisuContext(commands.Context):
    """Custom context providing helper embed methods"""

    bot: KurisuBot

    async def send_ok(self, content: str):
        await self.send(
            embed=discord.Embed(
                description=content, color=config.get("ok_color", "Core")
            )
        )

    async def send_info(self, content: str):
        await self.send(
            embed=discord.Embed(
                description=content, color=config.get("info_color", "Core")
            )
        )

    async def send_error(self, content: str):
        await self.send(
            embed=discord.Embed(
                description=content, color=config.get("error_color", "Core")
            )
        )
