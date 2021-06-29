from discord.ext import commands
import discord

from config import BOT_PREFIX
from utils.classes import HimejiBot
import config


class Help(commands.Cog):
    def __init__(self, bot: HimejiBot):
        self.bot = bot

    @commands.command() # Command made by zedchance modified by Tylerr
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help(self, ctx: commands.Context, *, commands: str):
        """ Shows this message """
        embed = discord.Embed(title=f"{self.bot.user}", color=self.bot.ok_color)

        def generate_usage(command_name):
            """ Generates a string of how to use a command """
            temp = f"{config.BOT_PREFIX}"
            command = self.bot.get_command(command_name)
            # Aliases
            if len(command.aliases) == 0:
                temp += f"{command_name}"
            elif len(command.aliases) == 1:
                temp += f"[{command.name}|{command.aliases[0]}]"
            else:
                t = "|".join(command.aliases)
                temp += f"[{command.name}|{t}]"
            # Parameters
            params = f" "
            for param in command.clean_params:
                params += f"<{command.clean_params[param]}> "
            temp += f"{params}"
            return temp

        def generate_command_list(cog):
            """ Generates the command list with properly spaced help messages """
            # Determine longest word
            max = 0
            for command in self.bot.get_cog(cog).get_commands():
                if not command.hidden:
                    if len(f"{command}") > max:
                        max = len(f"{command}")
            # Build list
            temp = ""
            for command in self.bot.get_cog(cog).get_commands():
                if command.hidden:
                    temp += ""
                elif command.help is None:
                    temp += f"{command}\n"
                else:
                    temp += f"`{command}`"
                    for i in range(0, max - len(f"{command}") + 1):
                        temp += "   "
                    temp += f"{command.help}\n"
            return temp

        # Help by itself just lists our own commands.
        if len(commands) == 0:
            for cog in self.bot.cogs:
                temp = generate_command_list(cog)
                if temp != "":
                    embed.add_field(name=f"**{cog}**", value=temp, inline=False)
        elif len(commands) == 1:
            # Try to see if it is a cog name
            name = commands[0].capitalize()
            command = None

            if name in self.bot.cogs:
                cog = self.bot.get_cog(name)
                msg = generate_command_list(name)
                embed.add_field(name=name, value=msg, inline=False)
                msg = f"{cog.description}\n"
                embed.set_footer(text=msg)

            # Must be a command then
            else:
                command = self.bot.get_command(name)
                if command is not None:
                    help = f""
                    if command.help is not None:
                        help = command.help
                    embed.add_field(
                        name=f"**{command}**",
                        value=f"{command.description}```{generate_usage(name)}```\n{help}",
                        inline=False,
                    )
                else:
                    msg = " ".join(commands)
                    embed.add_field(name="Not found", value=f"Command/category `{msg}` not found.")
        else:
            msg = " ".join(commands)
            embed.add_field(name="Not found", value=f"Command/category `{msg}` not found.")

        try:
            await ctx.author.send(f"{ctx.author.mention}", embed=embed)
            await ctx.message.add_reaction("\u2705")
        except discord.HTTPException:
            await ctx.send(
                "Failed sending help DM. Please open your DMS and run the command again"
            )
            await ctx.message.add_reaction("\u2049")
        return


def setup(bot):
    bot.add_cog(Help(bot))
