from discord.ext import commands
import discord
import toml


def get_color(color: str):
    if not color in ["ok", "error"]:
        return discord.Color.default()

    t = toml.load("configoptions.toml")
    if color == "ok":
        return int(str(t["options"]["ok_color"]).replace("#", "0x"), base=16)

    if color == "error":
        return int(str(t["options"]["error_color"]).replace("#", "0x"), base=16)


class KurisuContext(commands.Context):
    """Custom Context"""

    async def send_ok(self, content: str):
        await self.send(embed=discord.Embed(description=content, color=get_color("ok")))

    async def send_error(self, content: str):
        await self.send(embed=discord.Embed(description=content, color=get_color("error")))
