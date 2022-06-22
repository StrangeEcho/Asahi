import typing

import discord
from discord.ext import commands

from core import Asahi, AsahiContext


class Help(commands.Cog):
    def __init__(self, bot: Asahi):
        self.bot = bot
        self.bot.help_command = AsahiHelp()


class AsahiHelp(commands.HelpCommand):
    context: AsahiContext

    async def send_bot_help(self, mapping: typing.Mapping) -> None:
        view = discord.ui.View()
        view.add_item(Navigator(self.context))
        await self.context.send(
            embed=discord.Embed(
                title=f":wave: Hi Im {self.context.bot.user.name}",
                description="Select one of my modules below for more information.",
                color=self.context.bot.info_color,
            ).set_thumbnail(url=self.context.bot.user.avatar.url),
            view=view,
        )

    async def send_cog_help(self, cog: commands.Cog):
        await self.context.send(
            embed=discord.Embed(
                title=f"Help for {cog.qualified_name.replace('_', ' ')}",
                description=cog.description or "No Description",
                color=self.context.bot.info_color,
            )
            .add_field(name="Commands", value="\n".join([f"`{i.qualified_name}`" for i in cog.get_commands()]))
            .set_footer(
                text=f"Use {self.context.clean_prefix}help <commandname> for help on a command",
                icon_url=self.context.bot.user.avatar.url,
            )
        )

    async def send_command_help(self, command: commands.Command):
        cd = command._buckets._cooldown
        aliases = command.aliases
        embed = discord.Embed(
            title=f"Help for {command.qualified_name}",
            description=command.help or "No Description",
            color=self.context.bot.info_color,
        )
        embed.add_field(
            name="Usage", value=f"`{self.context.clean_prefix}{command.qualified_name} {command.signature}`"
        )
        if aliases:
            embed.add_field(name="Aliases", value=", ".join([f"`{a}`" for a in aliases]), inline=False)
        if cd:
            embed.add_field(name="Cooldown", value=f"{cd.rate} time(s) per {cd.per} seconds", inline=False)
        embed.set_footer(text="[] - Optional | <> - Required")
        await self.context.send(embed=embed)

    async def send_group_help(self, group: commands.Group):
        cd = group._buckets._cooldown
        aliases = group.aliases
        embed = discord.Embed(
            title=f"Help for {group.qualified_name}",
            description=group.help or "No Description",
            color=self.context.bot.info_color,
        )
        embed.add_field(
            name="Sub-Commands", value=", ".join([f"`{cmd.qualified_name}`" for cmd in group.all_commands.values()])
        )
        if aliases:
            embed.add_field(name="Aliases", value=", ".join([f"`{a}`" for a in aliases]), inline=False)
        if cd:
            embed.add_field(name="Cooldown", value=f"{cd.rate} time(s) per {cd.per} seconds", inline=False)
        await self.context.send(embed=embed)


class Navigator(discord.ui.Select):
    def __init__(self, ctx: AsahiContext):
        self.ctx = ctx
        selectoptions: list[discord.SelectOption] = []
        self.sent: bool = False
        for i in [c for c in self.ctx.bot.cogs.values() if c.get_commands()]:
            selectoptions.append(
                discord.SelectOption(
                    label=i.qualified_name.replace("_", " "), value=i.qualified_name, description=i.description
                )
            )
        super().__init__(placeholder="Select a module/cog to view.", options=selectoptions)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("You are not able to use this view", ephemeral=True)
        else:
            await interaction.response.defer()
            if not self.sent:
                await self.ctx.send_help(self.ctx.bot.get_cog(self.values[0]))
                self.sent = True


async def setup(bot: Asahi):
    await bot.add_cog(Help(bot))
