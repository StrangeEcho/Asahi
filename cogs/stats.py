import discord
import config
import platform

from discord.ext import commands
from EZPaginator import Paginator 

class Stats(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['botstats', 'info'])
    @commands.bot_has_permissions(embed_links = True)
    async def stats(self, ctx):
        embed = discord.Embed(title='Himeji Stats', color=0xffb6c1)
        embed.set_author(name='Basics')
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name='Mention:', value=self.bot.user.mention, inline=True)
        embed.add_field(name='Owner:', value='Tylerr#6979', inline=True)
        embed.add_field(name='Prefix:', value=config.BOT_PREFIX, inline=True)
        embed.add_field(name='Latency:', value=f'{self.bot.latency * 1000} Milliseconds', inline=True)
        embed.add_field(
            name='Using Discord.py Version:',
            value=f'[{discord.__version__}](https://discordpy.readthedocs.io/en/latest/)',
            inline=True
        )
        embed.add_field(
            name=' Using Python Version:',
            value=f'[{platform.python_version()}](https://www.python.org)',
            inline=True
        )
        embed.set_footer(text=f'Information Requested By {ctx.author.display_name}')

        text_channels = 0
        voice_channels = 0
        for channel in self.bot.get_all_channels():
            if isinstance(channel, discord.TextChannel):
                text_channels += 1
            if isinstance(channel, discord.VoiceChannel):
                voice_channels += 1
        embed2 = discord.Embed(title='Himeji Stats Stats', color=0xffb6c1)
        embed2.set_author(name='Presence')
        embed2.set_thumbnail(url=self.bot.user.avatar_url)
        embed2.add_field(name='Cached Guilds:', value=(len(self.bot.guilds)), inline=True)
        embed2.add_field(name='Total Text Channels:', value=text_channels, inline=True)
        embed2.add_field(name='Total Voice Channels:', value=voice_channels, inline=True)
        embed2.add_field(name='Cached Users:', value=(len(self.bot.users)), inline=True)
        embed2.set_footer(icon_url=ctx.author.avatar_url, text=f'Information Requested By {ctx.author.display_name}\nProcess Stats coming soon')
        
        embeds = [embed, embed2]
        
        msg = await ctx.send(embed=embed)
        page = Paginator(self.bot, msg, embeds=embeds)
        await page.start()


def setup(bot):
    bot.add_cog(Stats(bot))