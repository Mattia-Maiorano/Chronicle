# Chronicle [![CI](https://github.com/Mattia-Maiorano/Chronicle/actions/workflows/ci.yml/badge.svg)](https://github.com/Mattia-Maiorano/Chronicle/actions/workflows/ci.yml)

A lightweight, zero-dependency multi-language logging system for Python, TypeScript, Go, Dart, Kotlin, and C# / Unity applications.

---

## Overview

**Chronicle** provides structured terminal logging with support for indentation, spacing, ANSI colors, semantic message types, decision tree formatting, and a **Colorless Mode** for plain-text environments (e.g. CI logs, legacy terminals, file redirects).

All language implementations adhere to a single unified specification documented in [SPEC.md](SPEC.md) to guarantee exact visual parity.

---

## Monorepo Architecture

```
Chronicle/
├── SPEC.md         # Universal formatting & API specification sheet
├── python/         # Python SDK & PyPI package
├── typescript/     # TypeScript / Node.js SDK
├── go/             # Go module
├── dart/           # Dart / Flutter package
├── kotlin/         # Kotlin / JVM package
└── csharp/         # C# / Unity package
```

---

## Language Quickstarts

### 🐍 Python (`python/`)

```python
from chronicle import StructuredLogger, set_color_mode, log_info, log_decision

# Toggles global color / colorless modes
set_color_mode(True)

log_info("Starting data pipeline...")

# Structured Tree Logging
StructuredLogger.log_banner("DATA PROCESSING ENGINE", width=54)
StructuredLogger.log_section("Execution Phase")
StructuredLogger.log_detail("Batch size", 64)
StructuredLogger.log_decision("PASS", "Quality score 0.96 >= 0.85 threshold")
```

---

### 🟦 TypeScript / Node.js (`typescript/`)

```typescript
import { StructuredLogger, setColorMode, logInfo } from "@mattia-maiorano/chronicle";

setColorMode(true);

logInfo("Starting data pipeline...");

StructuredLogger.logBanner("DATA PROCESSING ENGINE", 54);
StructuredLogger.logSection("Execution Phase");
StructuredLogger.logDetail("Batch size", "64");
StructuredLogger.logDecision("PASS", "Quality score 0.96 >= 0.85 threshold");
```

---

### 🐹 Go (`go/`)

```go
package main

import "github.com/Mattia-Maiorano/Chronicle/go"

func main() {
    chronicle.SetColorMode(true)

    chronicle.LogInfo("Starting data pipeline...")

    chronicle.LogBanner("DATA PROCESSING ENGINE", 54)
    chronicle.LogSection("Execution Phase")
    chronicle.LogDetail("Batch size", 64)
    chronicle.LogDecision("PASS", "Quality score 0.96 >= 0.85 threshold")
}
```

---

### 🎯 Dart / Flutter (`dart/`)

```dart
import 'package:chronicle/chronicle.dart';

void main() {
  setColorMode(true);

  logInfo("Starting data pipeline...");

  StructuredLogger.logBanner("DATA PROCESSING ENGINE", width: 54);
  StructuredLogger.logSection("Execution Phase");
  StructuredLogger.logDetail("Batch size", 64);
  StructuredLogger.logDecision("PASS", detail: "Quality score 0.96 >= 0.85 threshold");

  // Example table logging
  StructuredLogger.logTable([
    ["Epoch", "Losses", "Errors", "Stats"],
    ["024/040", "Train Total: 3.49643 (Pred: 3.19063, Probe: 0.30581)", "Pos Err: 0.69107 | Vel Err: 0.73560", "Spike Rate: Train 0.110 / Val 0.111 | Grad Norm: 0.6237"],
  ]);

}
```

---

### 🟪 Kotlin (`kotlin/`)

```kotlin
import chronicle.*

fun main() {
    setColorMode(true)

    logInfo("Starting data pipeline...")

    StructuredLogger.logBanner("DATA PROCESSING ENGINE", width = 54)
    StructuredLogger.logSection("Execution Phase")
    StructuredLogger.logDetail("Batch size", 64)
    StructuredLogger.logDecision("PASS", detail = "Quality score 0.96 >= 0.85 threshold")
}
```

---

### 🟢 C# / Unity (`csharp/`)

```csharp
using Chronicle;

// Supports standard console out or UnityEngine.Debug.Log under UNITY_ENGINE
ChronicleLogger.SetColorMode(true);

ChronicleLogger.LogInfo("Starting data pipeline...");

StructuredLogger.LogBanner("DATA PROCESSING ENGINE", 54);
StructuredLogger.LogSection("Execution Phase");
StructuredLogger.LogDetail("Batch size", 64);
StructuredLogger.LogDecision("PASS", "Quality score 0.96 >= 0.85 threshold");
```

---

## Visual Output Demo

Chronicle produces identical terminal output across all 6 languages:

### Color Mode
```
+----------------------------------------------------+
| [DATA PROCESSING ENGINE]                           |
+----------------------------------------------------+


  |-- Execution Phase:
  +-- Batch size             : 64
  +-- Execution latency      : 14.2ms

  +--> DECISION: PASS -> Quality score 0.96 >= 0.85 threshold

  |-- Pipeline ready for next batch
```

### Colorless Mode (`set_color_mode(False)`)
```
[INFO] Starting pipeline execution in Colorless Mode...
[Step 1/3] Initialization
		[DEBUG] Running internal task for Initialization
[OK] Initialization complete

+----------------------------------------------------+
| [DATA PROCESSING ENGINE]                           |
+----------------------------------------------------+

  |-- Execution Phase:
  +-- Batch size             : 64
  +-- Execution latency      : 14.2ms

  +--> DECISION: PASS -> Quality score 0.96 >= 0.85 threshold
```

---

## Live Dashboard & Layout Framework

Chronicle includes a zero-dependency, rich-like terminal rendering framework designed to build live, responsive dashboards that update in place across Python, TypeScript, Go, Dart, Kotlin, and C#.

```python
from chronicle import (
    LiveEngine, Layout, Panel, LiveTable, Column,
    RollingLogStream, Badge, ProgressBar, Text, Fixed, Flex,
    Colors
)

# 1. Setup Data Components
stream = RollingLogStream(max_lines=50)
table = LiveTable([
    Column("Task", min_width=15, flex=2),
    Column("Status", min_width=10, align="center"),
    Column("Progress", flex=3)
])

p1 = ProgressBar(100, 0, "Build")
table.add_row("task1", ["Frontend", Badge("RUNNING", "RUNNING"), p1])

# 2. Compose Layout
main_layout = Layout(Layout.VERTICAL)
main_layout.add(Panel(Text("LIVE PIPELINE STATUS", style=Colors.BRIGHT_MAGENTA, align=Text.CENTER), border_style=Panel.ROUNDED), Fixed(3))
main_layout.add(Panel(table, title="Active Tasks", border_style=Panel.DOUBLE), Flex(1))
main_layout.add(Panel(stream, title="Timeline Event Stream", border_style=Panel.CHRONICLE_TREE), Flex(1))

# 3. Run Live Engine
with LiveEngine(main_layout, mode=LiveEngine.ALTERNATE_SCREEN, refresh_rate_hz=10, redirect_stdout=True, stream=stream):
    p1.update(50)
```

---

## Specification

For complete ANSI palette escape codes, border box glyphs, line padding conventions, and API method signatures, see the [SPEC.md](SPEC.md) document.

---

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
