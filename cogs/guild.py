import discord

from discord.ext import commands

class GuildManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def servername(self, ctx, *, name):
        """Change the servers name"""
        await ctx.guild.edit(name=name)
        await ctx.send(f"Successfully changed this severs name to **{name}**")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def set_afk(self, ctx, channel: discord.VoiceChannel):
        """Set the servers afk voice channel **THIS IS CASE SENSATIVE**"""
        await ctx.guild.edit(afk_channel=channel)
        await ctx.send(f"Successfully set this servers afk channel to {channel}")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def setafktimeout(self, ctx, time: int):
        """Set the timeout time for going to the afk in seconds"""
        try:
            await ctx.guild.edit(afk_timeout=time)
            await ctx.send(f"Successfully set the afk timeout time to {time} seconds")
        except Exception as e:
            await ctx.send(e)


def setup(bot):
    bot.add_cog(GuildCommands(bot))
