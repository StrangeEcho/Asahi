import discord #complete re-write using the commands.is_owner() decorator as well as cleaning up unneeded stuff
import config

from discord.ext import commands

class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        embed = discord.Embed(description='👋Logging Out!', color=0xffb6c1)
        await ctx.send(embed=embed)
        await self.bot.logout()
        await self.bot.close()
    
    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog):
        try:
            self.bot.load_extension(cog)
            await ctx.send(':ok_hand: Cog Loaded')
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
    
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog):
        try:
            self.bot.unload_extension(cog)
            await ctx.send(':ok_hand: Cog Unloaded')
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog):
        try:
            self.bot.reload_extension(cog)
            await ctx.send(':ok_hand: Cog Reloaded')
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')

    @commands.command() #ill probably make these 2 commands public soon? say/embed
    @commands.is_owner()
    async def say(self, ctx, *, msg):
        await ctx.message.delete()
        await ctx.send(msg)
    
    @commands.command()
    @commands.is_owner()
    async def embed(self, ctx, *, msg):
        embed = discord.Embed(description=msg, color=0xffb6c1)
        await ctx.send(embed=embed)
    
    @commands.group()
    @commands.is_owner()
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f'There are currently a total of {len(config.BLACKLIST)} blacklisted IDS',
                description=config.BLACKLIST,
                color=0xffb6c1
            )
            await ctx.send(embed=embed)
    
    @blacklist.command(name='add')
    @commands.is_owner()
    async def blacklist_add(self, ctx, member : discord.Member):
        config.BLACKLIST.append(member.id)
        embed = discord.Embed(
            title=f'User Blacklisted!!!',
            description=f'`{member.name}` has been sucessfully added to the blacklist.',
            color=0xffb6c1
        )
        embed.set_footer(text=f'There is now a total of {len(config.BLACKLIST)} blacklisted users')
        await ctx.send(embed=embed)
    
    @blacklist.command(name='remove')
    @commands.is_owner()
    async def blacklist_remove(self, ctx, member = discord.Member):
        config.BLACKLIST.remove(member.id)
        embed = discord.Embed(
            title='User Unblacklisted',
            description=f'`{member.name}` has been sucessfully removed to the blacklist.',
            color=0xffb6c1
        )
        embed.set_footer(text=f'There is now a total of {len(config.BLACKLIST)} blacklisted users')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Owner(bot))
    