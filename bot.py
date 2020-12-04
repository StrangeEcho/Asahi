import os
import platform
import sys
import asyncio
import discord

from discord.ext.commands import Bot
from discord.ext import commands

if not os.path.isfile("config.py"):
	sys.exit("'config.py' not found! Please add it and try again.")
else:
	import config

#intent stuff
intents = discord.Intents().default()
intents.messages = True
intents.reactions = True
intents.presences = True
intents.members = True
intents.guilds = True
intents.emojis = True
intents.bans = True
intents.guild_typing = False
intents.typing = False
intents.dm_messages = False
intents.dm_reactions = False
intents.dm_typing = False
intents.guild_messages = True
intents.guild_reactions = True
intents.integrations = True
intents.invites = True
intents.voice_states = False
intents.webhooks = False
	
bot = Bot(command_prefix=commands.when_mentioned_or(config.BOT_PREFIX), intents=intents)

#bot ready stuff
@bot.event
async def on_ready():
	bot.loop.create_task(status_task())
	print(f"Logged in as {bot.user.name}")
	print(f"Discord.py API version: {discord.__version__}")
	print(f"Python version: {platform.python_version()}")
	print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
	print("-------------------")

#game status stuff
async def status_task():
	while True:
		await bot.change_presence(activity=discord.Game("with you:D"))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Game("with Tylerr#6979!"))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Game(f"{config.BOT_PREFIX}help"))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Game("with humans!"))
		await asyncio.sleep(60)

# Remove gross gey dpy help command
bot.remove_command("help")
#cog stuff
if __name__ == "__main__":
	for extension in config.STARTUP_COGS:
		try:
			bot.load_extension(extension)
			extension = extension.replace("cogs.", "")
			print(f"Loaded extension '{extension}'")
		except Exception as e:
			exception = f"{type(e).__name__}: {e}"
			extension = extension.replace("cogs.", "")
			print(f"Failed to load extension {extension}\n{exception}")


@bot.event
async def on_message(message):
	# Ignores other bots and itself
	if message.author == bot.user or message.author.bot:
		return
	else:
		if message.author.id not in config.BLACKLIST:
			# Process command if user isnt blacklisted
			await bot.process_commands(message)
		else:
			# Let em know hes blacklisted
			context = await bot.get_context(message)
			embed = discord.Embed(
				title="Looks like you are blacklisted buddy. RIP :c",
				description="Ask the Tylerr#6979 to remove you from the list if you think it's not normal.",
				color=0x00FF00
			)
			await context.send(embed=embed)

# logs sucessfull commands
@bot.event
async def on_command_completion(ctx):
	fullCommandName = ctx.command.qualified_name
	split = fullCommandName.split(" ")
	executedCommand = str(split[0])
	print(f"Executed {executedCommand} command in {ctx.guild.name} by {ctx.message.author} (ID: {ctx.message.author.id})")

# error stuff
@bot.event
async def on_command_error(context, error):
	if isinstance(error, commands.CommandOnCooldown):
		embed = discord.Embed(
			title="Error!",
			description="This command is on a %.2fs cooldown" % error.retry_after,
			color=0x00FF00
		)
		await context.send(embed=embed)
	raise error

#todo idk. finish up some more code. perhaps add an eval
bot.run(config.TOKEN)
