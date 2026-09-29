import re
import shutil
from typing import NamedTuple, Optional, Tuple


class Size(NamedTuple):
    width: int
    height: int


class Point(NamedTuple):
    x: int
    y: int


class Segment(NamedTuple):
    text: str
    style: Optional[str] = None


class VisualMeter:
    """
    Utility class that uses regex to strip ANSI codes and measure visible terminal character length.
    """
    # Regex to match ANSI SGR escape sequences (e.g., \033[31m, \033[1;31m, \033[m)
    _ANSI_RE = re.compile(r'\033\[[0-9;]*[mK]')

    @classmethod
    def strip_ansi(cls, text: str) -> str:
        """Removes all ANSI escape sequences from a string."""
        return cls._ANSI_RE.sub('', text)

    @classmethod
    def measure(cls, text: str) -> int:
        """Returns the visual length of a string, ignoring ANSI escape sequences."""
        return len(cls.strip_ansi(text))


class TerminalMetrics:
    """Helper to query current viewport size using shutil.get_terminal_size()."""

    @staticmethod
    def get_size(fallback: Tuple[int, int] = (80, 24)) -> Size:
        """
        Returns the current terminal size.
        If the size cannot be determined, falls back to the provided dimensions.
        """
        size = shutil.get_terminal_size(fallback=fallback)
        return Size(width=size.columns, height=size.lines)
