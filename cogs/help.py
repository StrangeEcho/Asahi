import asyncio
from typing import Union, Mapping

import discord

from discord.ext import commands

from utils.helpers import get_color
from utils.kurisu import KurisuBot



class KurisuHelpCommand(commands.HelpCommand):
    """Custom HelpCommand subclass for Kurisu"""

    async def send_bot_help(self, mapping: Mapping) -> None:
        """Override method"""

        dropdown_options: list[discord.ui.SelectOption] = []

        for cog in self.context.bot.cogs.values():
            if cog.get_commands():
                dropdown_options.append(
                    discord.ui.SelectOption(
                        label=cog.qualified_name.replace("_", " "),
                        emoji="<:kurisucute:914198893628108841>",
                        value=cog.qualified_name
                    )
                )

        componets: discord.ui.MessageComponents = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.SelectMenu(
                    options=dropdown_options,
                    placeholder="Pick a module/cog to preview!"
                )
            )
        )

        chan: Union[discord.TextChannel, discord.DMChannel] = self.get_destination()
        msg = await chan.send(
            components=componets,
            embed=discord.Embed(
                title=f":wave: Hello there. Im {self.context.bot.user.name}",
                description="Kurisu is a multi-modular all purpose bot built with Discord.py\n\n"
                            "Prefix: "
                            f"`{self.context.bot.prefixes.get(str(self.context.guild.id)) or self.context.bot.get_config('config', 'config', 'prefix')}` "
                            f"or {self.context.bot.user.mention}",
                color=get_color("ok_color")
            ).set_thumbnail(url=self.context.bot.user.avatar.url)
            .set_footer(text=f"Do {self.context.clean_prefix}help <module/command> to for more info.")
        )

        def check(p: discord.Interaction):
            return p.message.id == msg.id and p.user.id == self.context.author.id

        try:
            payload: discord.Interaction = await self.context.bot.wait_for(
                "component_interaction",
                check=check,
                timeout=30
            )
            await self.send_cog_help(self.context.bot.get_cog(payload.values[0]))
            await msg.delete()
        except asyncio.TimeoutError:
            componets.disable_components()
            await msg.add_reaction("⏰")


    async def send_command_help(self, command: commands.Command) -> None:
        """Override method"""
        chan: Union[discord.TextChannel, discord.DMChannel] = self.get_destination()
        await chan.send(
            embed=discord.Embed(
                title=f"Info for `{command.qualified_name}`",
                description=f"Command Description: `{command.help}`",
                color=get_color("ok_color")
            ).add_field(name="Module/Cog", value=f"`{command.cog_name}`")
            .add_field(name="Usage", value=f"`{self.context.clean_prefix}{command.qualified_name} {command.signature}`")
            .add_field(
                name="Aliases",
                value=f"\n".join([f"`{a}`" for a in command.aliases]) if command.aliases else "`None`"
            )
            .set_footer(text="<> params signify required arguments while [] signify optional arguments")
        )


    async def send_cog_help(self, cog: commands.Cog) -> None:
        """Override method"""
        chan: Union[discord.TextChannel, discord.DMChannel] = self.get_destination()
        embed = discord.Embed(
            title=f"Info for `{cog.qualified_name}`",
            description=f"Description: `{cog.description}`",
            color=get_color("ok_color")
        )
        if cog.get_commands():
            embed.add_field(
                name="Commands",
                value="\n".join([f"`{c.name}`" for c in cog.get_commands() if not c.hidden])
            )
        await chan.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.bot.help_command = KurisuHelpCommand()

def setup(bot):
    bot.add_cog(Help(bot))