from datetime import timedelta
import asyncio

from discord.ext import commands
from utils.context import KurisuContext
from utils.kurisu import KurisuBot
import discord
import pomice

from .ext.player import Player


class Music(commands.Cog):
    """Play your favorite tunes"""

    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.bot.loop.create_task(self.start_nodes())
        self.pomice = pomice.NodePool()
        self.ll_host = self.bot.get_config("config", "music", "ll_host")
        self.ll_port = self.bot.get_config("config", "music", "ll_port")
        self.ll_password = self.bot.get_config(
            "config", "music", "ll_password"
        )
        self.spot_cid = self.bot.get_config(
            "config", "music", "spot_client_id"
        )
        self.spot_cs = self.bot.get_config(
            "config", "music", "spot_client_sec"
        )

    async def start_nodes(self) -> None:
        """Start ll nodes"""
        self.bot.logger.info("Attempting to create LL nodes.")
        try:
            await self.pomice.create_node(
                bot=self.bot,
                host=self.ll_host,
                port=str(self.ll_port),
                password=self.ll_password,
                spotify_client_id=self.spot_cid,
                spotify_client_secret=self.spot_cs,
                identifier="MAIN",
            )
            self.bot.logger.info("Sucessfully created LL nodes.")
        except pomice.NodeCreationError as e:
            self.bot.logger.error(
                f"Error while creating LL nodes\nError:\n{e}"
            )
            self.cog_unload()

    def check_connection_perms(ctx: KurisuContext) -> bool:
        if not ctx.author.voice:
            return False
        if not ctx.author.voice.channel.permissions_for(ctx.me).connect:
            return False
        else:
            return True

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: Player, track, _):
        try:
            await player.play(player.queue.pop(0))
        except IndexError:
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

    @commands.command(aliases=["summon", "connect"])
    @commands.check(check_connection_perms)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def join(self, ctx: KurisuContext):
        """Have the bot join your voice channel"""

        if ctx.voice_client:
            return await ctx.send_error("Im already connected to a VC.")

        if not ctx.author.voice:
            return await ctx.send_error(
                "You are currently not in a Voice Channel"
            )

        await ctx.author.voice.channel.connect(cls=Player)
        await ctx.guild.me.edit(deafen=True)
        await ctx.send(f"Sucessfully joined `{ctx.author.voice.channel.name}`")

    @commands.command(aliases=["queue"])
    @commands.check(check_connection_perms)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def play(self, ctx: KurisuContext, *, query: str):
        """Play a song"""
        if not ctx.guild.voice_client:
            await ctx.invoke(self.join)

        player: Player = ctx.voice_client

        results = await player.get_tracks(query=query, ctx=ctx)

        if not results:
            return await ctx.send_error("No results matching that query")

        if isinstance(results, pomice.Playlist):
            if player.current:
                for track in results.tracks:
                    player.queue.append(track)
                await ctx.send_ok(f"Added {results.track_count} to the queue")
                return
            for track in results.tracks:
                player.queue.append(track)
            await ctx.send_ok(f"Added {results.track_count} to the queue")
            await player.play(player.queue.pop(0))
            return

        if len(results) == 1:
            if player.current:
                player.queue.append(results[0])
                await ctx.send_ok(
                    f"Added {results[0].title[:80]} to the queue."
                )
                return
            await player.play(results[0])
            await ctx.send_ok(f"Now playing {results[0].title[:87]}")
            return

        dropdown_options: list[discord.ui.SelectOption] = []

        for num, track in enumerate(results[:5], 1):
            dropdown_options.append(
                discord.ui.SelectOption(
                    label=f"{num}. {track.title[:93]}", value=str(num)
                )
            )

        components: discord.ui.MessageComponents = (
            discord.ui.MessageComponents(
                discord.ui.ActionRow(
                    discord.ui.SelectMenu(
                        options=dropdown_options,
                        placeholder=f"Pick 1 of {len(dropdown_options)}",
                    )
                )
            )
        )
        msg = await ctx.send(
            embed=discord.Embed(
                description="Select here", color=self.bot.ok_color
            ),
            components=components,
        )

        def check(p: discord.Interaction):
            return p.message.id == msg.id and p.user.id == ctx.author.id

        try:
            payload: discord.Interaction = await self.bot.wait_for(
                "component_interaction", check=check, timeout=20
            )
            actual_track = results[int(payload.values[0]) - 1]
            await msg.delete()
            if player.current:
                player.queue.append(actual_track)
                await ctx.send_ok(f"Added {actual_track.title[:93]}")
                return
            await player.play(results[int(payload.values[0]) - 1])
            await ctx.send_ok(f"Now playing {player.current}")
        except asyncio.TimeoutError:
            components.disable_components()
            await msg.add_reaction("⏰")

    @commands.command(aliases=["leave", "gtfo", "fuckoff"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def disconnect(
            self,
            ctx: KurisuContext,
    ):
        """Disconnect from my current vc"""
        if not ctx.guild.voice_client:
            return await ctx.send_error(
                "Currently not connected to any VCs right now."
            )

        player: Player = ctx.voice_client

        await player.disconnect()
        await ctx.send(":ok_hand:")

    @commands.command(aliases=["next"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def skip(self, ctx: KurisuContext):
        """Skip to the next song in queue"""
        if not ctx.voice_client:
            return await ctx.send_error("There is no activate player.")
        if ctx.author not in ctx.guild.me.voice.channel.members:
            return await ctx.send_error(
                "You must be in the same voice chat as me to use this command."
            )

        player: Player = ctx.voice_client

        await player.stop()
        await ctx.send(
            "Skipping to the next song"
            if player.queue != 0
            else "Skipped. No more songs in queue"
        )

    @commands.command(aliases=["stop"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pause(self, ctx: KurisuContext):
        """Pause the current track"""
        if not ctx.voice_client:
            return await ctx.send_error("There is no activate player.")
        player: Player = ctx.voice_client
        await player.set_pause(True)
        await ctx.send_ok("Paused current track")

    @commands.command(aliases=["resume"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def unpause(self, ctx: KurisuContext):
        """Unpause the current track"""
        if not ctx.voice_client:
            return await ctx.send_error("There is no activate player.")
        player: Player = ctx.voice_client
        await player.set_pause(False)
        await ctx.send_ok("Unpaused current track")

    @commands.command(aliases=["np"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nowplaying(self, ctx: KurisuContext):
        """Shows the current playing track"""
        if not ctx.voice_client:
            return await ctx.send_error("There is no activate player.")
        player: Player = ctx.voice_client
        await ctx.send(
            embed=discord.Embed(
                title=f"[{player.current.title}]({player.current.uri})",
                description=f"Requested by {player.current.requester}",
                color=self.bot.ok_color,
            )
                .add_field(name="Author", value=player.current.author)
                .add_field(
                name="Length",
                value=str(timedelta(milliseconds=player.current.length)),
            )
                .set_thumbnail(
                url=player.current.thumbnail
                if player.current.thumbnail
                else player.current.requester.avatar.url
            )
        )

    @commands.command(aliases=["songlist", "lq"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def listqueue(self, ctx: KurisuContext):
        """Shows the current playing track"""
        if not ctx.voice_client:
            return await ctx.send_error("There is no activate player.")

        player: Player = ctx.voice_client

        if len(player.queue) == 0:
            return await ctx.send_error("Queue is currently empty")

        await ctx.send_ok(
            "\n".join(
                [
                    f"{n}. {t.title} - {t.author}"
                    for n, t in enumerate(player.queue, 1)
                ]
            )
        )

    @commands.command(aliases=["qc"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def queueclear(self, ctx: KurisuContext):
        """Clears the current music queue"""
        if not ctx.voice_client:
            return await ctx.send_error("There is no activate player.")

        player: Player = ctx.voice_client

        if len(player.queue) == 0:
            return await ctx.send_error("Queue is currently empty")

        player.queue.clear()
        await ctx.send_ok("Removed all items from the queue.")

    @commands.command(aliases=["remtrack"])
    @commands.cooldown(1, 2.5, commands.BucketType.user)
    async def removetrack(self, ctx: KurisuContext, index: int = 1):
        """Remove a single track from the music queue. If no index is provied, the first track in queue will be removed"""
        if not ctx.voice_client:
            return await ctx.send_error("There is no activate player.")

        player: Player = ctx.voice_client

        if len(player.queue) == 0:
            return await ctx.send_error("Queue is currently empty")
        try:
            item = player.queue.pop(index - 1)
            await ctx.send_ok(f"Removed {item.title[:92]}")
        except IndexError:
            return await ctx.send_error(
                "Error: You tried to remove an item from the queue that doesnt exist."
            )

    @commands.command(aliases=["vol"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def volume(self, ctx: KurisuContext, vol: int):
        """Set the volume of the current music player"""
        if not ctx.voice_client:
            return await ctx.send_error("There is no activate player.")

        player: Player = ctx

        if vol < 0 or vol > 100:
            return await ctx.send_error("Volume must be between 1 or 100")
        await player.set_volume(vol)
        await ctx.send_ok(f"Set player volume to {player.volume}")

    @commands.command(aliases=["ff"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def fastfoward(self, ctx: KurisuContext, queueposistion: int):
        """Fast foward to a specific spot in the queue. Will resume back to the least posistion in the queue after playing the fast-fowarded song"""
        if not ctx.voice_client:
            return await ctx.send_error("There is no activate player.")

        player: Player = ctx

        try:
            await player.play(player.queue[queueposistion - 1])
        except IndexError:
            return await ctx.send_error(
                "You tried to fast forward to a song thats not in the queue."
            )


def setup(bot: KurisuBot):
    bot.add_cog(Music(bot))
