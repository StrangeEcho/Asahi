import discord

from discord.ext import commands

from utils.classes import KurisuBot


class Help(commands.Cog):
    """Help related commands"""

    def __init__(self, bot: KurisuBot):
        self.bot = bot

    @commands.command(aliases=["cogs"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def modules(self, ctx: commands.Context):
        await ctx.send(
            embed=discord.Embed(
                title=f"{self.bot.user.name}'s available modules/cogs",
                description=("```\n" + "\n".join(sorted(map(str, self.bot.cogs)))) + "\n```",
                color=self.bot.ok_color,
            ).set_footer(
                text=f"use {ctx.clean_prefix}help [module] to get info about a module/cog"
            )
        )

    @commands.group(invoke_without_command=True)
    async def help(self, ctx: commands.Context):
        """Shows information on a specific command or module"""
        await ctx.send(
            embed=discord.Embed(
                title=f"Hi I'm {self.bot.user.name}",
                description=f"{self.bot.user.name} is a multi-modular all purpose bot built with Discord.py",
                color=self.bot.ok_color,
            )
            .set_thumbnail(url=self.bot.user.avatar.url)
            .set_footer(
                icon_url=self.bot.user.avatar.url,
                text=f"{self.bot.user} has been serving users since {self.bot.user.created_at.strftime('%c')}",
            )
            .add_field(
                name="Modules",
                value=(
                    f"Run `{ctx.clean_prefix}modules` for a list of active modules\n\n"
                    f"Run `{ctx.clean_prefix}help module <modulename>` for info on a specific module"
                ),
            )
            .add_field(
                name="Commands",
                value=f"Run `{ctx.clean_prefix}help command <commandname>` for info on a command",
            )
        )

    @help.command(aliases=["cmd"])
    async def command(self, ctx: commands.Context, *, target: str):
        cmd: commands.Command = self.bot.get_command(target.lower())
        if cmd:
            cmd_aliases = "\n".join(cmd.aliases)
            return await ctx.send(
                embed=discord.Embed(
                    title=f"Command: __{cmd.name}__",
                    description=f"`Command Description: {cmd.help}`",
                    color=self.bot.ok_color,
                )
                .add_field(
                    name="Usage",
                    value=f"`{ctx.clean_prefix}{cmd.name} {'' if not cmd.signature else cmd.signature}`",
                )
                .add_field(name="Module", value=f"`{cmd.cog_name}`")
                .add_field(
                    name=f"Aliases",
                    value="`None`" if not cmd.aliases else f"```\n{cmd_aliases}\n```",
                )
                .set_footer(
                    text="[] signify optional arguments while <> signify required arguments"
                )
            )
        if not cmd:
            return await ctx.send(
                embed=discord.Embed(
                    description=f"**COMMAND NOT FOUND**", color=self.bot.error_color
                )
            )

    @help.command(aliases=["mod"])
    async def module(self, ctx: commands.Context, target: str):
        found = []
        for c in self.bot.cogs:
            if str(c).lower().startswith(target.lower()):
                found.append(c)
            if c.lower() == target.lower():
                found = [c]
                break
        if found:
            cog = self.bot.get_cog(found[0])
            cog_commands = "\n".join(sorted(map(str, cog.get_commands()))) or None
            return await ctx.send(
                embed=discord.Embed(
                    title=cog.qualified_name or target,
                    color=self.bot.ok_color,
                )
                .add_field(name="Description", value=f"`{cog.description or None}`")
                .add_field(name="Commands", value=f"```\n{cog_commands}\n```")
                .set_footer(
                    text=f"Do {ctx.clean_prefix}help command <commandname> for help with a command"
                )
            )
        if not found:
            return await ctx.send(
                embed=discord.Embed(
                    description=f"**MODULE NOT FOUND**", color=self.bot.error_color
                )
            )


def setup(bot):
    bot.add_cog(Help(bot))
