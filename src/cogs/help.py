import typing

import discord
from discord.ext import commands

from core.bot import Asahi
from core.context import AsahiContext


class Help(commands.Cog):
    def __init__(self, bot: Asahi):
        self.bot = bot
        self.bot.help_command = AsahiHelp()


class AsahiHelp(commands.HelpCommand):
    context: AsahiContext

    async def send_bot_help(self, mapping: typing.Mapping) -> None:
        view = discord.ui.View()
        view.add_item(Navigator(self.context))
        await self.context.send(view=view)

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
        await self.context.send(
            embed=discord.Embed(
                title=f"Help for {command.qualified_name}",
                description=command.help or "No Description",
                color=self.context.bot.info_color,
            )
            .add_field(name="Aliases", value="\n".join([f"`{a}`" for a in command.aliases]) or "No Aliases")
            .add_field(
                name="Usage",
                value=f"`{self.context.clean_prefix}{command.qualified_name} {command.signature}`",
                inline=False,
            )
            .add_field(name="Cooldown", value=f"`{cd.rate}` time(s) per `{cd.per}` seconds", inline=False)
            .set_footer(text=f"You can run this command: {await command.can_run(self.context)}")
        )


class Navigator(discord.ui.Select):
    def __init__(self, ctx: AsahiContext):
        self.ctx = ctx
        selectoptions: list[discord.SelectOption] = []
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
            await self.ctx.send_help(self.ctx.bot.get_cog(self.values[0]))


async def setup(bot: Asahi):
    await bot.add_cog(Help(bot))
