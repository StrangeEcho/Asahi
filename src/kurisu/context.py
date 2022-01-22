from typing import Any

from discord.ext import commands
from helpers.confighandler import Config
from exts.functions import color_convert
import discord

class KurisuContext(commands.Context):
    """Subclass for added functionality"""
    config = Config()

    async def send_info(self, content: Any):
        """Send INFO embed"""
        await super().send(
            embed=discord.Embed(
                description=str(content),
                color=color_convert(self.config.get("info_color"))
            ).set_footer(
                text=str(self.author),
                icon_url=self.author.display_avatar.url
            )
        )


    async def send_ok(self, content: Any):
        """Send OK embed"""
        await super().send(
            embed=discord.Embed(
                description=str(content),
                color=color_convert(self.config.get("ok_color"))
            ).set_footer(
                text=str(self.author),
                icon_url=self.author.display_avatar.url
            )
        )


    async def send_error(self, content: Any):
        """Send ERROR embed"""
        await super().send(
            embed=discord.Embed(
                description=str(content),
                color=color_convert(self.config.get("error_color"))
            ).set_footer(
                text=str(self.author),
                icon_url=self.author.display_avatar.url
            )
        )