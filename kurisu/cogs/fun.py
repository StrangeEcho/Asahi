from io import BytesIO
from random import choice, randint

from discord.ext import commands, vbu
from utils.context import KurisuContext
from utils.kurisu import KurisuBot
from utils.helpers import get_ud_results
import aiohttp
import discord


class Fun(commands.Cog):
    """Many different fun styled commands for your enterainment."""

    def __init__(self, bot: KurisuBot):
        self.bot = bot


    @commands.command(name="8ball")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _8ball(self, ctx: KurisuContext, *, question):
        """Ask the mystical 8 ball anything."""
        answers = [
            "As I see it, yes.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "It is certain.",
            "It is decidedly so.",
            "Most likely.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Outlook good.",
            "Reply hazy, try again.",
            "Signs point to yes.",
            "Very doubtful.",
            "Without a doubt.",
            "Yes.",
            "No",
            "Yes – definitely.",
            "You may rely on it.",
        ]
        await ctx.send(
            embed=discord.Embed(
                title="🎱The Magic 8ball🎱",
                description=f"Question: `{question}`\nAnswer: `{choice(answers)}`",
                color=self.bot.ok_color,
            ).set_footer(text=f"Question asked by {ctx.author}")
        )


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def compliment(
            self, ctx: KurisuContext, member: discord.Member = None
    ):
        """Compliment someone or yourself"""
        if member is None:
            member = ctx.author

        compliments = [
            "Your positivity is infectious.",
            "You should be so proud of yourself.",
            "You’re amazing!",
            "You’re a true gift to the people in your life.",
            "You’re an incredible friend.",
            "I really appreciate everything that you do.",
            "You inspire me to be a better person.",
            "Your passion always motivates me.",
            "Your smile makes me smile.",
            "Thank you for being such a great person.",
            "The way you carry yourself is truly admirable.",
            "You are such a good listener.",
            "You have a remarkable sense of humor.",
            "Thanks for being you!",
            "You set a great example for everyone around you.",
            "I love your perspective on life.",
            "Being around you makes everything better.",
            "You always know the right thing to say.",
            "The world would be a better place if more people were like you!",
            "You are one of a kind.",
            "You make me want to be the best version of myself.",
            "You always have the best ideas.",
            "I’m so lucky to have you in my life.",
            "Your capacity for generosity knows no bounds.",
            "I wish I were more like you.",
            "You are so strong.",
            "I’ve never met someone as kind as you are.",
            "You have such a great heart.",
            "Simply knowing you has made me a better person.",
            "You are beautiful inside and out.",
        ]
        await ctx.send(
            embed=discord.Embed(
                description=f"{member.mention} {choice(compliments)}",
                color=self.bot.ok_color,
            ).set_footer(text=f"Compliment from {ctx.author}")
        )


    @commands.command(aliases=["rng"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def randomnumber(self, ctx, int1: int, int2: int):
        """Generate a random number between the two given fields"""
        try:
            await ctx.send(
                embed=discord.Embed(
                    title="Your number has been chosen",
                    description=f"Your number: {randint(int1, int2)}",
                    color=self.bot.ok_color,
                )
            )
        except ValueError:
            await ctx.send(
                embed=discord.Embed(
                    description="Please input a number that follows base 10 numeric system",
                    color=self.bot.error_color,
                )
            )


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def owoify(self, ctx: KurisuContext, *, txt):
        """Owoify some text"""
        if len(txt) > 200:
            await ctx.send(
                embed=discord.Embed(
                    description="Text cannot be over 200",
                    color=self.bot.error_color,
                )
            )
        else:
            async with self.bot.session.get(
                    f"https://nekos.life/api/v2/owoify?text={txt}"
            ) as resp:
                await ctx.send(
                    embed=discord.Embed(
                        title="OwO here you go.",
                        description=" ".join((await resp.json())["owo"]),
                        color=self.bot.ok_color,
                    )
                )


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True, attach_files=True)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def osu(self, ctx: KurisuContext, *, user):
        """Get osu information about someone."""
        try:
            async with self.bot.session.get(
                    "https://api.martinebot.com/v1/imagesgen/osuprofile",
                    params={
                        "player_username": user,
                    },
                    raise_for_status=True,
            ) as r:
                pic = BytesIO(await r.read())
        except aiohttp.ClientResponseError as e:
            emb = discord.Embed(
                description=f"Cannot contact the api due to error: [{e.status}] {e.message}",
                color=self.bot.ok_color,
            )
            return await ctx.send(embed=emb)
        e = discord.Embed(
            title=f"Here's the osu profile for {user}", color=self.bot.ok_color
        )
        if isinstance(pic, BytesIO):
            e.set_image(url="attachment://osu.png")
        elif isinstance(pic, str):
            e.set_footer(text="Api is currently down.")

        await ctx.send(
            embed=e,
            file=discord.File(pic, filename="osu.png") if pic else None,
        )
        if isinstance(pic, BytesIO):
            pic.close()


    @commands.command(aliases=["aq"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def animequote(self, ctx: KurisuContext):
        """Recieve an anime quote from the AnimeChan API"""
        async with self.bot.session.get(
                "https://animechan.vercel.app/api/random"
        ) as resp:
            if resp.status == 200:
                quote = (await resp.json())["quote"]
                char = (await resp.json())["character"]
                anime = (await resp.json())["anime"]
                await ctx.send(
                    embed=discord.Embed(
                        description=f"{quote}\n~{char}",
                        color=self.bot.ok_color,
                    ).set_footer(text=f"Anime: {anime}")
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        description=f"API threw a {resp.status}. Please try again later.",
                        color=self.bot.error_color,
                    )
                )


    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def img(self, ctx: KurisuContext):
        """Return sfw images from the waifu.im api"""
        await ctx.send_help(ctx.command)


    @img.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def maid(self, ctx: KurisuContext):
        """maids go brrr"""
        async with self.bot.session.get(
                "https://api.waifu.im/sfw/maid"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(
                    url=(await resp.json())["images"][0]["url"]
                )
            )


    @img.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def waifu(self, ctx: KurisuContext):
        """waifu"""
        async with self.bot.session.get(
                "https://api.waifu.im/sfw/waifu"
        ) as resp:
            await ctx.send(
                embed=discord.Embed(color=self.bot.ok_color).set_image(
                    url=(await resp.json())["images"][0]["url"]
                )
            )


    @commands.command()
    @commands.cooldown(1, 4.5, commands.BucketType.user)
    async def ud(self, ctx: KurisuContext, *, term: str):
        """Query the Urban Dictionary API with a term"""
        results = await get_ud_results(term)
        embeds: list[discord.Embed] = []

        for i in results:
            embeds.append(
                discord.Embed(
                    title=f"Definition for {term}",
                    description=f"Definition: {i['definition']}",
                    color=self.bot.ok_color
                ).set_footer(
                    text=f"👍: {i['thumbs_up']}"
                ).add_field(
                    name="Author",
                    value=i["author"] or "No Author "
                )
            )

        await vbu.Paginator(data=embeds, per_page=1).start(ctx)




def setup(bot):
    bot.add_cog(Fun(bot))
