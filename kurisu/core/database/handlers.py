import logging

from core import KurisuBot, KurisuContext
from discord.ext import commands
from utilities.errors import ItemNotFound


class PrefixManager:
    def __init__(self, bot: KurisuBot):
        self.bot = bot
        self.logger = logging.getLogger("core.database")

    async def add_prefix(self, guild: int, prefix: str) -> None:
        await self.bot.db.execute(
            "INSERT INTO GuildSettings (prefix) VALUES (?) WHERE guild = ? ON CONFLICT guild DO UPDATE SET prefix = ?",
            (prefix, guild, prefix),
        )
        self.bot.prefix[guild] = prefix  # Update in cache
        self.logger.info(f"Set prefix to '{prefix}' at guild '{guild}'")

    async def remove_prefix(self, guild: int) -> None:
        if (
            guild in self.bot.prefixes
        ):  # Any guild with a custom prefix will be in cache
            await self.bot.db.execute(
                "DELETE FROM GuildSettings WHERE guild = ?", (guild,)
            )
            self.logger.info(f"Removed GuildSetting at guild '{guild}'")
        else:
            raise ItemNotFound(f"No guild Column found with ID '{guild}'")


class AFKManager:
    def __init__(self, bot: KurisuBot):
        self.bot = bot

    async def insert_or_update(self, user: int, afk_message: str) -> None:
        """Insert or Update a users afk message in DB"""
        await self.bot.db.execute(
            "INSERT INTO afk (user, message) VALUES (?, ?) ON CONFLICT(user) DO UPDATE set message = ?",
            (user, afk_message, afk_message),
        )

    async def toggle_afk(self, user: int) -> None:
        data = await self.fetch_afk(user)

        if data[1] == 0:
            await self.bot.db.execute(
                "UPDATE afk SET toggled = 1 WHERE user = ?",
                (user,),
            )

        if data[1] == 1:
            await self.bot.db.execute(
                query="UPDATE afk SET toggled = 0 WHERE user = ?",
                values={"user": user},
            )

    async def fetch_afk(self, user: int) -> tuple[str, int]:
        """Fetch a users afk message from db"""
        data = await self.bot.db.fetch_one(
            "SELECT message, toggled FROM afk WHERE user = ?",
            (user,),
        )
        if not data:
            raise ItemNotFound("No Data found for this user")
        return data
