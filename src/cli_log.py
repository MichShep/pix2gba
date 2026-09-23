import os
import sys
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

# When False only warnings, errors, and summaries are printed.
_verbose = False

# Hidden INFO lines by indent level, printed as context above a later warning/error
_breadcrumbs: dict[int, str] = {}

_use_color = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

RED = "\033[31m" if _use_color else ""
GREEN = "\033[32m" if _use_color else ""
RESET = "\033[0m" if _use_color else ""


def set_verbose(enabled: bool) -> None:
    global _verbose
    _verbose = enabled


def is_verbose() -> bool:
    return _verbose


def indent() -> None:
    global _indent_level
    _indent_level += 1


def dedent() -> None:
    global _indent_level
    if _indent_level > 0:
        _indent_level -= 1


def _format(level: LogType, message: str, subject: Optional[str], indent_level: int) -> str:
    indent_str = " " * (indent_level * _indent_spaces)
    level_str = level.value.ljust(LEVEL_WIDTH)

    if subject:
        return f"{indent_str}{level_str} {subject}: {message}"
    return f"{indent_str}{level_str} {message}"


def _log(level: LogType, message: str, subject: Optional[str] = None, color: str = "", verbose_only: bool = False) -> None:
    line = _format(level, message, subject, _indent_level)

    if verbose_only and not _verbose:
        # Remember nested INFO lines so a later warning/error can show what it belongs to
        if level == LogType.INFO and _indent_level > 0:
            for lvl in [l for l in _breadcrumbs if l >= _indent_level]:
                del _breadcrumbs[lvl]
            _breadcrumbs[_indent_level] = line
        return

    if not _verbose:
        for lvl in sorted(l for l in _breadcrumbs if l < _indent_level):
            print(_breadcrumbs.pop(lvl))

    print(f"{color}{line}{RESET}" if color else line)


def blank() -> None:
    if _verbose:
        print()


def info(msg: str, subject: Optional[str] = None) -> None:
    _log(LogType.INFO, msg, subject, verbose_only=True)


def ok(msg: str, subject: Optional[str] = None) -> None:
    _log(LogType.OK, msg, subject, verbose_only=True)


def cache(msg: str, subject: Optional[str] = None) -> None:
    _log(LogType.CACHE, msg, subject, GREEN, verbose_only=True)


def skip(msg: str, subject: Optional[str] = None) -> None:
    _log(LogType.SKIP, msg, subject)


def warn(msg: str, subject: Optional[str] = None) -> None:
    _log(LogType.WARN, msg, subject)


def error(msg: str, subject: Optional[str] = None) -> None:
    _log(LogType.ERROR, msg, subject, RED)


def abort(msg: str = "build aborted") -> None:
    _log(LogType.ABORT, msg, color=RED)


def summary(msg: str) -> None:
    _breadcrumbs.clear()
    _log(LogType.SUMMARY, msg)
