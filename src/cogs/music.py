from datetime import timedelta
from typing import Optional, Union
import asyncio
import logging

from discord.ext import commands
from discord.ui import Select, View
from pomice import LoopMode, Playlist, Queue, Track
import discord
import pomice

from core import Asahi, AsahiContext
from exts import chunk_list, humanize_timedelta, Paginator


class Player(pomice.Player):
    """Custom implementation of pomice's player adding a queue system"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue: Queue = Queue()

    @property
    def queue(self) -> Queue:
        return self._queue


class TrackNavigator(Select):
    def __init__(self, ctx: AsahiContext, tracks: list[Track]):
        self.tracks: list[Track] = tracks
        self.select_options: list[discord.SelectOption] = []
        self.ctx: AsahiContext = ctx

        for i, track in enumerate(self.tracks[:5], 1):
            self.select_options.append(
                discord.SelectOption(
                    label=f"{i}. {track.title[:50]}", description=f"From: {track.author[:50]}", value=str(i - 1)
                )
            )
        super().__init__(placeholder="Select A Song To Play!", options=self.select_options)

    async def callback(self, inter: discord.Interaction) -> Optional[discord.Message]:
        if self.ctx.author.id != inter.user.id:
            return await inter.response.send_message("You are not able to use this Select Menu", ephemeral=True)

        player: Player = self.ctx.voice_client
        track: Track = self.tracks[int(self.values[0])]
        await inter.response.defer()
        if player.is_playing:
            player.queue.put(track)
            await self.ctx.send_ok(f"Enqueued {track.title[:50]} into the queue")
        else:
            await player.play(track)
            await self.ctx.send_ok(f"Now playing {track.title[:50]}")


class MusicView(View):
    def __init__(self, ctx: AsahiContext, tracks: list[Track]):
        super().__init__(timeout=30)
        self.add_item(TrackNavigator(ctx, tracks))


class Music(
    commands.Cog,
    command_attrs={"cooldown": commands.CooldownMapping.from_cooldown(1, 3.5, commands.BucketType.user)},
):
    def __init__(self, bot: Asahi):
        self.bot = bot
        asyncio.get_event_loop().create_task(self.create_ll_connection())

    def is_vc_joinable(self, ctx: AsahiContext) -> bool:
        """Checks if a vc is joinable under certain conditions"""
        if not ctx.author.voice:
            return False
        if not ctx.author.voice.channel.permissions_for(ctx.me).connect:
            return False
        if len(ctx.author.voice.channel.members) == ctx.author.voice.channel.user_limit:
            return False
        else:
            return True

    async def create_ll_connection(self) -> None:
        """Create a connection to LavaLink node"""
        await self.bot.wait_until_ready()
        music_logger = logging.getLogger("music-master")
        try:
            node = await self.bot.node_pool.create_node(
                bot=self.bot,
                host=self.bot.config.get("ll_host"),
                port=self.bot.config.get("ll_port"),
                password=self.bot.config.get("ll_password"),
                spotify_client_id=self.bot.config.get("spotify_client_id"),
                spotify_client_secret=self.bot.config.get("spotify_client_secret"),
                identifier="MAIN",
            )
            music_logger.info(f"Sucessfully created Node: {node._identifier}")
        except (pomice.NodeCreationError, pomice.NodeConnectionFailure) as e:
            music_logger.error(f"Error while creating Node. Unloading cog now...\n{e}")
            await self.cog_unload()

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: Player, track: pomice.Track, _):
        try:
            await player.play(player.queue.get())
        except pomice.QueueEmpty:
            await asyncio.sleep(60)
            if not player.current and not player.queue:
                await player.destroy()

    @commands.Cog.listener()
    async def on_pomice_track_stuck(self, player: Player, track, _):
        try:
            await player.play(player.queue.get())
        except pomice.QueueEmpty:
            await player.destroy()

    @commands.Cog.listener()
    async def on_pomice_track_exception(self, player: Player, track, _):
        try:
            await player.play(player.queue.get())
        except pomice.QueueEmpty:
            await player.destroy()

    @commands.command(aliases=["join", "con"])
    async def connect(self, ctx: AsahiContext):
        """Connect the bot to your current voice channel"""
        if self.is_vc_joinable(ctx):
            await ctx.author.voice.channel.connect(cls=Player)
        else:
            return await ctx.send_error("Cannot join voice channel")

    @commands.command(aliases=["enqueue"])
    async def play(self, ctx: AsahiContext, *, query: str):
        """Play or enqueue a song"""
        if ctx.me.voice is None and ctx.author.voice is not None:
            await ctx.invoke(self.connect)
        if not ctx.author.voice:
            return await ctx.send_error("You are not in a voice channel.")
        player: Player = ctx.voice_client

        results: Union[Playlist, list[Track]] = await player.get_tracks(query, ctx=ctx)
        if not results:
            return await ctx.send_error(f"No tracks found with the query '{query}'")

        if isinstance(results, Playlist):
            for track in results.tracks:
                player.queue.put(track)
            await ctx.send_ok(f"Added {results.track_count} tracks to the queue")
            if not player.is_playing:
                await player.play(player.queue.get())
                await ctx.send_ok(f"Now playing {player.current.title} from {player.current.author}")
            return

        else:
            if len(results) == 1:
                trk = results.pop(0)
                if player.is_playing:
                    player.queue.put(trk)
                    await ctx.send_ok(f"Added {trk.title} from {trk.author} to the queue")
                    return
                await player.play(trk)
                await ctx.send_ok(f"Now playing {trk.title} from {trk.author}")
            else:
                await ctx.send(
                    embed=discord.Embed(
                        title=f"Results for query '{query[:50]}'",
                        description="Select one of the options below to play",
                        color=self.bot.ok_color,
                    ),
                    view=MusicView(ctx, results),
                )

    @commands.command(aliases=["q"])
    async def queue(self, ctx: AsahiContext):
        """Show the current music queue"""
        player: Player = ctx.voice_client
        if not player:
            return await ctx.send_error("No Music Player found for this guild.")
        if not player.queue:
            return await ctx.send_info("No tracks left in queue.")

        queue_length: str = humanize_timedelta(timedelta(milliseconds=sum([int(i.length) for i in player.queue])))
        track_list: list[list[Track]] = list(chunk_list(list(player.queue), 8))
        embeds = [
            discord.Embed(
                description="\n".join([f"{trk.title[:50]} - {trk.author[:50]}" for trk in _list]),
                color=self.bot.info_color,
            )
            .set_footer(text=f"Vol: {player.volume}% | Track Count: {len(player.queue)} | Length: {queue_length}")
            .set_author(name=f"Current song {player.current.title[:50]} - {player.current.author[:25]}")
            .set_thumbnail(url=ctx.guild.icon.url)
            for _list in track_list
        ]
        await Paginator(embeds).start(ctx)

    @commands.command(aliases=["np"])
    async def nowplaying(self, ctx: AsahiContext):
        """Shows information about the currently playing song"""
        player: Player = ctx.voice_client
        if not player:
            return await ctx.send_error("No Music Player found for this guild.")
        if not player.current:
            return await ctx.send_error("There is no song currently playing")
        await ctx.send(
            embed=discord.Embed(
                title=player.current.title,
                url=player.current.uri,
                description=f"From: {player.current.author}",
                color=self.bot.ok_color,
            )
            .add_field(
                name="Length",
                value=humanize_timedelta(timedelta(milliseconds=player.current.length)),
            )
            .add_field(name="Requester", value=player.current.requester)
            .set_thumbnail(url=player.current.thumbnail)
        )

    @commands.command(aliases=["leave", "gtfo", "fuckoff", "dc"])
    async def disconnect(
        self,
        ctx: AsahiContext,
    ):
        """Disconnect from my current vc"""
        player: Player = ctx.voice_client

        if not player:
            return await ctx.send_error("Currently not connected to any VCs right now.")

        await player.destroy()
        await ctx.send_info("Disconnected")

    @commands.command(aliases=["next"])
    async def skip(self, ctx: AsahiContext):
        """Skip to the next song in queue"""
        player: Player = ctx.voice_client

        if not player:
            return await ctx.send_error("There is no active player.")
        if ctx.author not in ctx.guild.me.voice.channel.members:
            return await ctx.send_error("You must be in the same voice chat as me to use this command.")
        await player.stop()
        await ctx.message.add_reaction("✅")

    @commands.command(aliases=["stop"])
    async def pause(self, ctx: AsahiContext):
        """Pause the current track"""
        player: Player = ctx.voice_client

        if not player:
            return await ctx.send_error("There is no activate player.")

        await player.set_pause(True)
        await ctx.send_ok("Paused current track")

    @commands.command(aliases=["resume"])
    async def unpause(self, ctx: AsahiContext):
        """Unpause the current track"""
        player: Player = ctx.voice_client
        if not player:
            return await ctx.send_error("There is no activate player.")

        await player.set_pause(False)
        await ctx.send_ok("Unpaused current track")

    @commands.command(aliases=["vol"])
    async def volume(self, ctx: AsahiContext, vol: int):
        """Set the volume of the current music player"""
        player: Player = ctx.voice_client
        if not player:
            return await ctx.send_error("There is no activate player.")

        if vol < 0 or vol > 100:
            return await ctx.send_error("Volume must be between 1 or 100")
        await player.set_volume(vol)
        await ctx.send_ok(f"Set player volume to {player.volume}")

    @commands.command(aliases=["loop"])
    async def repeat(self, ctx: AsahiContext):
        """Repeats/loops the current song"""
        player: Player = ctx.voice_client
        if not player:
            return await ctx.send_error("There is no active player")

        if player.queue.loop_mode is None:
            player.queue.set_loop_mode(LoopMode.TRACK)
            await ctx.send_ok("Now repeating the current track")
            return
        if player.queue.loop_mode is LoopMode.TRACK:
            player.queue.set_loop_mode(LoopMode.QUEUE)
            await ctx.send_ok("Now looping the queue")
            return
        if player.queue.loop_mode is LoopMode.QUEUE:
            player.queue.set_loop_mode(None)
            await ctx.send_ok("Disabled looping")
            return


async def setup(bot: Asahi):
    await bot.add_cog(Music(bot))
