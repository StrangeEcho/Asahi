from discord.ext import commands

from .errors import UserNotFound
from .kurisu import KurisuBot


class PrefixManager:
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    async def add_prefix(self, guild: int, prefix: str):
        await self.bot.db.execute(
            query="INSERT INTO guildsettings (guild, prefix) VALUES (:guild, :prefix) ON CONFLICT(guild) DO UPDATE afk SET prefix = :update_prefix",
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
        """Delete a warning row for a user"""
        tuplist = await self.fetch_warnings(user, server)

        try:
            target_tup = tuplist[warning - 1]
        except IndexError:
            raise commands.BadArgument("You tried to clear a invalid warning")

        await self.bot.db.execute(
            query="DELETE FROM warnings WHERE user = :user AND reason = :warning AND guild = :guild",
            values={"user": user, "warning": target_tup[0], "guild": server},
        )


class AFKManager:
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    async def insert_or_update(self, user: int, afk_message: str):
        """Insert or Update a users afk message in DB"""
        await self.bot.db.execute(
            query="INSERT INTO afk (user, message) VALUES (:user, :message) ON CONFLICT DO UPDATE SET message = :msg WHERE user = :usr",
            values={"user": user, "message": afk_message, "msg": afk_message, "usr": user},
        )

    async def toggle_afk(self, user: int):
        data = await self.fetch_afk(user)

        if data[1] == 0:
            await self.bot.db.execute(
                query="UPDATE afk SET toggled = 1 WHERE user = :user", values={"user": user}
            )

        if data[1] == 1:
            await self.bot.db.execute(
                query="UPDATE afk SET toggled = 0 WHERE user = :user", values={"user": user}
            )

    async def fetch_afk(self, user: int):
        """Fetch a users afk message from db"""
        data = await self.bot.db.fetch_one(
            query="SELECT message, toggled FROM afk WHERE user = :user", values={"user": user}
        )
        if not data:
            raise UserNotFound
        return data
