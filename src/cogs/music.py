from datetime import timedelta
from typing import Any, Optional, Union
import asyncio
import logging

from discord.ext import commands
from discord.ui import Select, View
from pomice import Playlist, Track
import discord
import pomice

from core import Asahi, AsahiContext
from exts.helpers import humanize_timedelta


class VoiceConnectionError(commands.CommandError):
    def __init__(self, message: Optional[str] = None, *args: Any):
        message = message or "There was an error thrown while trying to connect to a voice channel."
        super().__init__(message, *args)


class Player(pomice.Player):
    """Subclass of Pomice Player, adding a queue implementation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop: bool = False
        self._queue: list[pomice.Track] = []

    @property
    def queue(self) -> list[pomice.Track]:
        return self._queue


class MusicNavigator(Select):
    def __init__(self, ctx: AsahiContext, tracks: list[pomice.Track]):
        self.selections: list[discord.SelectOption] = []
        self.ctx = ctx
        self.tracks = tracks
        for num, track in enumerate(self.tracks[:5], 1):
            self.selections.append(
                discord.SelectOption(
                    label=f"{num}. {track.title[:50]}",
                    description=f"From {track.author[:50]}",
                    value=str(num - 1),
                )
            )
        super().__init__(placeholder="Select A Song To Play Here!", options=self.selections)

    async def callback(self, inter: discord.Interaction) -> Optional[discord.Message]:
        if inter.user.id != self.ctx.author.id:
            return await inter.response.send_message("You are not able to respond to this select menu", ephemeral=True)

        player: Player = self.ctx.voice_client
        track = self.tracks[int(self.values[0])]

        if player.is_playing:
            player.queue.append(track)
            await inter.response.send_message(f"Added {track.title[:50]} from {track.author[:25]} to the queue.")
        else:
            await player.play(track)
            await inter.response.send_message(f"Now playing {track.title[:50]} from {track.author[:25]}")


class MusicView(View):
    def __init__(self, ctx: AsahiContext, tracks: list[pomice.Track]):
        super().__init__(timeout=16)
        self.add_item(MusicNavigator(ctx, tracks))


class Music(
    commands.Cog,
    command_attrs={"cooldown": commands.CooldownMapping.from_cooldown(1, 3.5, commands.BucketType.user)},
):
    """All commands related to the bots music features"""

    def __init__(self, bot: Asahi):
        self.bot = bot
        self.logger = logging.getLogger("music-master")
        asyncio.get_running_loop().create_task(self.create_ll_connection())

    async def create_ll_connection(self) -> None:
        await self.bot.wait_until_ready()
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
            self.logger.info(f"Sucessfully created Node: {node._identifier}")
        except (pomice.NodeCreationError, pomice.NodeConnectionFailure) as e:
            self.logger.error(f"Error while creating Node. Unloading cog now...\n{e}")
            await self.cog_unload()

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: Player, track: pomice.Track, _):
        try:
            if player.loop:
                await player.play(track)
            else:
                await player.play(player.queue.pop(0))
        except IndexError:
            await asyncio.sleep(60)
            if not player.current and not player.queue:
                await player.destroy()

    @commands.Cog.listener()
    async def on_pomice_track_stuck(self, player: Player, track, _):
        try:
            await player.play(player.queue.pop(0))
        except IndexError:
            await player.destroy()

    @commands.Cog.listener()
    async def on_pomice_track_exception(self, player: Player, track, _):
        try:
            await player.play(player.queue.pop(0))
        except IndexError:
            await player.destroy()

    @commands.command()
    async def connect(self, ctx: AsahiContext):
        """Connect the bot to your current vc"""
        if not ctx.author.voice:
            raise VoiceConnectionError("You are not connected to any Voice Channels.")
        if not ctx.author.voice.channel.permissions_for(ctx.me).connect:
            raise VoiceConnectionError("Not able to join due to lack of permissions")
        await ctx.author.voice.channel.connect(cls=Player)
        await ctx.send_ok(f":white_check_mark: Connected to {ctx.author.voice.channel.name}")

    @commands.command(aliases=["enqueue"])
    async def play(self, ctx: AsahiContext, *, query: str):
        """Play or enqueue a song"""
        player: Player = ctx.voice_client
        if not player:
            try:
                await ctx.invoke(ctx.invoke(ctx.bot.get_command("connect")))
            except VoiceConnectionError as e:
                await ctx.send_error(e)
            player: Player = ctx.voice_client

        results: Union[Playlist, list[Track]] = await player.get_tracks(query, ctx=ctx)
        if not results:
            return await ctx.send_error(f"No tracks found with the query '{query}'")

        if isinstance(results, Playlist):
            for track in results.tracks:
                player.queue.append(track)
            await ctx.send_ok(f"Added {results.track_count} tracks to the queue")
            if not player.is_playing:
                await player.play(player.queue.pop(0))
                await ctx.send_ok(f"Now playing {player.current.title} from {player.current.author}")
            return

        else:
            if len(results) == 1:
                trk = results.pop(0)
                if player.is_playing:
                    player.queue.append(trk)
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

        queue_length = humanize_timedelta(timedelta(milliseconds=sum([int(i.length) for i in player.queue])))

        await ctx.send(
            embed=discord.Embed(
                title=f"Queue for {ctx.guild}",
                description="\n".join(
                    [f"{num}. {track.title} - {track.author}" for num, track in enumerate(player.queue, 1)]
                ),
                color=self.bot.info_color,
            )
            .set_footer(text=f"Vol: {player.volume}% | Track Count: {len(player.queue)} | Length: {queue_length}")
            .set_author(name=f"Current Song: {player.current.title}")
        )

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

    @commands.command(aliases=["leave", "gtfo", "fuckoff"])
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
            return await ctx.send_error("There is no activate player.")
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

    @commands.command(aliases=["remtrack"])
    async def removetrack(self, ctx: AsahiContext, index: int = 1):
        """Remove a single track from the music queue. If no index is provied, the first track in queue will be removed"""
        player: Player = ctx.voice_client

        if not player:
            return await ctx.send_error("There is no activate player.")

        if len(player.queue) == 0:
            return await ctx.send_error("Queue is currently empty")
        try:
            item = player.queue.pop(index - 1)
            await ctx.send_ok(f"Removed {item.title}")
        except IndexError:
            return await ctx.send_error("Error: You tried to remove an item from the queue that doesnt exist.")

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

    @commands.command()
    async def repeat(self, ctx: AsahiContext):
        """Repeats/loops the current song"""
        player: Player = ctx.voice_client
        if not player:
            return await ctx.send_error("There is no active player")

        if not player.current:
            return await ctx.send_error("There is currently nothing playing to repeat")

        player.loop = not player.loop
        if player.loop:
            await ctx.send_ok(f"Now repeating {player.current.title}")
        else:
            await ctx.send_ok("Looping is now disabled.")


async def setup(bot: Asahi):
    await bot.add_cog(Music(bot))
