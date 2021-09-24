from discord.ext import commands, menus

from .kurisu import KurisuBot


class EmbedListMenu(menus.ListPageSource):
    """
    Paginated embed menu.
    """

    def __init__(self, data):
        """
        Initializes the EmbedListMenu.
        """
        super().__init__(data, per_page=1)

    async def format_page(self, menu, embeds):
        """
        Formats the page.
        """
        return embeds


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
