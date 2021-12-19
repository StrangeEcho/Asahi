from datetime import timedelta
import asyncio

from discord.ext import commands, vbu
from tabulate import tabulate
import discord
import lavalink

from utils.context import KurisuContext
from utils.funcs import box, parse_llnode_stat
from utils.kurisu import KurisuBot


class Music(commands.Cog):
    """Play your favorite tunes with these commands!!!"""

    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.bot.loop.create_task(self.node_init())
        self.ll_ip = self.bot.get_config("config", "music", "ll_host")
        self.ll_ws_port = self.bot.get_config("config", "music", "ll_port")
        self.ll_password = self.bot.get_config(
            "config", "music", "ll_password"
        )

    async def node_init(self):
        """Initialize LavaLink Node"""
        try:
            await lavalink.initialize(
                bot=self.bot,
                host=self.ll_ip,
                ws_port=self.ll_ws_port,
                password=self.ll_password,
            )
            self.bot.logger.info(
                f"Initialized LavaLink Node\nIP: {self.ll_ip}\nPort: {self.ll_ws_port}"
            )
        except:
            self.bot.logger.warning(
                "Error thrown in Music Init. This usually means theres an error in your ll credentials.\nUnloading Cog Now."
            )
            self.cog_unload()

    @commands.command(name="connect")
    async def _conenct(self, ctx: KurisuContext):
        """Connect the bot to your vc"""
        if not ctx.author.voice:
            return await ctx.send_error(
                "You must be in a vc to use this command."
            )
        if not ctx.author.voice.channel.permissions_for(ctx.me).connect:
            return await ctx.send(
                "I do not have permission to join that channel."
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
        if not ct:
            return await ctx.send_error(
                "There is currently no song playing right now."
            )
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
        if player.current:
            await ctx.send_ok(f"Now Playing {player.current.title}")
        else:
            await ctx.send_ok("Nothing left in queue.")

    @commands.command()
    @commands.is_owner()
    async def llnodestats(self, ctx: commands.Context):
        """Get Lavalink Node Stats"""
        nodes = lavalink.node.get_nodes_stats()
        if not nodes:
            await ctx.send("No nodes found.")
            return

        stats = [stat for stat in dir(nodes[0]) if not stat.startswith("_")]
        tabs = []
        for i, n in enumerate(nodes, start=1):
            tabs.append(
                f"Node {i}/{len(nodes)}\n"
                + box(
                    tabulate(
                        [
                            (
                                stat.replace("_", " ").title(),
                                await parse_llnode_stat(n, stat),
                            )
                            for stat in stats
                        ],
                    ),
                    "ml",
                )
            )

        if len(tabs) != 1:
            await vbu.Paginator(tabs, per_page=1).start(ctx, timeout=45)
        else:
            await ctx.send(tabs[0])

    @commands.command()
    async def volume(self, ctx: KurisuContext, vol: int = None):
        """Change Volume"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send_error("No Activate Players")
        if not vol:
            return await ctx.send(f"Current Volume: {player.volume}")
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
        if not player.queue:
            return await ctx.send_error("Nothing in the queue to shuffle.")
        if not player.shuffle:
            player.shuffle = True
            return await ctx.send_ok("Repeating Queue")
        if player.shuffle:
            player.shuffle = False
            return await ctx.send_ok("No longer repeating queue")

    @commands.command(aliases=["p"])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def play(self, ctx: KurisuContext, *, query: str):
        """Play a song"""
        if not ctx.author.voice:
            return await ctx.send_error(
                "You must be in a vc to use this command."
            )
        if not ctx.author.voice.channel.permissions_for(ctx.me).connect:
            return await ctx.send(
                "I do not have permission to join that channel."
            )

        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            player = await lavalink.connect(ctx.author.voice.channel, True)
        async with ctx.typing():
            tracks = await player.search_yt(query)
        if not tracks.tracks:
            return await ctx.send_error("No Tracks Found")

        if len(tracks.tracks) == 1:
            player.add(ctx.author, tracks.tracks[0])
            if player.is_playing:
                await ctx.send_ok(
                    f"Added {tracks.tracks[0].title} to the queue"
                )
            else:
                await ctx.send_ok(f"Now playing {tracks.tracks[0].title}")
            if not player.current:
                await player.play()
            return

        track_options = []

        for x, v in enumerate(tracks.tracks[:5], 1):
            track_options.append(
                discord.ui.SelectOption(
                    label=v.title[:100],
                    description=f"Length: {timedelta(milliseconds=v.length)}",
                    value=str(x),
                )
            )
        embed = discord.Embed(
            description="Use the select menu below to choose an song to play.",
            color=self.bot.ok_color,
            timestamp=discord.utils.utcnow(),
        )
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.SelectMenu(
                    custom_id="MUSIC_TRACK",
                    options=track_options,
                    placeholder="Select a song",
                ),
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="cancel",
                    style=discord.ui.ButtonStyle.danger,
                    custom_id="CLOSE_MENU",
                )
            ),
        )
        msg = await ctx.send(embed=embed, components=components)

        def check(payload: discord.Interaction):
            if payload.message.id != msg.id:
                return False
            if payload.user.id not in (*ctx.bot.owner_ids, ctx.author.id):
                self.bot.loop.create_task(
                    payload.response.send_message(
                        "You can't use this select!",
                        ephemeral=True,
                    )
                )
                return False
            return True

        try:
            payload = await self.bot.wait_for(
                "component_interaction", check=check, timeout=60
            )
        except asyncio.TimeoutError:
            embed.description = (
                "Timed out... Choose an song before Christmas comes."
            )
            return await msg.edit(embed=embed, components=None)
        if payload.component.custom_id == "CLOSE_MENU":
            embed.description = (
                "Why did you try to play a song at the first place?"
            )
            return await msg.edit(embed=embed, components=None)

        await msg.delete()

        a_int = int(payload.values[0]) - 1
        player.add(ctx.author, tracks.tracks[a_int])
        if player.is_playing:
            await ctx.send_ok(
                f"Added {tracks.tracks[a_int].title} to the queue."
            )
        else:
            await ctx.send_ok(f"Now Playing {tracks.tracks[a_int].title}")
        if not player.current:
            await player.play()

    @commands.command(aliases=["pause"])
    async def stop(self, ctx: KurisuContext):
        """Stop or pause the current song"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send_error("No player found")
        await player.stop()

    @commands.command()
    async def resume(self, ctx: KurisuContext):
        """Stop or pause the current song"""
        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await ctx.send_error("No player found")
        await player.resume(player.current)

    @commands.command()
    async def disconnect(self, ctx: KurisuContext):
        """Disconnect me from vc"""
        if not ctx.me.voice:
            return ctx.send_error("I am not connected to any vc.")
        if not ctx.author in ctx.me.voice.channel.members:
            return await ctx.send_error(
                "You must be in the same vc as me to disconnect me."
            )
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
        total_time = 0
        for time in [i.length for i in player.queue]:
            total_time += time
        await ctx.send(
            embed=discord.Embed(
                title=f"Queue For {ctx.guild.name}",
                description=f"Total Tracks: {len(player.queue)}\nTotal Track Time: {timedelta(milliseconds=total_time)}",
                color=self.bot.ok_color,
            ).add_field(
                name="Tracks",
                value="\n".join(
                    [f"{x}. {v.title}" for x, v in enumerate(player.queue, 1)]
                ),
            )
        )


def setup(bot):
    bot.add_cog(Music(bot))
