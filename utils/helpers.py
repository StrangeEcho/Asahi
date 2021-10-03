from discord.ext import menus


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
