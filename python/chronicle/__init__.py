"""
Chronicle - A flexible and colorized logging system for Python applications.
"""

from .logger import (
    Colors,
    log,
    log_newline,
    log_application_title,
    log_section_header,
    log_subsection,
    log_error,
    log_warning,
    log_success,
    log_info,
    log_debug,
    log_step,
    log_file_saved,
    log_final_result,
    set_color_mode,
    get_color_mode,
    set_colorless_mode,
    set_ascii_mode,
    get_ascii_mode,
    StructuredLogger,
    AsciiLogger,
    KeeperLogger,
    log_banner,
    log_section,
    log_detail,
    log_decision,
    log_message,
)

from .core.geometry import Size, Point, Segment, VisualMeter, TerminalMetrics
from .layout import RenderContext, Renderable, Text, Rule, Panel, Layout, FlexSplitter, Fixed, Flex, Ratio
from .components import LiveTable, Column, RollingLogStream, Badge, ProgressBar
from .engine import Canvas, LiveEngine

__version__ = "1.0.4"

__all__ = [
    "Colors",
    "log",
    "log_newline",
    "log_application_title",
    "log_section_header",
    "log_subsection",
    "log_error",
    "log_warning",
    "log_success",
    "log_info",
    "log_debug",
    "log_step",
    "log_file_saved",
    "log_final_result",
    "set_color_mode",
    "get_color_mode",
    "set_colorless_mode",
    "set_ascii_mode",
    "get_ascii_mode",
    "StructuredLogger",
    "AsciiLogger",
    "KeeperLogger",
    "log_banner",
    "log_section",
    "log_detail",
    "log_decision",
    "log_message",
    "Size", "Point", "Segment", "VisualMeter", "TerminalMetrics",
    "RenderContext", "Renderable", "Text", "Rule", "Panel", "Layout", "FlexSplitter", "Fixed", "Flex", "Ratio",
    "LiveTable", "Column", "RollingLogStream", "Badge", "ProgressBar",
    "Canvas", "LiveEngine"
]
