from typing import Union

import discord

from discord.ext import commands
from discord.utils import get
from utils.classes import MemberID
from utils.funcs import check_hierachy


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def ban(self, ctx: commands.Context, member: MemberID, *, reason: str = None):
        """Ban users from the current server"""

        if reason is None:
            reason = "No reason passed"

        await ctx.guild.ban(member, reason=f"{reason} | Moderator: {ctx.author}")
        await ctx.send(f"Successfully banned {member} from {ctx.guild.name}")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def kick(
        self, ctx: commands.Context, member: discord.Member, *, reason: str = None
    ):
        """Kick members from the current server"""
        if await check_hierachy(ctx, member):
            return

        if reason is None:
            reason = "No reason passed"

        await member.kick(reason=f"{reason} | Moderator: {ctx.author}")
        await ctx.send(f"Successfully kicked `{member}` from `{ctx.guild.name}`")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def unban(self, ctx: commands.Context, id: int):
        """Unban someone from the current server"""
        if id is None:
            await ctx.send("Please pass in a ID for me to unban!")
        else:
            try:
                user = await self.bot.fetch_user(id)
                await ctx.guild.unban(user)
                await ctx.send(f"Sucessfully unbanned `{user}`")
            except discord.HTTPException:
                await ctx.send(
                    f"Failed trying to unban `{user}`. This user is probably already unbanned."
                )

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def mute(
        self, ctx: commands.Context, member: discord.Member, *, reason: str = None
    ):
        if await check_hierachy(ctx, member):
            return
        if reason is None:
            reason = "No reason added"
        if not get(ctx.guild.roles, name="Himeji-Mute"):
            role = await ctx.guild.create_role(
                name="Himeji-Mute", permissions=discord.Permissions(send_messages=False)
            )
            for chan in ctx.guild.text_channels:
                await chan.set_permissions(role, send_messages=False)
            await ctx.send("My mute role was not setup so I went ahead and made one.")
            await member.add_roles(role)
            await ctx.send(f"{member} is now muted for {reason}")
        elif get(ctx.guild.roles, name="Himeji-Mute"):
            await member.add_roles(get(ctx.guild.roles, name="Himeji-Mute"))
            await ctx.send(f"`{member}` is now muted for `{reason}`")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        if not get(ctx.guild.roles, name="Himeji-Mute") in member.roles:
            await ctx.send(f"{member} is not muted.")
        elif get(ctx.guild.roles, name="Himeji-Mute") in member.roles:
            await member.remove_roles(get(ctx.guild.roles, name="Himeji-Mute"))
            await ctx.send(f"`{member}` is now unmuted")


def setup(bot):
    bot.add_cog(Moderation(bot))
