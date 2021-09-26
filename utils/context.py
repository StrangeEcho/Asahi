from discord.ext import commands
import discord
import toml


def get_color(color: str):
    if not color in ["ok_color", "error_color"]:
        return discord.Color.default()

    t = toml.load("configoptions.toml")
    return int(str(t["options"][color]).replace("#", "0x"), base=16)


class KurisuContext(commands.Context):
    """Custom Context"""

    async def send_ok(self, content: str):
        await self.send(embed=discord.Embed(description=content, color=get_color("ok_color")))

    async def send_error(self, content: str):
        await self.send(embed=discord.Embed(description=content, color=get_color("error_color")))
