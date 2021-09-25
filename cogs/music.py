import asyncio
from datetime import timedelta

from discord.ext import commands
import discord
import lavalink

from utils.context import KurisuContext
from utils.kurisu import KurisuBot


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
            bot=self.bot, host=self.ll_ip, ws_port=self.ll_ws_port, password=self.ll_password
        )
        self.bot.logger.info(
            f"Initialized LavaLink Node\nIP: {self.ll_ip}\nPort: {self.ll_ws_port}"
        )

    @commands.command(name="connect")
    async def _conenct(self, ctx: KurisuContext):
        """Connect the bot to your vc"""
        if not ctx.author.voice.channel:
            return await ctx.send_error(
                "You are not in a Voice Channel. Please try again after joining one. "
            )
        await lavalink.connect(ctx.author.voice.channel, True)
        await ctx.send_ok(f"Connected to {ctx.author.voice.channel.name}")

    @commands.command(aliases=["np"])
    async def nowplaying(self, ctx: KurisuContext):
        """See what the current song is"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send_error("No Activate Players")
        ct = player.current
        await ctx.send_ok(
            f"Currently Playing [{ct.title}]({ct.uri}) by {ct.author}\nTrack Length: {timedelta(milliseconds=ct.length)}"
        )

    @commands.command()
    async def skip(self, ctx: KurisuContext):
        """Skip Song"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send_error("No Activate Players")
        await player.skip()
        await ctx.send_ok("Skipped Last Song")

    @commands.command()
    async def volume(self, ctx: KurisuContext, vol: int):
        """Change Volume"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send_error("No Activate Players")
        if vol < 0 or vol > 100:
            return await ctx.send_error("Volume Must Be Between 0 and 100")
        await player.set_volume(vol)
        await ctx.send_ok(f"Changed Volume To {player.volume}%")

    @commands.command()
    async def repeat(self, ctx: KurisuContext):
        """Toggle a repeat for the queue"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send_error("No Activate Players")
        if not player.repeat:
            player.repeat = True
            return await ctx.send_ok("Repeating Queue")
        if player.repeat:
            player.repeat = False
            return await ctx.send_ok("No longer repeating queue")

    @commands.command()
    async def shuffle(self, ctx: KurisuContext):
        """Toggle a shuffle for the queue"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send_error("No Activate Players")
        if not player.shuffle:
            player.shuffle = True
            return await ctx.send_ok("Repeating Queue")
        if player.shuffle:
            player.shuffle = False
            return await ctx.send_ok("No longer repeating queue")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def play(self, ctx: KurisuContext, *, query: str):
        """Play a song"""
        if not ctx.author.voice.channel:
            return ctx.send_error("You must be in a voice channel to use this command.")

        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            player = await lavalink.connect(ctx.author.voice.channel, True)

        tracks = await player.search_yt(query)
        if not tracks:
            return await ctx.send_error("No tracks found")
        if len(tracks.tracks) == 1:
            player.add(ctx.author, tracks.tracks[0])
            return await ctx.send_ok(f"Added {tracks.tracks[0].title} To The Queue.")

        await ctx.send_ok(
            "Pick 1 out of 5\n"
            + "\n".join([f"`{x}`. {v.title[:100]} - {timedelta(milliseconds=v.length)}" for x, v in enumerate(tracks.tracks[:5], 1)])
        )

        def check(m: discord.Message):
            return (
                m.author == ctx.author
                and m.channel == ctx.channel
                and m.content in ["1", "2", "3", "4", "5"]
            )
        try:
            msg: discord.Message = await self.bot.wait_for("message", check=check, timeout=15)
            a_int = int(msg.content) - 1
            player.add(ctx.author, tracks.tracks[a_int])
            await ctx.send_ok(f"Added {tracks.tracks[a_int].title} To The Queue.")
        except asyncio.TimeoutError:
            await ctx.send_error("Timeout Reached")

        if not player.is_playing:
            await player.play()

    @commands.command()
    async def disconnect(self, ctx: KurisuContext):
        """Disconnect me from vc"""
        if not ctx.me.voice.channel:
            return ctx.send_error("I am not connected to any vc.")
        if not ctx.author in ctx.me.voice.channel.members:
            return await ctx.send_error("You must be in the same vc as me to disconnect me.")
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send_error("No Activate Players")
        await player.disconnect()
        await ctx.send_ok("Disconnected")

    @commands.command()
    async def queue(self, ctx: KurisuContext):
        """Check the queue."""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send_error("No Active Player")

        if not player.is_playing:
            return await ctx.send_error("Not playing anything.")
        player = lavalink.get_player(ctx.guild.id)
        if len(player.queue) == 0:
            return await ctx.send_error("Nothing in queue.")
        msg = f"**Queue in {ctx.guild.name}:**\n\n"
        for t in player.queue:
            msg += f"- `{t.title}` Added by `{t.requester}`\n"
        await ctx.send_ok(msg)


def setup(bot):
    bot.add_cog(Music(bot))
