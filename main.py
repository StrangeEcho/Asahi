import os
import platform

import discord
import config
from discord.ext import commands
from colorama import Fore, Style

loaded_cogs = 0

bot = commands.Bot(
    commands.when_mentioned_or(config.BOT_PREFIX), intents=discord.Intents.all()
)

bot.remove_command("help")


class HimejiHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page, color=discord.Color.random())
            await destination.send(embed=embed)


bot.help_command = HimejiHelpCommand(no_category="Help")


print(Fore.MAGENTA + "STARTING COG LOADING PROCESS", Style.RESET_ALL)
for cog in os.listdir("./cogs"):
    if cog.endswith(".py"):
        bot.load_extension(f"cogs.{cog[:-3]}")
        loaded_cogs += 1
        print(Fore.YELLOW + f"Loaded {cog}", Style.RESET_ALL)
print(Fore.MAGENTA + "DONE", Style.RESET_ALL)
print("-" * 15)


@bot.event
async def on_ready():
    print(Fore.GREEN, f"\rLogged in as {bot.user.name}(ID: {bot.user.id})")
    print(f"Total loaded cogs: {loaded_cogs}")
    print(
        f"Using Python version *{platform.python_version()}* and using Discord.py version *{discord.__version__}*"
    )
    print(
        f"Running on: {platform.system()} {platform.release()} ({os.name})",
        Style.RESET_ALL,
    )
    print("-" * 15)


bot.run(config.TOKEN)
