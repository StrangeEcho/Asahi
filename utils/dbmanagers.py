from discord.ext import commands

from .kurisu import KurisuBot


class PrefixManager:
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    async def add_prefix(self, guild: int, prefix: str):
        await self.bot.db.execute(
            query="INSERT INTO guildsettings (guild, prefix) VALUES (:guild, :prefix) ON CONFLICT(guild) DO UPDATE SET prefix = :update_prefix",
            values={
                "guild": guild,
                "prefix": prefix,
                "update_prefix": prefix,
            },
        )
        self.bot.prefixes[str(guild)] = prefix

    async def remove_prefix(self, guild: int):
        if str(guild) in self.bot.prefixes:
            self.bot.prefixes.pop(str(guild))
            await self.bot.db.execute(
                query="DELETE FROM guildsettings WHERE guild = :guild_id",
                values={
                    "guild_id": guild,
                },
            )

    async def startup_caching(self):
        for g, p in await self.bot.db.fetch_all(query="SELECT guild, prefix FROM guildsettings"):
            self.bot.prefixes.setdefault(str(g), str(p))
            self.bot.logger.info("Prefixes Appended To Cache")


class WarningManager:
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    async def add_warning(self, ctx: commands.Context, userid: int, reason: str):
        """Insert a warning for a user"""

        await self.bot.db.execute(
            query="INSERT INTO warnings (user, reason, guild, moderator) VALUES (:user, :reason, :guild, :moderator)",
            values={
                "user": userid,
                "reason": reason,
                "guild": ctx.guild.id,
                "moderator": ctx.author.id,
            },
        )

    async def fetch_warnings(self, userid: int, guild: int):
        """Fetch all warnings for a user within the guild passed in"""
        warnings = await self.bot.db.fetch_all(
            query="SELECT reason, moderator, guild FROM warnings WHERE user = :userid AND guild = :guild",
            values={"userid": userid, "guild": guild},
        )
        return warnings

    async def remove_warning(self, user: int, warning: int, server: int):
        idkanymore = await self.fetch_warnings(user, server)

        try:
            something = idkanymore[warning - 1]
        except IndexError:
            raise commands.BadArgument("You tried to clear a invalid warning")

        await self.bot.db.execute(
            query="DELETE FROM warnings WHERE user = :user AND reason = :warning AND guild = :guild",
            values={"user": user, "warning": something[0], "guild": server},
        )
