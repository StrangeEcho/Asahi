import discord
import lavalink
from discord.ext import commands

from datetime import timedelta

from utils.classes import KurisuBot


class Music(commands.Cog):
    """Music Module"""
    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.bot.loop.create_task(self.node_init())
        self.ll_ip = self.bot.get_config("config", "music", "ll_host")
        self.ll_ws_port = self.bot.get_config("config", "music", "ll_port")
        self.ll_password = self.bot.get_config("config", "music", "ll_password")

    async def node_init(self):
        """Initialize LavaLink Node"""
        await lavalink.initialize(
            bot=self.bot,
            host=self.ll_ip,
            ws_port=self.ll_ws_port,
            password=self.ll_password
        )
        self.bot.logger.info(f"Initialized LavaLink Node\nIP: {self.ll_ip}\nPort: {self.ll_ws_port}")

    @commands.command(name="connect")
    async def _conenct(self, ctx: commands.Context):
        """Connect the bot to your vc"""
        await lavalink.connect(ctx.author.voice.channel, True)
        await ctx.send(f"Connected to {ctx.author.voice.channel.name}")

    @commands.command(aliases=["np"])
    async def nowplaying(self, ctx: commands.Context):
        """See what the current song is"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send("No Activate Players")
        ct = player.current
        await ctx.send(f"Currently Playing [{ct.title}]({ct.uri}) by {ct.author}\nTrack Length: {timedelta(milliseconds=ct.length)}")

    @commands.command()
    async def skip(self, ctx: commands.Context):
        """Skip Song"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send("No Activate Players")
        await player.skip()
        await ctx.send("Skipped Last Song")

    @commands.command()
    async def volume(self, ctx: commands.Context, vol: int):
        """Change Volume"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send("No Activate Players")
        if vol < 0 or vol > 100:
            return await ctx.send("Volume Must Be Between 0 and 100")
        await player.set_volume(vol)
        await ctx.send(f"Changed Volume To {player.volume}%")

    @commands.command()
    async def repeat(self, ctx: commands.Context):
        """Toggle a repeat for the queue"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send("No Activate Players")
        if not player.repeat:
            player.repeat = True
            return await ctx.send("Repeating Queue")
        if player.repeat:
            player.repeat = False
            return await ctx.send("No longer repeating queue")

    @commands.command()
    async def shuffle(self, ctx: commands.Context):
        """Toggle a shuffle for the queue"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send("No Activate Players")
        if not player.shuffle:
            player.shuffle = True
            return await ctx.send("Repeating Queue")
        if player.shuffle:
            player.shuffle = False
            return await ctx.send("No longer repeating queue")

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        """Play a song"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            player = await lavalink.connect(ctx.author.voice.channel, True)

        tracks = await player.search_yt(query)
        if not tracks:
            return await ctx.send("No tracks found")
        if len(tracks.tracks) == 1:
            player.add(ctx.author, tracks.tracks[0])
            return await ctx.send(f"Added {tracks.tracks[0].title} To The Queue.")

        await ctx.send("Pick 1 out of 5\n" + "\n".join([f"{x}. {v.title[:100]}" for x, v in enumerate(tracks.tracks[:5], 1)]))

        def check(m: discord.Message):
            return m.author == ctx.author and m.channel == ctx.channel and m.content in ["1", "2", "3", "4", "5"]

        msg: discord.Message = await self.bot.wait_for("message", check=check, timeout=15)
        player.add(ctx.author, tracks.tracks[int(msg.content)])
        await player.play()

    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        """Disconnect me from vc"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send("No Activate Players")
        await player.disconnect()
        await ctx.send("Disconnected")

    @commands.command()
    async def queue(self, ctx):
        """Check the queue."""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send("I'm not connected to any voice channels.")

        if not player.is_playing:
            return await ctx.send("Not playing anything.")
        player = lavalink.get_player(ctx.guild.id)
        if len(player.queue) == 0:
            return await ctx.send("Nothing in queue.")
        msg = f"**Queue in {ctx.guild.name}:**\n\n"
        for t in player.queue:
            msg += f"- `{t.title}` Added by `{t.requester}`\n"
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Music(bot))

