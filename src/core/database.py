import logging

from .bot import Asahi

LOGGER = logging.getLogger("database")


class PrefixHandler:
    def __init__(self, bot: Asahi):
        self.bot = bot

    async def add_prefix(self, prefix: str, guild: int) -> None:
        """Add a guild specific prefix to db and to cache"""
        if len(prefix) > 10:
            return LOGGER.error(f"Prefix assignmnent for {guild} errored out because prefix length was too large")
        await self.bot.db.execute(
            "INSERT INTO Guild_Settings (guild_id, prefix) VALUES(:guild, :prefix) ON CONFLICT(guild_id) DO UPDATE SET prefix = :u_prefix",
            values={"guild": guild, "prefix": prefix, "u_prefix": prefix},
        )
        self.bot.prefixes[guild] = prefix  # Add to cache
        LOGGER.info(f"Added custom prefix '{prefix}' for guild {guild}")

    async def remove_prefix(self, guild: int) -> None:
        """Remove a guild prefix from cache and db"""
        await self.bot.db.execute("DELETE FROM Guild_Settings WHERE guild_id = :guild", values={"guild": guild})
        del self.bot.prefixes[guild]  # Delete from cache
        LOGGER.info(f"Removed custom prefix for guild {guild}")


class MuteHandler:
    def __init__(self, bot: Asahi):
        self.bot = bot

    async def set_mute_role(self, guild: int, role_id: int):
        await self.bot.db.execute(
            "INSERT INTO Mute_Settings (guild_id, mute_role) VALUES(:guild, :mute_role) ON CONFLICT(guild_id) DO UPDATE SET mute_role = :u_mute_role",
            values={"guild": guild, "mute_role": role_id, "u_mute_role": role_id},
        )
        LOGGER.info(f"Added mute role for guild {guild}")

    async def fetch_mute_role(self, guild: int):
        """Fetch a guilds mute role"""
        return await self.bot.db.fetch_one(
            "SELECT mute_role FROM Mute_Settings WHERE guild_id = :guild", values={"guild": guild}
        )
