from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu import Kurisu


class PrefixManager:
    def __init__(self, bot: Kurisu):
        self.bot = bot

    async def add_prefix(self, guild_id: int, prefix: str):
        """Add a prefix to cache and DB"""

        self.bot.prefixes[guild_id] = prefix
        await self.bot.db.execute(
            query="INSERT INTO guildsettings (guild, prefix) VALUES (:guild, :prefix) ON CONFLICT(guild) DO UPDATE SET prefix = :update_prefix",  # noqa e501
            values={"guild": guild_id, "prefix": prefix, "update_prefix": prefix},
        )

    async def remove_prefix(self, guild_id: int):
        """Removes custom prefix from cache and DB"""

        if guild_id not in self.bot.prefixes.keys():
            raise KeyError("No custom prefixes for this guild were found.")

        del self.bot.prefixes[guild_id]
        await self.bot.db.execute("DELETE FROM guildsettings WHERE guild = :guild", {"guild": guild_id})

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
        await self.bot.db.execute("INSERT INTO suppressed (guild) VALUES (:guild)", {"guild": id})

    async def fetch_all(self) -> list[tuple[int]]:
        """Reteive a list of IDS of all guilds that are suppressed"""
        return await self.bot.db.fetch_all("SELECT * FROM suppressed")

    async def remove(self, id: int) -> None:
        """Remove a guild id into suppressed guilds list"""
        await self.bot.db.execute("DELETE FROM suppressed WHERE guild = :guild", {"guild": id})
