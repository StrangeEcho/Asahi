from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu import Kurisu


SCHEMA = """
CREATE TABLE IF NOT EXISTS guildsettings (guild BIGINT PRIMARY KEY, prefix VARCHAR(10))
;;
CREATE TABLE IF NOT EXISTS warnings (user BIGINT, reason VARCHAR(200), guild BIGINT, moderator VARCHAR)
;;
CREATE TABLE IF NOT EXISTS afk (user BIGINT PRIMARY KEY, message VARCHAR(200), toggled INTEGER DEFAULT 0)
;;
CREATE TABLE IF NOT EXISTS suppressed (guild BIGINT NOT NULL)
;;
CREATE TABLE IF NOT EXISTS todo (user INTEGER BIGINT, item VARCHAR(150))
 """


class PrefixManager:
    def __init__(self, bot: Kurisu):
        self.bot = bot

    async def add_prefix(self, guild: int, prefix: str):
        """Add a prefix to cache and DB"""
        self.bot.prefixes[guild] = prefix

        await self.bot.db.execute(
            query="INSERT INTO guildsettings (guild, prefix) VALUES (:guild, :prefix) ON CONFLICT(guild) DO UPDATE SET prefix = :update_prefix",  # noqa e501
            values={
                "guild": guild,
                "prefix": prefix,
                "update_prefix": prefix,
            },
        )

    async def remove_prefix(self, guild: int):
        """Removes custom prefix from cache and DB"""
        if guild not in self.bot.prefixes.keys():
            raise KeyError("No custom prefixes for this guild were found.")

        del self.bot.prefixes[guild]
        await self.bot.db.execute(
            "DELETE FROM guildsettings WHERE guild = :guild",
            {"guild": guild},
        )

    async def startup_caching(self):
        """Append prefixes from DB to cache"""
        for g, p in await self.bot.db.fetch_all("SELECT guild, prefix FROM guildsettings"):
            self.bot.prefixes.setdefault(g, p)
            self.bot.logger.info("Finished appending prefixes into memory.")


class ErrorSuppressionHandler:
    def __init__(self, bot: Kurisu):
        self.bot = bot

    async def insert(self, id: int) -> None:
        """Insert a guild id into suppressed guilds list"""
        await self.bot.db.execute(
            "INSERT INTO suppressed (guild) VALUES (:guild)",
            {"guild": id},
        )

    async def fetch_all(self) -> list[tuple[int]]:
        """Reteive a list of IDS of all guilds that are suppressed"""
        return await self.bot.db.fetch_all(
            "SELECT * FROM suppressed",
        )

    async def remove(self, id: int) -> None:
        """Remove a guild id into suppressed guilds list"""
        await self.bot.db.execute(
            "DELETE FROM suppressed WHERE guild = :guild",
            {"guild": id},
        )
