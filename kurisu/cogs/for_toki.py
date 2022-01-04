import async_cse # literally amazing

import discord

from utils.kurisu import KurisuBot
from utils.context import KurisuContext
from discord.ext import commands

class ImSorry(commands.Cog):
    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.api_key = self.bot.get_config("config", "search", "google_api_key")
        self.client_session = async_cse.Search(self.api_key)


    def cog_unload(self) -> None:
        self.bot.loop.create_task(self.cleanup())
        super().cog_unload()


    async def cleanup(self) -> None:
        await self.client_session.close()


    @commands.command()
    async def google(self, ctx: KurisuContext, *, query: str):
        """Search stuff up on google"""
        results = await self.client_session.search(query, safesearch=True, image_search=False)
        if not results:
            return await ctx.send_error("No Results Found")

        await ctx.send(
            embed=discord.Embed(
                title=f"Query: {query}"
                description="\n".join([f"[{res.title}]({res.url})\n{res.description}\n\n" for res in results[:5]]),
                color=self.bot.ok_color
            ).set_footer(
                text=f"Requested by {ctx.author}" if ctx.author.id != 595493378062548994 else "ily <3",
                icon_url=ctx.author.display_avatar
            ).set_author(
                name=str(ctx.author),
                icon_url="https://staffordonline.org/wp-content/uploads/2019/01/Google.jpg"
            )
        )


def setup(bot: KurisuBot):
    bot.add_cog(ImSorry(bot))
