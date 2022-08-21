from datetime import timedelta
from typing import Any, Generator

from humanize import naturaldelta, precisedelta
import toml


class ConfigKeyNotFound(KeyError):
    pass


class Config:
    master: dict = toml.load("./src/core/data/config.toml")

    def get(self, key: str) -> Any:
        try:
            return self.master[key]
        except KeyError:
            raise ConfigKeyNotFound(f"No config with key: '{key}' was found.")


def color_resolver(color: str) -> int:
    """Lazy color resolver"""
    try:
        if color.startswith("#"):
            return int(color.replace("#", "0x"), 16)
        if color.startswith("0x"):
            return int(color, 16)
    except ValueError:
        print(f"There was a problem with resolving the following color: '{color}' ")


def humanize_timedelta(_delta: timedelta, *, precise: bool = False) -> str:
    """Humanize a datetime.timedelta"""
    if precise:
        return precisedelta(_delta)
    else:
        return naturaldelta(_delta)


def chunk_list(_list: list, size: int) -> Generator:
    """Divide a list into even chunks"""
    for i in range(0, len(_list), size):
        yield _list[i : i + size]
