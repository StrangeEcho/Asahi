import discord

from utils import misc

from discord.ext import commands

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member : discord.Member, reason=None):
        if await misc.check_hierachy(ctx, member):
            return

        try:
            if reason is None:
                await member.kick(reason=f"{reason} - {ctx.author.name}")
                await ctx.send(f"{member.name} was kicked for {reason}")
        except Exception as e:
            await ctx.send(e)

def setup(bot):
    bot.add_cog(Moderation(bot))
