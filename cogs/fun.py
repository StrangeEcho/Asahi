import discord
import aiohttp # requests are gey. dey blocking
import nekos

from discord.ext import commands

npa = ' '

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command() #copy and pasting time bois
    @commands.bot_has_permissions(embed_links = True)
    async def pat(self, ctx, *, args=npa): #this is a shitty way to do it but im noob 
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/api/sfw/pat') as r:

                pat = (await r.json())['url']

                embed = discord.Embed(
                    description=f'{ctx.author.mention} pats {args}',
                    color=0xffb6c1
                )
                embed.set_image(url=pat)
                await ctx.send(embed=embed)
    
    @commands.command() 
    @commands.bot_has_permissions(embed_links = True)
    async def kiss(self, ctx, *, args=npa): 
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/api/sfw/kiss') as r:

                kiss = (await r.json())['url']

                embed = discord.Embed(
                    description=f'{ctx.author.mention} kisses {args}',
                    color=0xffb6c1
                )
                embed.set_footer(text='owo')
                embed.set_image(url=kiss)
                await ctx.send(embed=embed)
    
    @commands.command() 
    @commands.bot_has_permissions(embed_links = True)
    async def hug(self, ctx, *, args=npa): 
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/api/sfw/hug') as r:

                hug = (await r.json())['url']

                embed = discord.Embed(
                    description=f'{ctx.author.mention} hugs {args}',
                    color=0xffb6c1
                )
                embed.set_image(url=hug)
                await ctx.send(embed=embed)

    @commands.command()
    async def cuddle(self, ctx, *, args=npa):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/api/sfw/cuddle') as r:

                cuddle = (await r.json())['url']

                embed = discord.Embed(
                    description=f'{ctx.author.mention} cuddles {args}',
                    color=0xffb6c1
                )
                embed.set_image(url=cuddle)
                await ctx.send(embed=embed)

    @commands.command()
    async def lick(self, ctx, *, args=npa):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/sfw/lick') as r:
                
                lick = (await r.json())['url']

                embed = discord.Embed(
                    description=f'{ctx.author.mention} licks {args}',
                    color=0xffb6c1
                )
                embed.set_image(url=lick)
                await ctx.send(embed=embed)

    @commands.command()
    async def bully(self, ctx, *, args=npa):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/api/sfw/bully') as r:

                bully = (await r.json())['url']

                embed = discord.Embed(
                    description=f'{ctx.author.mention} bullies {args}',
                    color=0xffb6c1
                )
                embed.set_image(url=bully)
                await ctx.send(embed=embed)

    @commands.command()
    async def poke(self, ctx, *, args=npa):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/api/sfw/poke') as r:

                poke = (await r.json())['url']

                embed = discord.Embed(
                    description=f'{ctx.author.mention} pokes {args}',
                    color=0xffb6c1
                )
                embed.set_image(url=poke)
                await ctx.send(embed=embed)
    
    @commands.command()
    async def baka(self, ctx, *, args=npa):
        
        baka = nekos.img('baka')

        embed = discord.Embed(color=0xffb6c1)
        embed.description = f'{ctx.author.mention} calls {args} a baka'
        embed.set_image(url=baka)
        await ctx.send(embed=embed)  

    @commands.command()
    async def slap(self, ctx, *, args):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/api/sfw/slap') as r:
                
                slap = (await r.json())['url']

                embed = discord.Embed(
                    description=f'{ctx.author.mention} slaps {args}',
                    color=0xffb6c1
                )
                embed.set_image(url=slap)
                await ctx.send(embed=embed)

    @commands.command()
    async def tickle(self, ctx, *, args=npa):
        
        tickle = nekos.img('tickle')

        embed = discord.Embed(color=0xffb6c1)
        embed.description = f'{ctx.author.mention} tickles {args}'
        embed.set_image(url=tickle)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def smug(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://waifu.pics/api/sfw/smug') as r:

                smug = (await r.json())['url']

                embed = discord.Embed(
                    description=f'{ctx.author.mention} has a smug look',
                    color=0xffb6c1
                )
                embed.set_image(url=smug)
                await ctx.send(embed=embed)
    
    @commands.command()
    async def feed(self, ctx, *, args=npa):
        
        feed = nekos.img('feed')

        embed = discord.Embed(color=0xffb6c1)
        embed.description = f'{ctx.author.mention} feeds {args}'
        embed.set_image(url=feed)
        embed.set_footer(text='Eat Up!')
        await ctx.send(embed=embed) 

            


def setup(bot):
    bot.add_cog(Fun(bot))