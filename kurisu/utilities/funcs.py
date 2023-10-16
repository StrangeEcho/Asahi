import datetime
from humanize import naturaldelta, precisedelta


def humanize_timedelta(delta: datetime.timedelta, *, precise: bool = False) -> str:
    """"Humanize" a datetime.timedelta object to be human readable"""
    if precise:
        return precisedelta(delta)
    return naturaldelta(delta)


def box(text: str, lang: str = "") -> str:
    return f"```{lang}\n{text}\n```"
     
