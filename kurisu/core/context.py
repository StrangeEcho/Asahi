from typing import Literal
import tomllib

from discord.ext import commands
import discord


def get_color(color: Literal["ok_color", "error_color", "info_color"]) -> int:
    with open("./kurisu/core/config.toml") as f:
        config = tomllib.load(f.read())
    try:
        return config["Core"][color]
    except KeyError:
        return discord.Color.default()


class KurisuContext(commands.Context):
    """Custom Context"""

    async def send_ok(self, content: str):
        await self.send(
            embed=discord.Embed(
                description=content, color=get_color("ok_color")
            )
        )

    async def send_info(self, content: str):
        await self.send(
            embed=discord.Embed(description=content, color=get_color())
        )

    async def send_error(self, content: str):
        await self.send(
            embed=discord.Embed(
                description=content, color=get_color("error_color")
            )
        )
