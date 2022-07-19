from typing import Union

from discord.ext import commands
import discord

from core import Asahi, AsahiContext, MuteHandler, WarningHandler


class Moderation(commands.Cog):
    """Basic Moderation Commands"""

    def __init__(self, bot: Asahi):
        self.bot = bot
        self.mute_handler = MuteHandler(self.bot)
        self.warn_handler = WarningHandler(self.bot)

    def owner_cooldown_bypass(message: discord.Message) -> commands.Cooldown:
        """Shortens cooldown for the guild owner"""
        if message.author == message.guild.owner:
            return commands.Cooldown(1, 1.5)
        else:
            return commands.Cooldown(1, 5)

    async def check_hierachy(self, ctx: AsahiContext, target: discord.Member) -> Union[bool, discord.Message]:
        if ctx.me.top_role.position < target.top_role.position:
            return await ctx.send_error("Cant do this action because the target is higher on the role hierachy than me")
        if ctx.author == ctx.guild.owner:
            return False
        if ctx.author.top_role.position < target.top_role.position:
            return await ctx.send_error("Cant do this action because the target has a higher role than you")
        if ctx.author == target:
            return await ctx.send_error("You cant perform this action on yourself")

    @commands.command()
    @commands.dynamic_cooldown(owner_cooldown_bypass, type=commands.BucketType.user)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx: AsahiContext, member: discord.Member, *, reason: str = None):
        """Kick a member from this guild"""
        if await self.check_hierachy(ctx, member):
            return
        reason = reason or "No Reason Provided"

        await member.kick(reason=f"{reason} - {ctx.author}")
        await ctx.message.add_reaction("👍")

    @commands.command()
    @commands.dynamic_cooldown(owner_cooldown_bypass, type=commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx: AsahiContext, member: Union[discord.Member, int], *, reason: str = None):
        """Bans a member from this guild"""
        reason = reason or "No Reason Provided"

        if isinstance(member, discord.Member):
            if await self.check_hierachy(ctx, member):
                return
            await member.ban(reason=f"{reason} - {ctx.author}")
            await ctx.message.add_reaction("👍")
        if isinstance(member, int):
            try:
                await ctx.guild.ban(discord.Object(member), reason=f"{reason} - {ctx.author}")
                await ctx.message.add_reaction("👍")
            except discord.HTTPException:
                return await ctx.send_error(f"Could not ban anyone outside this guild with ID: {member}")

    @commands.command()
    @commands.dynamic_cooldown(owner_cooldown_bypass, type=commands.BucketType.user)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def mute(self, ctx: AsahiContext, member: discord.Member, *, reason: str = None):
        """Mute a member in this guild"""
        if await self.check_hierachy(ctx, member):
            return

        reason = reason or "No Reason Provided"
        raw_role_data = await self.mute_handler.fetch_mute_role(ctx.guild.id)

        if not raw_role_data:
            return await ctx.send_error("No mute role configured for this guild. Try again after setting one.")
        role = ctx.guild.get_role(raw_role_data[0])
        if role.position > ctx.me.top_role.position:
            return await ctx.send_error(
                "The mute role cannot be above me highest role. Please re-configure it to be lower and try again."
            )
        await member.add_roles(role)
        await ctx.send_ok(f"Muted {member} for the reason: {reason}")

    @commands.command()
    @commands.dynamic_cooldown(owner_cooldown_bypass, type=commands.BucketType.user)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def unmute(self, ctx: AsahiContext, member: discord.Member):
        """Unmmute a member in this guild"""

        raw_role_data = await self.mute_handler.fetch_mute_role(ctx.guild.id)

        if not raw_role_data:
            return await ctx.send_error("No mute role configured for this guild. Try again after setting one.")
        role = ctx.guild.get_role(raw_role_data[0])

        if role not in member.roles:
            return await ctx.send_error("This member is currently not muted with the configured mute role")
        if role.position > ctx.me.top_role.position:
            return await ctx.send_error(
                "The mute role cannot be above me highest role. Please re-configure it to be lower and try again."
            )

        await member.remove_roles(role)
        await ctx.message.add_reaction("👍")

    @commands.command()
    @commands.dynamic_cooldown(owner_cooldown_bypass, type=commands.BucketType.user)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def warn(self, ctx: AsahiContext, member: discord.Member, *, reason: str = None):
        """Warn a member in this guild"""
        if await self.check_hierachy(ctx, member):
            return
        reason = reason or "No Reason Provided"

        await self.warn_handler.insert_warning(
            member=member.id, guild_id=ctx.guild.id, moderator=ctx.author.id, reason=reason
        )
        await ctx.send_ok(f"Warned {member} for the reason {reason}")

    @commands.command()
    @commands.dynamic_cooldown(owner_cooldown_bypass, type=commands.BucketType.user)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def warns(self, ctx: AsahiContext, member: discord.Member = None):
        """View all the warns for someone in this guild"""
        member = member or ctx.author

        raw_warn_data: list[tuple] = await self.warn_handler.fetch_warnings(
            member.id, ctx.guild.id
        )  # returns in (user, gid, mid, reason, wid)
        await ctx.send_info(
            "\n\n".join(
                [
                    f"{num}. Warned for `{i[3]}` by `{await self.bot.getch_user(i[2])}` under warn ID: `{i[4]}`"
                    for num, i in enumerate(raw_warn_data, 1)
                ]
            )
        )

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setmuterole(self, ctx: AsahiContext, *, role: discord.Role):
        """Set this guilds mute role"""
        await self.mute_handler.set_mute_role(ctx.guild.id, role.id)
        await ctx.send_ok(f"Set this servers mute role to `{role.name}`")


async def setup(bot: Asahi):
    await bot.add_cog(Moderation(bot))
