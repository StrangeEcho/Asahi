from typing import Optional, Union

from discord.ext import commands
from discord.utils import get
import discord

from utils.classes import HimejiBot
from utils.funcs import check_hierarchy


class Moderation(commands.Cog):
    def __init__(self, bot: HimejiBot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def ban(
        self,
        ctx: commands.Context,
        member: Union[discord.Member, int] = None,
        *,
        reason: str = None,
    ):
        """Ban users from the current server"""

        if reason is None:
            reason = "No reason passed"

        actionembed = discord.Embed(
            description=f" :red_circle: Banned {member} for {reason}", color=self.bot.ok_color
        )
        actionembed.set_footer(text=f"Moderator: {ctx.author}")

        if isinstance(member, discord.Member):
            if await check_hierarchy(ctx, member):
                return
            try:
                await member.send(
                    embed=discord.Embed(
                        title=f"You were banned from {ctx.guild}",
                        description=f"Reason: {reason}",
                        color=self.bot.ok_color,
                    ).set_footer(text=f"Moderator: {ctx.author}")
                )
                await member.ban(reason=f"{reason} | Moderator: {ctx.author}")
                embed = discord.Embed(
                    description=f"Banned {member} for {reason}", color=self.bot.ok_color
                )
                embed.set_footer(text=f"Moderator: {ctx.author}")
                await ctx.send(embed=actionembed)
            except discord.Forbidden:
                await ctx.send(
                    embed=discord.Embed(
                        description=f":warning: Failed sending DM to {member}\n**Proceeding with ban regardless.**",
                        color=self.bot.error_color,
                    )
                )
                await member.ban(reason=f"{reason} | Moderator: {ctx.author}")
                await ctx.send(embed=actionembed)
        if isinstance(member, int):
            user = await self.bot.fetch_user(member)
            await ctx.guild.ban(user, reason=f"{reason} | Moderator: {ctx.author}")
            await ctx.send(
                embed=discord.Embed(
                    description=f":red_circle: Banned {user} for {reason}", color=self.bot.ok_color
                ).set_footer(text=f"Moderator: {ctx.author}")
            )

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        """Kick members from the current server"""
        if await check_hierarchy(ctx, member):
            return

        if reason is None:
            reason = "No reason passed"

        await member.kick(reason=f"{reason} | Moderator: {ctx.author}")
        await ctx.send(
            embed=discord.Embed(
                description=f":boot: Successfully kicked `{member}` from this guild.",
                color=self.bot.ok_color,
            )
        )

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
                await ctx.send(
                    embed=discord.Embed(
                        description=f":green_circle: Successfully unbanned `{user}` from this guild.",
                        color=self.bot.ok_color,
                    )
                )
            except discord.HTTPException:
                await ctx.send(
                    embed=discord.Embed(
                        description=f"Failed trying to unban `{user}`. This user is probably already unbanned.",
                        color=self.bot.error_color,
                    )
                )

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def mute(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        """Mute a member"""
        if await check_hierarchy(ctx, member):
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
            await ctx.send(
                embed=discord.Embed(
                    description=f":shushing_face: Successfully muted `{member}` for `{reason}`",
                    color=self.bot.ok_color,
                )
            )
        elif get(ctx.guild.roles, name="Himeji-Mute"):
            await member.add_roles(get(ctx.guild.roles, name="Himeji-Mute"))
            await ctx.send(
                embed=discord.Embed(
                    description=f":shushing_face: Successfully muted `{member}` for `{reason}`",
                    color=self.bot.ok_color,
                )
            )

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        """Unmute a member"""
        if not get(ctx.guild.roles, name="Himeji-Mute") in member.roles:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{member} is not muted.", color=self.bot.error_color
                )
            )
        elif get(ctx.guild.roles, name="Himeji-Mute") in member.roles:
            await member.remove_roles(get(ctx.guild.roles, name="Himeji-Mute"))
            await ctx.send(
                embed=discord.Embed(
                    description=f":unlock: Successfully unmuted `{member}`",
                    color=self.bot.ok_color,
                )
            )

    @commands.command(aliases=["clear", "remove"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def purge(self, ctx: commands.Context, amount: int = None):
        """Purge x amount of messages"""
        if amount is None:
            await ctx.send("Please pass in a amount of messages you want me to delete.")
        else:
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)
            await ctx.send(
                embed=discord.Embed(
                    description=f":put_litter_in_its_place: Successfully purged `{amount}` from this channel",
                    color=self.bot.ok_color,
                )
            )

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slowmode(
        self, ctx: commands.Context, chan: Optional[discord.TextChannel] = None, time: int = 0
    ):
        """Turn a slowmode delay on a specified channel in SECONDS"""
        if chan is None:
            chan = ctx.channel
        if time > 21600:
            await ctx.send(
                embed=discord.Embed(
                    description="Slowmode delay cannot go longer than 21600 seconds",
                    color=self.bot.ok_color,
                )
            )
        else:
            await chan.edit(slowmode_delay=time)
            await ctx.send(f"`{chan.name}` now has a slowmode delay of `{time}` seconds")


def setup(bot):
    bot.add_cog(Moderation(bot))
