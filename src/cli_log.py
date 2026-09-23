from enum import Enum
from typing import Optional

class LogType(Enum):
    INFO = "INFO"
    OK = "OK"
    SKIP = "SKIP"
    WARN = "WARN"
    ERROR = "ERROR"
    ABORT = "ABORT"
    SUMMARY = "SUMMARY"
    CACHE = "CACHE"


LEVEL_WIDTH = 7
_indent_level = 0
_indent_spaces = 4

RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RESET = "\033[0m"


def indent() -> None:
    global _indent_level
    _indent_level += 1


def dedent() -> None:
    global _indent_level
    if _indent_level > 0:
        _indent_level -= 1


def _log(level: LogType, message: str, subject: Optional[str] = None) -> None:
    indent_str = " " * (_indent_level * _indent_spaces)
    level_str = level.value.ljust(LEVEL_WIDTH)

    if subject:
        line = f"{indent_str}{level_str} {subject}: {message}"
    else:
        line = f"{indent_str}{level_str} {message}"

    print(line)


def info(msg: str, subject: Optional[str] = None) -> None:
    _log(LogType.INFO, msg, subject)


def ok(msg: str, subject: Optional[str] = None) -> None:
    _log(LogType.OK, msg, subject)


def skip(msg: str, subject: Optional[str] = None) -> None:
    print(YELLOW, end="")
    _log(LogType.SKIP, msg, subject)
    print(RESET, end="")

def cache(msg: str, subject: Optional[str] = None) -> None:
    print(GREEN, end="")
    _log(LogType.CACHE, msg, subject)
    print(RESET, end="")


def warn(msg: str, subject: Optional[str] = None) -> None:
    _log(LogType.WARN, msg, subject)


def error(msg: str, subject: Optional[str] = None) -> None:
    print(RED, end="")
    _log(LogType.ERROR, msg, subject)
    print(RESET, end="")


def abort(msg: str = "build aborted") -> None:
    print(RED, end="")
    _log(LogType.ABORT, msg)
    print(RESET, end="")


def summary(msg: str) -> None:
    _log(LogType.SUMMARY, msg)