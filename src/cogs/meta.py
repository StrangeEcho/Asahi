import discord
from discord.ext import commands
from core.context import AsahiContext
from core.bot import Asahi
from core.database import PrefixHandler

class Meta(commands.Cog):
    def __init__(self, bot: Asahi):
        self.bot = bot
        self.prefix_handler = PrefixHandler(self.bot) 
    
    @commands.command()
    async def ping(self, ctx: AsahiContext):
        """Obligitory command"""
        msg = await ctx.send("Measuring now...")
        await msg.edit(
            embed=discord.Embed(
                description=f"Ping for {self.bot.user}",
                color=self.bot.info_color
            ).add_field(
                name="WebSocket Latency",
                value=f"{round(self.bot.latency * 1000)}ms"
            ).add_field(
                name="Message",
                value=f"{round((msg.created_at - ctx.message.created_at).total_seconds() * 1000)}ms"
            )
        )

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx: AsahiContext, prefix: str = None):
        """Set a custom prefix for the guild"""
        if not prefix:
            return await ctx.send_info(f"Prefix for this guild {self.bot.prefixes.get(ctx.guild.id) or self.bot.config.get('prefix')}")
        
        await self.prefix_handler.add_prefix(prefix, ctx.guild.id)
        await ctx.send_ok(f"Sucessfully changed this guild's prefix to `{prefix}`")

async def setup(bot: Asahi):
    await bot.add_cog(Meta(bot))