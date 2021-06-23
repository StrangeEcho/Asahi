from discord.ext import commands
import discord

from utils.classes import HimejiBot

np = ""


class Actions(commands.Cog):
    def __init__(self, bot: HimejiBot):
        self.bot = bot

    @commands.command()
    async def hug(self, ctx: commands.Context, *, target=np):
        async with self.bot.session.get(url="https://api.waifu.pics/sfw/hug") as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} hugs {target}",
                    color=ctx.author.top_role.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )

    @commands.command()
    async def kiss(self, ctx: commands.Context, *, target=np):
        async with self.bot.session.get(url="https://api.waifu.pics/sfw/hug") as resp:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} kisses {target}",
                    color=ctx.author.top_role.color or self.bot.ok_color,
                ).set_image(url=(await resp.json())["url"])
            )

    @commands.command()
    async def pat(self, ctx: commands.Context, *, target=np):
        async with self.bot.session.get(url="https://api.waifu.pics/sfw/pat") as resp:
            await ctx.send(embed=discord.Embed(
                description=f"{ctx.author.mention} pats {target}",
                color=ctx.author.top_role or self.bot.ok_color
            ).set_image(url=(await resp.json())["url"])
        )

    @commands.command()
    async def cuddle(self, ctx: commands.Context, *, target=np):
        async with self.bot.session.get(url="https://api.waifu.pics/sfw/cuddle") as resp:
            await ctx.send(embed=discord.Embed(
                description=f"{ctx.author.mention} cuddles {target}",
                color=ctx.author.top_role.color or self.bot.ok_color
            ).set_image(url=(await resp.json())["url"])
        )

    @commands.command()
    async def lick(self, ctx: commands.Context, *, target=np):
        async with self.bot.session.get("https://api.waifu.pics/sfw/lick") as resp:
            await ctx.send(embed=discord.Embed(
                description=f"{ctx.author.mention} licks {target}",
                color=ctx.author.top_role.color or self.bot.ok_color
            ).set_image(url=(await resp.json())["url"])
        )



def setup(bot):
    bot.add_cog(Actions(bot))
