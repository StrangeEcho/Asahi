from io import BytesIO
import asyncio

from discord.ext import commands
import discord

from utils.classes import KurisuBot

snipe = {
    "id": None,
    "content": None,
    "author": None,
    "attachment": None,
    "guild": None,
    "channel": None,
}

edit_snipe = {"author": None, "content": None, "guild": None, "channel": None}


class Snipe(commands.Cog):
    """Some snipe related commands xd"""

    def __init__(self, bot):
        self.bot = bot

    def __init__(self, bot: KurisuBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if message.author.bot:
            return

        global snipe

        snipe["id"] = message.id
        snipe["author"] = message.author
        snipe["content"] = message.content
        snipe["guild"] = message.guild
        snipe["channel"] = message.channel

        if message.attachments:
            snipe["attachment"] = message.attachments[0].proxy_url

        await asyncio.sleep(60)

        if message.id == snipe["id"]:
            snipe["id"] = None
            snipe["author"] = None
            snipe["content"] = None
            snipe["attachment"] = None
            snipe["guild"] = None
            snipe["channel"] = None

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        global edit_snipe

        if before.author.bot:
            return

        edit_snipe["author"] = before.author
        edit_snipe["content"] = before.content
        edit_snipe["guild"] = before.guild
        edit_snipe["channel"] = before.channel

        await asyncio.sleep(60)

        if before.id == after.id:
            edit_snipe["author"] = None
            edit_snipe["content"] = None
            edit_snipe["guild"] = None
            edit_snipe["channel"] = None

    @commands.command(aliases=["imagesnipe"])
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def snipe(self, ctx: commands.Context):
        """Snipe the last deleted message, works with images"""
        global snipe

        if (
            snipe["guild"] != ctx.guild
            or snipe["channel"] != ctx.channel
            or snipe["content"] == None
        ):
            emb = discord.Embed(
                color=self.bot.ok_color,
                description="There's nothing to snipe!",
            )
            return await ctx.send(embed=emb, delete_after=5)

        embed = discord.Embed(description=str(snipe["content"]), colour=0xFFCDCD)
        embed.set_author(
            name="{0.name}#{0.discriminator}".format(snipe["author"]),
            icon_url=snipe["author"].avatar.url,
        )
        embed.set_footer(
            text=f"sniped by {ctx.author.name}#{ctx.author.discriminator}",
            icon_url=ctx.author.avatar.url,
        )
        if snipe["attachment"] is not None:
            async with self.bot.session.get(snipe["attachment"]) as r:
                file = BytesIO(await r.read())
            embed.set_image(url="attachment://snipe.jpg")
            await ctx.send(embed=embed, file=discord.File(file, filename="snipe.jpg"))
            snipe["attachment"] = None
        else:
            await ctx.send(embed=embed)
            snipe["attachment"] = None

    @commands.command(aliases=["esnipe"])
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def editsnipe(self, ctx: commands.Context):
        """Sneaky Sneaky snipe the edited message"""

        if (
            edit_snipe["guild"] != ctx.guild
            or edit_snipe["channel"] != ctx.channel
            or edit_snipe["content"] == None
        ):
            emb = discord.Embed(
                color=self.bot.ok_color,
                description="There's nothing to esnipe!",
            )
            return await ctx.send(embed=emb, delete_after=5)

        embed = discord.Embed(description=str(edit_snipe["content"]), colour=0xFFCDCD)
        embed.set_footer(
            text=f"sniped by {ctx.author.name}#{ctx.author.discriminator}",
            icon_url=ctx.author.avatar.url,
        )
        embed.set_author(
            name="{0.name}#{0.discriminator}".format(edit_snipe["author"]),
            icon_url=edit_snipe["author"].avatar.url,
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Snipe(bot))
