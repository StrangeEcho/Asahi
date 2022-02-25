import disnake
import async_cse
from disnake.ext import commands, vbu
from kurisu import Kurisu, KurisuContext


class Searches(commands.Cog):
    def __init__(self, bot: Kurisu):
        self.bot = bot
        self.cse_session = async_cse.Search(self.bot.config.get("google_api_key"))

    def cog_unload(self):
        self.bot.loop.create_task(self.cse_session.close())
        super().cog_unload()

    @commands.command()
    @commands.cooldown(1, 3.5, commands.BucketType.user)
    async def google(self, ctx: KurisuContext, *, query: str):
        try:
            results: list[async_cse.Result] = await self.cse_session.search(query)
        except async_cse.NoResults:
            return await ctx.send_error("No results found for that query.")

        await ctx.send(
            embed=disnake.Embed(
                description="\n".join([f"[{res.title}]({res.url})\n{res.description}\n\n" for res in results[:5]]),
                color=disnake.Color.random(),
            )
            .set_footer(text=f"Requested by {ctx.author}")
            .set_author(name=ctx.author, icon_url="https://staffordonline.org/wp-content/uploads/2019/01/Google.jpg")
        )

    @commands.command(aliases=["image"])
    @commands.cooldown(1, 3.5, commands.BucketType.user)
    async def imagesearch(self, ctx: KurisuContext, *, query):
        """Image search"""
        try:
            results = await self.cse_session.search(query)
        except async_cse.NoResults:
            return await ctx.send_error("No images found for that query.")

        embeds = []
        for i in results[:7]:
            embeds.append(disnake.Embed(color=disnake.Color.random()).set_image(url=i.image_url))
        await vbu.Paginator(embeds, per_page=1).start(ctx)


def setup(bot: Kurisu):
    bot.add_cog(Searches(bot))
