import logging

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    """Handler for discord.py errors."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError
    ):
        """Handle errors caused by commands."""
        # Skips errors that were already handled locally.
        if getattr(ctx, 'handled', False):
            return

        ignored = (commands.CommandNotFound)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(
                title='Oops!',
                description='Command Failed To Execute. Reason:\n`Command Can Not Be Used In Direct Messages`',
                color=0xFF0000
            )
            await ctx.send(embed=embed)
		
        
        elif isinstance(error, commands.TooManyArguments):
            embed = discord.Embed(
                title='Oops!',
                description='Command Failed To Execute. Reason:\n`Passed In Too Many Arguments`',
                color=0xFF0000
            )
            await ctx.send(embed=embed)

        elif isinstance(error, commands.NSFWChannelRequired):
            embed = discord.Embed(
                title='Oops!',
                description=f'Command Failed To Execute. Reason:\n`{ctx.channel} Is Not NSFW`',
                color=0xFF0000
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, discord.Forbidden):
            embed = discord.Embed(
                title='Oops!',
                description='Command Failed To Execute. Reason:\n`Discord Is Restricting Command Execution`',
                color=0xFF0000
            )
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title='Oops!',
                description=f'Command Failed To Execute. Reason:\n`Missing Required Argument:`\n`{error.param.name}`',
                color=0xFF0000
            )
            await ctx.send(embed=embed)

        elif (
            isinstance(error, commands.NotOwner)
            or isinstance(error, commands.MissingPermissions)
        ):
            embed = discord.Embed(
                title='Oops',
                description='Command Failed To Execute. Reason:\n`Missing Permissions`',
                color=0xFF0000
            )
            await ctx.send(embed=embed)

        elif (
            isinstance(error, commands.CommandOnCooldown)
            or isinstance(error, commands.CheckFailure)
        ):
            embed = discord.Embed(
                title='Oops',
                description='Command Failed To Execute. Reason\n```{error}```',
                color=0xFF0000
            ) 
            await ctx.send(embed=embed)

        elif isinstance(error, commands.DisabledCommand): #SoonTM
            embed = discord.Embed(
                title='Oops!',
                description='Command Failed To Execute. Reason:\n`Command Is Disabled`',
                color=0xFF0000
            )
            await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title='Oops!',
                description=f'Command Failed To Execute. Reason:\n`Bad Argument`\n```{error}```',
                color=0xFF0000
            )
            await ctx.send(embed=embed)

        elif isinstance(error, discord.HTTPException):
            embed = discord.Embed(
                title='Oops!',
                description='Commands Failed To Execute. Reason:\n`A HTTP EXCEPTION WAS THROWN`',
                color=0xFF0000
            )
            embed.add_field(
                name='Action Command Failure?',
                value='If the command used was a Action command, there is a high chance that the API Request failed.',
                inline=True
            )
            embed.set_footer(text='Please Contact #Tylerr#6979 For Help.')
            await ctx.send(embed=embed)
            
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title='Oops!',
                description='Command Failed To Execute. Reason:\n`Bot Is Missing Permissions`',
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            log.error(
                f'{ctx.command.qualified_name} cannot be executed because the '
                f'bot is missing the following permissions: '
                f'{", ".join(error.list)}'
            )

        elif isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title='Oops!',
                description='Command Failed To Execute. Reason:\n`INTERNAL ERROR`',
                color=0xFF0000 
            )
            embed.set_footer(text='Please Contact Tylerr#6979 For Help')
            await ctx.send(embed=embed)
            log.error(
                f'{ctx.command.qualified_name} failed to execute. ',
                exc_info=error.original
            )

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
