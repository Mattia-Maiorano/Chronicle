"""
Logger module for structured, colorized, and colorless console output.
Provides a flexible logging function with indentation, spacing, color, and tree structure support.
"""

from typing import Any, Optional, List

_COLOR_MODE: bool = True


def set_color_mode(enabled: bool = True) -> None:
    """
    Enable or disable global color mode for logging.
    When set to False (colorless mode), color codes and non-ASCII decorative borders are omitted.
    """
    global _COLOR_MODE
    _COLOR_MODE = enabled


def get_color_mode() -> bool:
    """
    Get the current global color mode state.
    """
    return _COLOR_MODE


def set_colorless_mode(enabled: bool = True) -> None:
    """
    Enable or disable colorless mode.
    """
    global _COLOR_MODE
    _COLOR_MODE = not enabled


def set_ascii_mode(enabled: bool = True) -> None:
    """
    Backward-compatible alias for set_colorless_mode.
    """
    set_colorless_mode(enabled)


def get_ascii_mode() -> bool:
    """
    Backward-compatible alias for checking if colorless mode is active.
    """
    return not _COLOR_MODE


class Colors:
    """ANSI color codes for terminal output."""
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright text colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Reset
    RESET = '\033[0m'
    
    # Semantic colors for common use cases
    ERROR = RED
    WARNING = YELLOW
    SUCCESS = GREEN
    INFO = CYAN
    DEBUG = BRIGHT_MAGENTA
    HEADER = BRIGHT_CYAN
    EMPHASIS = BRIGHT_YELLOW


def log(indentation_tabs=0, newline_before=0, newline_after=0, color=None, content="", color_mode=None):
    """
    Log a message with structured formatting, indentation, spacing, and color.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode

    # Print newlines before content
    if newline_before > 0:
        print('\n' * (newline_before - 1), end='')
    
    # Build indentation
    indentation = '\t' * indentation_tabs
    
    # Build the message with color if specified and in color mode
    if color and use_color:
        message = f"{indentation}{color}{content}{Colors.RESET}"
    else:
        message = f"{indentation}{content}"
    
    # Print the message
    print(message, end='')
    
    # Print newlines after content
    if newline_after > 0:
        print('\n' * newline_after, end='')
    else:
        print()  # Default newline


def log_newline(count=1):
    """
    Log specified number of newlines.
    """
    print('\n' * (count - 1), end='')
    print()  # Ensure at least one newline


def log_application_title(title, width=60, color_mode=None):
    """
    Log a stylized application title with decorative borders.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode

    title_length = len(title)
    if title_length + 2 > width - 2:
        width = title_length + 4
    
    padding = (width - 2 - title_length) // 2
    padded_title = " " * padding + title + " " * (width - 2 - title_length - padding)
    
    if use_color:
        top_border = "╔" + "═" * (width - 2) + "╗"
        middle_line = "║" + padded_title + "║"
        bottom_border = "╚" + "═" * (width - 2) + "╝"
        color = Colors.BRIGHT_MAGENTA + Colors.BOLD
    else:
        top_border = "+" + "-" * (width - 2) + "+"
        middle_line = "|" + padded_title + "|"
        bottom_border = "+" + "-" * (width - 2) + "+"
        color = None
    
    log_newline(2)
    log(0, 1, 0, color, top_border, color_mode=use_color)
    log(0, 0, 0, color, middle_line, color_mode=use_color)
    log(0, 0, 1, color, bottom_border, color_mode=use_color)
    log_newline(2)


def log_section_header(title, indentation_tabs=0, color_mode=None):
    """
    Log a section header with consistent formatting.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    color = Colors.HEADER + Colors.BOLD if use_color else None
    separator = "=" * 60

    log(indentation_tabs, 1, 0, color, separator, color_mode=use_color)
    log(indentation_tabs, 0, 0, color, title, color_mode=use_color)
    log(indentation_tabs, 0, 1, color, separator, color_mode=use_color)
    log_newline()


def log_subsection(title, indentation_tabs=0, color_mode=None):
    """
    Log a subsection header with consistent formatting.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    color = Colors.BRIGHT_CYAN if use_color else None
    separator = "-" * 40

    log(indentation_tabs, 1, 0, color, separator, color_mode=use_color)
    log(indentation_tabs, 0, 0, color, title, color_mode=use_color)
    log(indentation_tabs, 0, 0, color, separator, color_mode=use_color)
    log_newline()


def log_error(message, indentation_tabs=0, newline_before=0, newline_after=0, color_mode=None):
    """
    Log an error message with consistent formatting.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    prefix = "ERROR:" if use_color else "[ERROR]"
    color = Colors.ERROR + Colors.BOLD if use_color else None
    log(indentation_tabs, newline_before, newline_after, 
        color, f"{prefix} {message}", color_mode=use_color)


def log_warning(message, indentation_tabs=0, newline_before=0, newline_after=0, color_mode=None):
    """
    Log a warning message with consistent formatting.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    prefix = "WARNING:" if use_color else "[WARNING]"
    color = Colors.WARNING + Colors.BOLD if use_color else None
    log(indentation_tabs, newline_before, newline_after, 
        color, f"{prefix} {message}", color_mode=use_color)


def log_success(message, indentation_tabs=0, newline_before=0, newline_after=0, color_mode=None):
    """
    Log a success message with consistent formatting.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    prefix = "SUCCESS:" if use_color else "[OK]"
    color = Colors.SUCCESS + Colors.BOLD if use_color else None
    log(indentation_tabs, newline_before, newline_after, 
        color, f"{prefix} {message}", color_mode=use_color)


def log_info(message, indentation_tabs=0, newline_before=0, newline_after=0, color_mode=None):
    """
    Log an info message with consistent formatting.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    prefix = "INFO:" if use_color else "[INFO]"
    color = Colors.INFO if use_color else None
    log(indentation_tabs, newline_before, newline_after, 
        color, f"{prefix} {message}", color_mode=use_color)


def log_debug(message, indentation_tabs=2, newline_before=0, newline_after=0, color_mode=None):
    """
    Log a debug message with consistent formatting. Default indentation is 2 tabs.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    prefix = "DEBUG:" if use_color else "[DEBUG]"
    color = Colors.DEBUG + Colors.BOLD if use_color else None
    log(indentation_tabs, newline_before, newline_after, 
        color, f"{prefix} {message}", color_mode=use_color)


def log_step(step_number, total_steps, description, indentation_tabs=0, color_mode=None):
    """
    Log a step in a process with consistent formatting.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    color = Colors.BRIGHT_BLUE + Colors.BOLD if use_color else None
    log_newline()
    log(indentation_tabs, 1, 0, color, 
        f"[Step {step_number}/{total_steps}] {description}", color_mode=use_color)
    log_newline()


def log_file_saved(filepath, indentation_tabs=1, color_mode=None):
    """
    Log a file save operation with consistent formatting.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    prefix = "Saved:"
    color = Colors.SUCCESS if use_color else None
    log(indentation_tabs, 0, 0, color, 
        f"{prefix} {filepath}", color_mode=use_color)


def log_final_result(success, message, width=60, color_mode=None):
    """
    Log a final result with decorative formatting.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    color = (Colors.SUCCESS + Colors.BOLD if success else Colors.ERROR + Colors.BOLD) if use_color else None
    separator = "=" * width
    
    log_newline(2)
    log(0, 1, 0, color, separator, color_mode=use_color)
    if success:
        log_success(message, newline_after=1, color_mode=use_color)
    else:
        log_error(message, newline_after=1, color_mode=use_color)
    log(0, 0, 1, color, separator, color_mode=use_color)
    log_newline(2)


# --- Tree Structured Logger ---

def log_banner(title: str, width: int = 54, color_mode: Optional[bool] = None) -> None:
    """
    Log a top-level section header wrapped in ASCII border box.
    Vibrant colors in Color Mode; plain text in Colorless Mode.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    min_width = len(title) + 6
    if width < min_width:
        width = min_width

    line_dashes = '-' * (width - 2)
    padded = f"| [{title.upper()}]".ljust(width - 1)

    if use_color:
        c = Colors.HEADER + Colors.BOLD
        r = Colors.RESET
        top = f"{c}+{line_dashes}+{r}"
        mid = f"{c}{padded}|{r}"
        bot = f"{c}+{line_dashes}+{r}"
        print(f"\n{top}\n{mid}\n{bot}\n")
    else:
        top = f"+{line_dashes}+"
        mid = f"{padded}|"
        bot = f"+{line_dashes}+"
        print(f"\n{top}\n{mid}\n{bot}\n")


def log_section(category: str, indent_level: int = 0, color_mode: Optional[bool] = None) -> None:
    """
    Log an indented sub-section or category header.
    Vibrant colors in Color Mode; plain text in Colorless Mode.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    indent = '  ' * indent_level
    cat_str = category if category.endswith(':') else f"{category}:"

    if use_color:
        c_tree = Colors.BRIGHT_CYAN
        c_cat = Colors.BRIGHT_CYAN + Colors.BOLD
        r = Colors.RESET
        print(f"\n{indent}  {c_tree}|--{r} {c_cat}{cat_str}{r}")
    else:
        print(f"\n{indent}  |-- {cat_str}")


def log_detail(label: str, value: Any, indent_level: int = 0, color_mode: Optional[bool] = None) -> None:
    """
    Log a key-value metric item in the tree.
    Vibrant colors in Color Mode; plain text in Colorless Mode.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    indent = '  ' * (indent_level + 1)
    formatted_label = str(label).ljust(22)

    if use_color:
        c_tree = Colors.BRIGHT_CYAN
        c_label = Colors.CYAN + Colors.BOLD
        c_val = Colors.BRIGHT_WHITE + Colors.BOLD
        r = Colors.RESET
        print(f"{indent}{c_tree}+--{r} {c_label}{formatted_label}{r} : {c_val}{value}{r}")
    else:
        print(f"{indent}+-- {formatted_label} : {value}")


def log_decision(action: str, detail: Optional[str] = None, indent_level: int = 0, color_mode: Optional[bool] = None) -> None:
    """
    Log a decision or state transition arrow.
    Vibrant colors in Color Mode; plain text in Colorless Mode.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    indent = '  ' * indent_level

    if use_color:
        c_arrow = Colors.BRIGHT_YELLOW + Colors.BOLD
        c_action = Colors.BRIGHT_GREEN + Colors.BOLD
        c_detail = Colors.BRIGHT_WHITE
        r = Colors.RESET

        if detail is not None and str(detail).strip() != "":
            print(f"\n{indent}  {c_arrow}+--> DECISION:{r} {c_action}{action}{r} -> {c_detail}{detail}{r}\n")
        else:
            print(f"\n{indent}  {c_arrow}+--> DECISION:{r} {c_action}{action}{r}\n")
    else:
        if detail is not None and str(detail).strip() != "":
            print(f"\n{indent}  +--> DECISION: {action} -> {detail}\n")
        else:
            print(f"\n{indent}  +--> DECISION: {action}\n")


def log_message(message: str, indent_level: int = 0, color_mode: Optional[bool] = None) -> None:
    """
    Log a raw message with optional tree indent prefix.
    Vibrant colors in Color Mode; plain text in Colorless Mode.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode
    indent = '  ' * indent_level

    if use_color:
        c_tree = Colors.BRIGHT_CYAN
        c_msg = Colors.BRIGHT_WHITE
        r = Colors.RESET
        print(f"{indent}{c_tree}|--{r} {c_msg}{message}{r}")
    else:
        print(f"{indent}|-- {message}")

def log_table(rows: List[List[str]], headers: Optional[List[str]] = None, alignments: Optional[List[str]] = None, color_mode: Optional[bool] = None) -> None:
    """Render a table of rows with optional headers and alignments.

    Args:
        rows: List of rows, each a list of cell strings.
        headers: Optional list of column headers.
        alignments: Optional list of alignment specifiers per column ('<', '^', '>').
        color_mode: Override global color mode.
    """
    use_color = _COLOR_MODE if color_mode is None else color_mode

    # Determine column count
    col_count = max(
        len(headers) if headers else 0,
        max((len(r) for r in rows), default=0)
    )
    if col_count == 0:
        return

    # Compute column widths
    col_widths = [0] * col_count
    for r in rows:
        for i, cell in enumerate(r):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    if headers:
        for i, h in enumerate(headers):
            col_widths[i] = max(col_widths[i], len(str(h)))

    # Prepare alignments (default left)
    if not alignments:
        alignments = ['<'] * col_count
    else:
        alignments = (list(alignments) + ['<'] * col_count)[:col_count]

    # Border characters based on mode
    if use_color:
        tl, tm, tr = '┌', '┬', '┐'
        ml, mm, mr = '├', '┼', '┤'
        bl, bm, br = '└', '┴', '┘'
        h, v = '─', '│'
        border_color = Colors.BRIGHT_CYAN
    else:
        tl = tm = tr = ml = mm = mr = bl = bm = br = '+'
        h = '-'
        v = '|'
        border_color = None

    def make_line(left, sep, right):
        line = left
        for i, w in enumerate(col_widths):
            line += h * (w + 2)
            line += sep if i < len(col_widths) - 1 else right
        return line

    top_line = make_line(tl, tm, tr)
    sep_line = make_line(ml, mm, mr)
    bottom_line = make_line(bl, bm, br)

    def format_row(cells):
        parts = []
        for i, cell in enumerate(cells):
            txt = str(cell)
            align = alignments[i]
            parts.append(f' {txt:{align}{col_widths[i]}} ')
        return v + v.join(parts) + v

    lines = [top_line]
    if headers:
        lines.append(format_row(headers))
        lines.append(sep_line)
    for r in rows:
        padded = r + [''] * (col_count - len(r))
        lines.append(format_row(padded))
    lines.append(bottom_line)

    for line in lines:
        if border_color and use_color:
            print(f"{border_color}{line}{Colors.RESET}")
        else:
            print(line)



class StructuredLogger:
    """
    Structured tree logger for Python applications.
    Strictly uses framing, tree indentation, and decision arrows.
    Fully colorized in Color Mode; plain text in Colorless Mode.
    """

    @staticmethod
    def log_banner(title: str, width: int = 54, color_mode: Optional[bool] = None) -> None:
        log_banner(title, width=width, color_mode=color_mode)

    @staticmethod
    def log_section(category: str, indent_level: int = 0, color_mode: Optional[bool] = None) -> None:
        log_section(category, indent_level=indent_level, color_mode=color_mode)

    @staticmethod
    def log_detail(label: str, value: Any, indent_level: int = 0, color_mode: Optional[bool] = None) -> None:
        log_detail(label, value, indent_level=indent_level, color_mode=color_mode)

    @staticmethod
    def log_decision(action: str, detail: Optional[str] = None, indent_level: int = 0, color_mode: Optional[bool] = None) -> None:
        log_decision(action, detail=detail, indent_level=indent_level, color_mode=color_mode)

    @staticmethod
    def log_message(message: str, indent_level: int = 0, color_mode: Optional[bool] = None) -> None:
        log_message(message, indent_level=indent_level, color_mode=color_mode)

    # CamelCase aliases
    logBanner = log_banner
    logSection = log_section
    logDetail = log_detail
    logDecision = log_decision
    logMessage = log_message


# Backward compatibility aliases
AsciiLogger = StructuredLogger
KeeperLogger = StructuredLogger
