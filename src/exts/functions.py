from __future__ import annotations

import subprocess
from datetime import timedelta
from typing import TYPE_CHECKING, Generator

import aiohttp
from humanize import naturaldelta, precisedelta


def color_convert(color: str) -> int:
    """Convert colors from config file"""

    if color.startswith("0x"):
        return color
    else:
        return int(color.replace("#", "0x"), 16)


def chunk_list(_list: list, size: int) -> Generator:
    """Divide a list into even chunks"""
    for i in range(0, len(_list), size):
        yield _list[i : i + size]


def humanize_timedelta(_delta: timedelta, *, precise: bool = False) -> str:
    """Humanize a datetime.timedelta"""
    if precise:
        return precisedelta(_delta)
    else:
        return naturaldelta(_delta)


def get_version_hash() -> str:
    return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("ascii").strip()
