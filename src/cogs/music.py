import asyncio
from datetime import timedelta

import pomice
import discord
from discord.ext import commands
from kurisu import Kurisu, KurisuContext
from exts import do_music, Player, humanize_timedelta


class Music(
    commands.Cog, command_attrs={"cooldown": commands.CooldownMapping.from_cooldown(1, 2.5, commands.BucketType.user)}
):
    """Play your favorite tunes"""

    def __init__(self, bot: Kurisu):
        self.bot = bot
        self.bot.loop.create_task(self.ll_init())

    async def ll_init(self) -> None:
        self.bot.logger.info("Attempting to create LL nodes.")
        await self.bot.wait_until_ready()
        try:
            await self.bot.node_pool.create_node(
                bot=self.bot,
                host=self.bot.config.get("ll_host"),
                port=self.bot.config.get("ll_port"),
                password=self.bot.config.get("ll_password"),
                spotify_client_id=self.bot.config.get("spotify_client_id"),
                spotify_client_secret=self.bot.config.get("spotify_client_secret"),
                identifier="MAIN",
            )
            self.bot.logger.info("Sucessfully created LL nodes.")
        except pomice.NodeCreationError as e:
            self.bot.logger.error(f"Error while creating LL nodes\nError:\n{e}")
            self.cog_unload()

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: Player, track, _):
        try:
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

    @commands.command(aliases=["summon", "join"])
    async def connect(self, ctx: KurisuContext):
        """Connect the bot to a VC"""
        if not ctx.author.voice:
            return await ctx.send_error("You are not connected to a VC.")
        if not ctx.author.voice.channel.permissions_for(ctx.me).connect:
            return await ctx.send_error("I am not able to join that voice channel.")

        try:
            await ctx.author.voice.channel.connect(cls=Player)
        except discord.ClientException as e:
            return await ctx.send_error(e)

    @commands.command(aliases=["queueadd"])
    @commands.cooldown(1, 3.5, commands.BucketType.user)
    async def play(self, ctx: KurisuContext, *, query: str):
        """Play a song"""
        if not ctx.author.voice:
            return await ctx.send_error("You are not connected to a VC.")
        if not ctx.author.voice.channel.permissions_for(ctx.me).connect:
            return await ctx.send_error("I am not able to join that voice channel.")

        try:
            await ctx.author.voice.channel.connect(cls=Player)
        except discord.ClientException:
            pass

        await do_music(ctx, query)

    @commands.command(aliases=["q"])
    async def queue(self, ctx: KurisuContext):
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
    async def nowplaying(self, ctx: KurisuContext):
        """Shows information about the currently playing song"""
        player: Player = ctx.voice_client
        if not player:
            return await ctx.send_error("No Music Player found for this guild.")
        await ctx.send(
            embed=discord.Embed(
                title=player.current.title,
                url=player.current.uri,
                description=f"From: {player.current.author}",
                color=self.bot.ok_color,
            )
            .add_field(name="Length", value=humanize_timedelta(timedelta(milliseconds=player.current.length)))
            .add_field(name="Requester", value=player.current.requester)
            .set_thumbnail(url=player.current.thumbnail)
        )

    @commands.command(aliases=["leave", "gtfo", "fuckoff"])
    async def disconnect(
        self,
        ctx: KurisuContext,
    ):
        """Disconnect from my current vc"""
        player: Player = ctx.voice_client

        if not player:
            return await ctx.send_error("Currently not connected to any VCs right now.")

        await player.destroy()
        await ctx.send_info("Disconnected")

    @commands.command(aliases=["next"])
    async def skip(self, ctx: KurisuContext):
        """Skip to the next song in queue"""
        player: Player = ctx.voice_client

        if not player:
            return await ctx.send_error("There is no activate player.")
        if ctx.author not in ctx.guild.me.voice.channel.members:
            return await ctx.send_error("You must be in the same voice chat as me to use this command.")

        await player.stop()

    @commands.command(aliases=["stop"])
    async def pause(self, ctx: KurisuContext):
        """Pause the current track"""
        player: Player = ctx.voice_client

        if not player:
            return await ctx.send_error("There is no activate player.")

        await player.set_pause(True)
        await ctx.send_ok("Paused current track")

    @commands.command(aliases=["resume"])
    async def unpause(self, ctx: KurisuContext):
        """Unpause the current track"""
        player: Player = ctx.voice_client
        if not player:
            return await ctx.send_error("There is no activate player.")

        await player.set_pause(False)
        await ctx.send_ok("Unpaused current track")

    @commands.command(aliases=["remtrack"])
    async def removetrack(self, ctx: KurisuContext, index: int = 1):
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
    async def volume(self, ctx: KurisuContext, vol: int):
        """Set the volume of the current music player"""
        player: Player = ctx.voice_client
        if not player:
            return await ctx.send_error("There is no activate player.")

        if vol < 0 or vol > 100:
            return await ctx.send_error("Volume must be between 1 or 100")
        await player.set_volume(vol)
        await ctx.send_ok(f"Set player volume to {player.volume}")


def setup(bot: Kurisu):
    bot.add_cog(Music(bot))
