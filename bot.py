import os
import platform
import sys
import asyncio
import discord
import traceback
import inspect
import textwrap
import contextlib
import io

from discord.ext import commands
from contextlib import redirect_stdout

if not os.path.isfile("config.py"):
	sys.exit("config.py' not found! Please add it and try again.")
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
	
bot = commands.Bot(command_prefix=commands.when_mentioned_or(config.BOT_PREFIX), intents=intents)

# The code in this event is executed when the bot is ready
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
		await bot.change_presence(activity=discord.Game("with you :D"))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Game("with Tylerr#6979!"))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Game(f"{config.BOT_PREFIX}help"))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Game("with humans!"))
		await asyncio.sleep(60)

# help command stuff
bot.remove_command("help")


class HimejiHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page, color=0xff00ff)
            await destination.send(embed=embed)
bot.help_command = HimejiHelpCommand()

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
			context = await bot.get_context(message) #fix this 
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
	print(f"Command Executed\nName: {executedCommand}\nGuild Name: {ctx.guild.name} (GID: {ctx.guild.id})\nUser: {ctx.message.author} (ID: {ctx.message.author.id})\nChannel:{ctx.channel} (CID: {ctx.channel.id})\n-------------------")


@bot.command(name='eval') #Borrowed eval command. -R.Danny
@commands.is_owner()
async def _eval(ctx, *, body): 
    env = {
        'ctx': ctx,
        'bot': bot,
        'channel': ctx.channel,
        'author': ctx.author,
        'guild': ctx.guild,
        'message': ctx.message,
        'source': inspect.getsource
    }

    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    env.update(globals())

    body = cleanup_code(body)
    stdout = io.StringIO()
    err = out = None

    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    def paginate(text: str):
        '''Simple generator that paginates text.'''
        last = 0
        pages = []
        for curr in range(0, len(text)):
            if curr % 1980 == 0:
                pages.append(text[last:curr])
                last = curr
                appd_index = curr
        if appd_index != len(text) - 1:
            pages.append(text[last:curr])
        return list(filter(lambda a: a != '', pages))

    try:
        exec(to_compile, env)
    except Exception as e:
        err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
        return await ctx.message.add_reaction('\u2049')

    func = env['func']
    try:
        with redirect_stdout(stdout):
            ret = await func()
    except Exception as e:
        value = stdout.getvalue()
        err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
    else:
        value = stdout.getvalue()
        if ret is None:
            if value:
                try:

                    out = await ctx.send(f'```py\n{value}\n```')
                except:
                    paginated_text = paginate(value)
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f'```py\n{page}\n```')
                            break
                        await ctx.send(f'```py\n{page}\n```')
        else:
            try:
                out = await ctx.send(f'```py\n{value}{ret}\n```')
            except:
                paginated_text = paginate(f"{value}{ret}")
                for page in paginated_text:
                    if page == paginated_text[-1]:
                        out = await ctx.send(f'```py\n{page}\n```')
                        break
                    await ctx.send(f'```py\n{page}\n```')

    if out:
        await ctx.message.add_reaction('\u2705')  # tick
    elif err:
        await ctx.message.add_reaction('\u2049')  # x
    else:
        await ctx.message.add_reaction('\u2705')

bot.run(config.TOKEN)