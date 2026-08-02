# Chronicle

A flexible and colorized logging system for Python applications.

## Overview
Chronicle provides structured logging with support for indentation, spacing, colors, semantic message types, and a Colorless Mode for plain-text environments where terminal colors are unsupported.

## Installation

### From GitHub
```bash
pip install git+https://github.com/theUzumaki/Chronicle.git
```

### In requirements.txt
```
git+https://github.com/theUzumaki/Chronicle.git
```

## Features
- **Flexible formatting**: Control indentation, newlines before/after, and colors
- **Semantic functions**: Pre-configured functions for errors, warnings, success, info, and debug messages
- **Color support**: Full ANSI color support including bright text colors, background colors, and bold styles
- **Structured Tree Logging**: Clean framing and tree logging (`StructuredLogger` / `log_banner`, `log_section`, `log_detail`, `log_decision`, `log_message`)
- **Color Mode & Colorless Mode**: Global `set_color_mode(False)` toggle for plain-text environments without ANSI escape sequences
- **Pipeline logging**: Special functions for structured logging in multi-step processes
- **File operation logging**: Dedicated functions for logging file saves

## Basic Usage

### Simple Logging
```python
from chronicle import log, Colors

# Plain message
log(0, 0, 0, None, "Hello, World!")

# Colored message
log(0, 0, 0, Colors.GREEN, "Success message in green")

# Indented message
log(1, 0, 0, Colors.CYAN, "This is indented 1 tab")
log(2, 0, 0, Colors.YELLOW, "This is indented 2 tabs")

# Message with spacing
log(0, 2, 1, Colors.RED, "2 newlines before, 1 after")

# Combined styles
log(0, 0, 0, Colors.BOLD + Colors.BLUE, "Bold blue text")
```

## Semantic Logging Functions

### Error Messages
```python
from chronicle import log_error

log_error("File not found")
log_error("Connection timeout", indentation_tabs=1)
log_error("Critical failure", newline_before=1, newline_after=1)
```

### Warning Messages
```python
from chronicle import log_warning

log_warning("Deprecated function used")
log_warning("Low memory available", indentation_tabs=1)
```

### Success Messages
```python
from chronicle import log_success

log_success("Operation completed successfully")
log_success("Data processed", indentation_tabs=1)
```

### Info Messages
```python
from chronicle import log_info

log_info("Starting process...")
log_info("Loading configuration", indentation_tabs=1)
```

### Debug Messages
```python
from chronicle import log_debug

log_debug("Variable x = 42")
log_debug("Function called with args: foo, bar", indentation_tabs=1)
```

## Color Mode vs. Colorless Mode

Chronicle allows toggling color mode globally. When Color Mode is disabled (`set_color_mode(False)`), ANSI escape codes are omitted for plain-text logging.

```python
from chronicle import set_color_mode, log_info, log_error, log_success

# Disable colors for plain-text logging
set_color_mode(False)

log_info("Running in plain text environment")  # Outputs: [INFO] Running in plain text environment
log_error("Failed to connect")                  # Outputs: [ERROR] Failed to connect
log_success("Process finished")                 # Outputs: [OK] Process finished
```

### Structured Tree Logger (`StructuredLogger`)
Chronicle provides a structured debug logger using framing, tree indentation, and decision arrows. In Color Mode, tree lines and banners are syntax-highlighted; in Colorless Mode, plain text is produced:

```python
from chronicle import StructuredLogger

# Log a top-level section header wrapped in a border box
StructuredLogger.log_banner("DATA PROCESSING ENGINE")

# Log an indented sub-section or category header
StructuredLogger.log_section("Execution Phase")

# Log key-value metric items in the tree
StructuredLogger.log_detail("Batch size", "64")
StructuredLogger.log_detail("Latency", "14.2ms")

# Log a decision or state transition arrow
StructuredLogger.log_decision("PASS", "Quality score 0.96 >= 0.85 threshold")

# Log a raw message with optional tree indent
StructuredLogger.log_message("Pipeline ready for next batch", indent_level=1)
```

**Output:**
```
+----------------------------------------------------+
| [DATA PROCESSING ENGINE]                           |
+----------------------------------------------------+
  |-- Execution Phase:
  +-- Batch size             : 64
  +-- Latency                : 14.2ms
  +--> DECISION: PASS -> Quality score 0.96 >= 0.85 threshold
  |-- Pipeline ready for next batch
```

You can also use standalone top-level functions (`log_banner`, `log_section`, `log_detail`, `log_decision`, `log_message`) or camelCase aliases (`logBanner`, `logSection`, `logDetail`, `logDecision`, `logMessage`).

## Structured Logging

### Section Headers
```python
from chronicle import log_section_header, log_subsection

log_section_header("MAIN PROCESSING PIPELINE")
log_subsection("Data Loading Phase")
```

### Step-by-step Logging
```python
from chronicle import log_step

log_step(1, 5, "Preprocessing data")
log_step(2, 5, "Feature extraction")
log_step(3, 5, "Model training")
```

### File Operations
```python
from chronicle import log_file_saved

log_file_saved("output/results.png")
log_file_saved("models/trained_model.bin", indentation_tabs=1)
```

## Color Reference

### Text Colors
- `Colors.BLACK`, `Colors.RED`, `Colors.GREEN`, `Colors.YELLOW`
- `Colors.BLUE`, `Colors.MAGENTA`, `Colors.CYAN`, `Colors.WHITE`

### Bright Text Colors
- `Colors.BRIGHT_RED`, `Colors.BRIGHT_GREEN`, `Colors.BRIGHT_YELLOW`
- `Colors.BRIGHT_BLUE`, `Colors.BRIGHT_MAGENTA`, `Colors.BRIGHT_CYAN`

### Background Colors
- `Colors.BG_BLACK`, `Colors.BG_RED`, `Colors.BG_GREEN`, `Colors.BG_YELLOW`
- `Colors.BG_BLUE`, `Colors.BG_MAGENTA`, `Colors.BG_CYAN`, `Colors.BG_WHITE`

### Text Styles
- `Colors.BOLD` - Bold text
- `Colors.DIM` - Dimmed text
- `Colors.ITALIC` - Italic text
- `Colors.UNDERLINE` - Underlined text
- `Colors.REVERSE` - Inverted colors

### Semantic Colors
- `Colors.ERROR` - Red (for errors)
- `Colors.WARNING` - Yellow (for warnings)
- `Colors.SUCCESS` - Green (for success)
- `Colors.INFO` - Cyan (for information)
- `Colors.DEBUG` - Bright Magenta (for debug)
- `Colors.HEADER` - Bright cyan (for headers)

## Function Reference

### `log(indentation_tabs, newline_before, newline_after, color, content)`
The core logging function.

### Color Mode Control & Tree Logger
- `set_color_mode(enabled: bool = True)` - Enable or disable global Color Mode
- `get_color_mode() -> bool` - Return current Color Mode state
- `log_banner(title: str, width: int = 54)` / `StructuredLogger.log_banner` - Log border box banner
- `log_section(category: str, indent_level: int = 0)` / `StructuredLogger.log_section` - Log indented category header
- `log_detail(label: str, value: Any, indent_level: int = 0)` / `StructuredLogger.log_detail` - Log key-value metric item
- `log_decision(action: str, detail: Optional[str] = None, indent_level: int = 0)` / `StructuredLogger.log_decision` - Log decision arrow
- `log_message(message: str, indent_level: int = 0)` / `StructuredLogger.log_message` - Log raw tree message

### Semantic Functions
All semantic functions accept:
- `message` (str): The message to log
- `indentation_tabs` (int): Indentation level (default: 0)
- `newline_before` (int): Newlines before (default: 0)
- `newline_after` (int): Newlines after (default: 0)

Functions:
- `log_error(message, ...)` - Log error
- `log_warning(message, ...)` - Log warning
- `log_success(message, ...)` - Log success
- `log_info(message, ...)` - Log info
- `log_debug(message, ...)` - Log debug

### Structural Functions
- `log_section_header(title, indentation_tabs=0)` - Log major section header
- `log_subsection(title, indentation_tabs=0)` - Log subsection header
- `log_step(step_number, total_steps, description, indentation_tabs=0)` - Log processing step
- `log_file_saved(filepath, indentation_tabs=1)` - Log file save operation

## Demo
Run the demo script to see a concise example of both Color Mode and Colorless Mode in action:
```bash
python example.py
```
