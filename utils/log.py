from datetime import datetime
from types import TracebackType
from typing import Tuple
import logging
import threading
import traceback

from colorama import Fore, init, Style

init()

colors = {
    "DEBUG": f"{Style.DIM}{Fore.LIGHTWHITE_EX}",
    "INFO": "",
    "WARNING": f"{Fore.YELLOW}{Style.BRIGHT}",
    "ERROR": f"{Fore.LIGHTRED_EX}{Style.BRIGHT}",
    "CRITICAL": f"{Fore.RED}{Style.BRIGHT}",
}
colors2 = {
    "DEBUG": f"{Style.DIM}{Fore.LIGHTWHITE_EX}",
    "INFO": Fore.BLUE,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.LIGHTRED_EX,
    "CRITICAL": Fore.RED,
}
styles = {
    "DEBUG": f"{Style.DIM}{Fore.LIGHTWHITE_EX}",
    "INFO": "",
    "WARNING": "",
    "ERROR": "",
    "CRITICAL": Style.BRIGHT,
}
names = {
    "kurisu": Fore.BLUE,
    "discord.client": Fore.GREEN,
    "discord.gateway": Fore.MAGENTA,
    "discord.ext.commands.core": Fore.YELLOW,
    "discord.http": Fore.RED,
}

lock = threading.Lock()


class LoggingHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord) -> None:
        name = record.name
        # noinspection PyStatementEffect
        level = record.levelno  # noqa F841
        level_name = record.levelname
        if name == "kurisu":
            split = record.msg.split(";")
            if len(split) == 1:
                sub = None
                message = split[0]
            else:
                sub = split[0]
                message = ";".join(split[1:])
        else:
            message = record.msg
            sub = None

        message %= record.args
        with lock:
            first = True
            for line in message.splitlines():
                print(
                    f"{datetime.now().strftime('%x %X') if first else '                 '}"
                    f" "
                    f"{colors2[level_name]}{styles[level_name]}[{level_name[:3]}]{Style.RESET_ALL}"
                    f" "
                    f"{Style.BRIGHT}{names[name]}{name}{Style.RESET_ALL} "
                    + (
                        f"» {Style.BRIGHT}{Fore.LIGHTBLUE_EX}{sub}{Style.RESET_ALL} "
                        if sub
                        else ""
                    )
                    + f"» "
                    f"{colors[level_name]}{line}{Style.RESET_ALL}"
                )
                first = False

            if record.exc_info:
                exception: Tuple[type, BaseException, TracebackType] = record.exc_info
                lines = traceback.format_exception(*exception)
                for line in lines:
                    for msg in line.splitlines():
                        print(
                            f"                 "
                            f" "
                            f"{colors2[level_name]}{styles[level_name]}[{level_name[:3]}]{Style.RESET_ALL}"
                            f" "
                            f"{Style.BRIGHT}{names[name]}{name}{Style.RESET_ALL} "
                            + (
                                f"» {Style.BRIGHT}{Fore.LIGHTBLUE_EX}{sub}{Style.RESET_ALL} "
                                if sub
                                else ""
                            )
                            + f"» "
                            f"{colors[level_name]}{msg}{Style.RESET_ALL}"
                        )
