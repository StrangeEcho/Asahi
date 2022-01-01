from discord.ext import commands

from .errors import UserNotFound
from .kurisu import KurisuBot


class PrefixManager:
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    async def add_prefix(self, guild: int, prefix: str) -> None:
        await self.bot.db.execute(
            query="INSERT INTO guildsettings (guild, prefix) VALUES (:guild, :prefix) ON CONFLICT(guild) DO UPDATE SET prefix = :update_prefix",
            values={
                "guild": guild,
                "prefix": prefix,
                "update_prefix": prefix,
            },
        )
        self.bot.prefixes[str(guild)] = prefix

    async def remove_prefix(self, guild: int) -> None:
        if str(guild) in self.bot.prefixes:
            self.bot.prefixes.pop(str(guild))
            await self.bot.db.execute(
                query="DELETE FROM guildsettings WHERE guild = :guild_id",
                values={
                    "guild_id": guild,
                },
            )

    async def startup_caching(self) -> None:
        for g, p in await self.bot.db.fetch_all(
                query="SELECT guild, prefix FROM guildsettings"
        ):
            self.bot.prefixes.setdefault(str(g), str(p))
            self.bot.logger.info("Prefixes Appended To Cache")


class WarningManager:
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    async def add_warning(
            self, ctx: commands.Context, userid: int, reason: str
    ) -> None:
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

    async def insert_or_update(self, user: int, afk_message: str) -> None:
        """Insert or Update a users afk message in DB"""
        await self.bot.db.execute(
            query="INSERT INTO afk (user, message) VALUES (:user, :message) ON CONFLICT(user) DO UPDATE set message = :msg",
            values={"user": user, "message": afk_message, "msg": afk_message},
        )

    async def toggle_afk(self, user: int) -> None | UserNotFound:
        data = await self.fetch_afk(user)

        if data[1] == 0:
            await self.bot.db.execute(
                query="UPDATE afk SET toggled = 1 WHERE user = :user",
                values={"user": user},
            )

        if data[1] == 1:
            await self.bot.db.execute(
                query="UPDATE afk SET toggled = 0 WHERE user = :user",
                values={"user": user},
            )

    async def fetch_afk(self, user: int) -> tuple[str, int]:
        """Fetch a users afk message from db"""
        data = await self.bot.db.fetch_one(
            query="SELECT message, toggled FROM afk WHERE user = :user",
            values={"user": user},
        )
        if not data:
            raise UserNotFound("No Data found for this user")
        return data


class ErrorSuppressionHandler:
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    async def insert(self, id: int) -> None:
        """Insert a guild id into suppressed guilds list"""
        await self.bot.db.execute(
            query="INSERT INTO suppressed (guild) VALUES (:guild)",
            values={"guild": id},
        )

    async def fetch_all(self) -> list[tuple[int]]:
        """Reteive a list of IDS of all guilds that are suppressed"""
        return await self.bot.db.fetch_all(
            query="SELECT * FROM suppressed",
        )

    async def remove(self, id: int) -> None:
        """Remove a guild id into suppressed guilds list"""
        await self.bot.db.execute(
            query="DELETE FROM suppressed WHERE guild = :guild",
            values={"guild": id},
        )


class TodoManager:
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    async def add_todo(self, user: int, item: str) -> None:
        """Insert a todo item"""
        await self.bot.db.execute(
            query="INSERT INTO todo (user, item) VALUES (:user, :item)",
            values={"user": user, "item": item},
        )

    async def fetch_todos(self, user: int):
        """Fetch all todo items for a user"""
        return await self.bot.db.fetch_all(
            query="SELECT item FROM todo WHERE user = :user",
            values={"user": user},
        )

    async def remove_todo(self, user: int, item_number: int):
        tuplist = await self.fetch_todos(user)

        try:
            target_tup = tuplist[item_number - 1]
        except IndexError:
            raise commands.BadArgument("You tried to clear a invalid warning")

        await self.bot.db.execute(
            query="DELETE FROM todo WHERE user = :user AND item = :item",
            values={"user": user, "item": target_tup[0]},
        )
