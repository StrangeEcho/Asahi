from discord.ext.commands import BadArgument


class UserNotFound(BaseException):
    """Thrown if a user passed is not in database"""

    pass


class UrbanDictionaryError(BadArgument):
    """UD related error"""

    pass
