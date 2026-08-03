# Chronicle Specification (SPEC.md)

**Version**: 1.0.4  
**Specification**: Universal Formatting & API Specification for Chronicle Logging Engine

---

## 1. Overview

Chronicle is a lightweight, zero-dependency structured logging system designed for terminal visualization across server-side, web, mobile, and system programming environments.

Chronicle operates in two global visual modalities:
1. **Color Mode** (Default): Uses ANSI SGR escape sequences for text styling, bright colors, bold text, and UTF-8 box-drawing characters.
2. **Colorless Mode**: Omits ANSI escape sequences and UTF-8 decorative borders for plain-text logging environments (e.g. CI logs, legacy terminals, file redirects).

---

## 2. Color Palette & ANSI Escape Sequences

Chronicle uses standard 3-bit / 4-bit SGR (Select Graphic Rendition) ANSI escape codes.

### Base Colors (SGR 30–37)
| Color Name | SGR Code | Hex / Render Approximation | Semantic Usage |
| :--- | :--- | :--- | :--- |
| `BLACK` | `\033[30m` | `#000000` | Dark text |
| `RED` | `\033[31m` | `#CD3131` | `ERROR` |
| `GREEN` | `\033[32m` | `#0DBC79` | `SUCCESS` |
| `YELLOW` | `\033[33m` | `#E5E510` | `WARNING` |
| `BLUE` | `\033[34m` | `#2472C8` | Standard info |
| `MAGENTA` | `\033[35m` | `#BC3FBC` | Secondary accents |
| `CYAN` | `\033[36m` | `#11A8CD` | `INFO`, Tree labels |
| `WHITE` | `\033[37m` | `#E5E5E5` | Standard text |

### Bright Text Colors (SGR 90–97)
| Color Name | SGR Code | Hex / Render Approximation | Semantic Usage |
| :--- | :--- | :--- | :--- |
| `BRIGHT_BLACK` | `\033[90m` | `#666666` | Dimmed / Muted |
| `BRIGHT_RED` | `\033[91m` | `#F14C4C` | Critical errors |
| `BRIGHT_GREEN` | `\033[92m` | `#23D18B` | Decision PASS |
| `BRIGHT_YELLOW` | `\033[93m` | `#F5F543` | Decision arrows, Emphasis |
| `BRIGHT_BLUE` | `\033[94m` | `#3B8EEA` | Process steps |
| `BRIGHT_MAGENTA` | `\033[95m` | `#D670D6` | `DEBUG`, Title banners |
| `BRIGHT_CYAN` | `\033[96m` | `#29B8DB` | `HEADER`, Tree headers |
| `BRIGHT_WHITE` | `\033[97m` | `#FFFFFF` | Tree detail values, messages |

### Background Colors (SGR 40–47)
- `BG_BLACK` (`\033[40m`), `BG_RED` (`\033[41m`), `BG_GREEN` (`\033[42m`), `BG_YELLOW` (`\033[43m`)
- `BG_BLUE` (`\033[44m`), `BG_MAGENTA` (`\033[45m`), `BG_CYAN` (`\033[46m`), `BG_WHITE` (`\033[47m`)

### Text Styles & Reset
- `BOLD` (`\033[1m`), `DIM` (`\033[2m`), `ITALIC` (`\033[3m`), `UNDERLINE` (`\033[4m`), `REVERSE` (`\033[7m`)
- `RESET` (`\033[0m`) - **MUST** be appended to restore default terminal styling after every styled token.

---

## 3. Formatting Tokens & Semantic Prefixes

### Mode Prefixes
When emitting level-based log messages:

| Level | Color Mode Prefix | Color Mode Style | Colorless Mode Prefix |
| :--- | :--- | :--- | :--- |
| **Error** | `ERROR:` | `Colors.RED + Colors.BOLD` | `[ERROR]` |
| **Warning** | `WARNING:` | `Colors.YELLOW + Colors.BOLD` | `[WARNING]` |
| **Success** | `SUCCESS:` | `Colors.GREEN + Colors.BOLD` | `[OK]` |
| **Info** | `INFO:` | `Colors.CYAN` | `[INFO]` |
| **Debug** | `DEBUG:` | `Colors.BRIGHT_MAGENTA + Colors.BOLD` | `[DEBUG]` |
| **File Saved** | `Saved:` | `Colors.GREEN` | `Saved:` |

---

## 4. Visual Layouts & Tree Box Drawing

### A. Application Title (`log_application_title`)
- **Default Width**: `60` (or `title.length + 4`, whichever is larger).
- **Color Mode Border**: UTF-8 Double Box Drawing (`╔`, `═`, `╗`, `║`, `╚`, `╝`). Style: `Colors.BRIGHT_MAGENTA + Colors.BOLD`.
- **Colorless Mode Border**: ASCII characters (`+`, `-`, `|`).
- **Padding**: Center aligned inside the box frame.

#### Color Mode Box:
```
╔════════════════════════════════════════════════════╗
║            CHRONICLE DEMO (COLOR MODE)             ║
╚════════════════════════════════════════════════════╝
```

#### Colorless Mode Box:
```
+----------------------------------------------------+
|          CHRONICLE DEMO (COLORLESS MODE)           |
+----------------------------------------------------+
```

---

### B. Structured Tree Logging (`StructuredLogger`)
The tree logger renders hierarchical execution pipelines. Tree indents use 2 spaces (`'  '`) per `indent_level`.

1. **`log_banner(title, width=54)`**:
   - Standard width: `54` (minimum `title.length + 6`).
   - Title text format: `[TITLE_IN_UPPERCASE]`. Left padded by 1 space.
   - **Color Mode**: `Colors.HEADER + Colors.BOLD` using `+`, `-`, `|`.
   - **Colorless Mode**: Plain ASCII `+`, `-`, `|`.

2. **`log_section(category, indent_level=0)`**:
   - Glyph: `|--`
   - **Color Mode**: `|--` in `BRIGHT_CYAN`, `category:` in `BRIGHT_CYAN + BOLD`.
   - **Colorless Mode**: `|-- category:`

3. **`log_detail(label, value, indent_level=0)`**:
   - Glyph: `+--`
   - Label alignment: Left-justified to width `22`.
   - Format: `+-- <label pad 22> : <value>`
   - **Color Mode**: `+--` in `BRIGHT_CYAN`, label in `CYAN + BOLD`, value in `BRIGHT_WHITE + BOLD`.
   - **Colorless Mode**: Plain text.

4. **`log_decision(action, detail=None, indent_level=0)`**:
   - Glyph: `+--> DECISION:`
   - Format with detail: `+--> DECISION: <action> -> <detail>`
   - Format without detail: `+--> DECISION: <action>`
   - **Color Mode**: Arrow in `BRIGHT_YELLOW + BOLD`, action in `BRIGHT_GREEN + BOLD`, detail in `BRIGHT_WHITE`.
   - **Colorless Mode**: Plain text.

5. **`log_message(message, indent_level=0)`**:
   - Glyph: `|--`
   - Format: `|-- <message>`
   - **Color Mode**: `|--` in `BRIGHT_CYAN`, message in `BRIGHT_WHITE`.
   - **Colorless Mode**: Plain text.

---

## 5. Unified API Signatures Across Languages

Each language implementation provides zero-dependency native functions and a `StructuredLogger` class (or namespace/struct), respecting language-native casing conventions (e.g. `snake_case` for Python, `camelCase` for TypeScript/Dart/Kotlin, `PascalCase` for Go and C#).

### Core Global Functions
- Mode Control: `set_color_mode(bool)`, `get_color_mode()`, `set_colorless_mode(bool)`, `set_ascii_mode(bool)`, `get_ascii_mode()`
- Semantic Loggers: `log_error(msg)`, `log_warning(msg)`, `log_success(msg)`, `log_info(msg)`, `log_debug(msg)` (default debug indent: 2 tabs)
- Structural Loggers: `log_application_title(title, width)`, `log_section_header(title)`, `log_subsection(title)`, `log_step(step, total, desc)`, `log_file_saved(path)`, `log_final_result(success, msg)`

### StructuredLogger API
- `log_banner(title, width)`
- `log_section(category, indent_level)`
- `log_detail(label, value, indent_level)`
- `log_decision(action, detail, indent_level)`
- `log_message(message, indent_level)`
