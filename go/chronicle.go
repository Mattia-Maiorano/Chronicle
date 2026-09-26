// Package chronicle provides a flexible, colorized, and colorless structured logging system.
package chronicle

import (
	"fmt"
	"strings"
	"sync"
)

var (
	mu        sync.RWMutex
	colorMode = true
)

// SetColorMode enables or disables global color mode.
func SetColorMode(enabled bool) {
	mu.Lock()
	defer mu.Unlock()
	colorMode = enabled
}

// GetColorMode returns the current color mode status.
func GetColorMode() bool {
	mu.RLock()
	defer mu.RUnlock()
	return colorMode
}

// SetColorlessMode enables or disables colorless mode.
func SetColorlessMode(enabled bool) {
	SetColorMode(!enabled)
}

// SetAsciiMode is an alias for SetColorlessMode.
func SetAsciiMode(enabled bool) {
	SetColorlessMode(enabled)
}

// GetAsciiMode returns whether colorless/ASCII mode is active.
func GetAsciiMode() bool {
	return !GetColorMode()
}

// Colors ANSI escape codes for terminal styling.
type ColorPalette struct {
	Black         string
	Red           string
	Green         string
	Yellow        string
	Blue          string
	Magenta       string
	Cyan          string
	White         string
	BrightBlack   string
	BrightRed     string
	BrightGreen   string
	BrightYellow  string
	BrightBlue    string
	BrightMagenta string
	BrightCyan    string
	BrightWhite   string
	BgBlack       string
	BgRed         string
	BgGreen       string
	BgYellow      string
	BgBlue        string
	BgMagenta     string
	BgCyan        string
	BgWhite       string
	Bold          string
	Dim           string
	Italic        string
	Underline     string
	Blink         string
	Reverse       string
	Reset         string

	// Semantic colors
	Error    string
	Warning  string
	Success  string
	Info     string
	Debug    string
	Header   string
	Emphasis string
}

var Colors = ColorPalette{
	Black:         "\033[30m",
	Red:           "\033[31m",
	Green:         "\033[32m",
	Yellow:        "\033[33m",
	Blue:          "\033[34m",
	Magenta:       "\033[35m",
	Cyan:          "\033[36m",
	White:         "\033[37m",
	BrightBlack:   "\033[90m",
	BrightRed:     "\033[91m",
	BrightGreen:   "\033[92m",
	BrightYellow:  "\033[93m",
	BrightBlue:    "\033[94m",
	BrightMagenta: "\033[95m",
	BrightCyan:    "\033[96m",
	BrightWhite:   "\033[97m",
	BgBlack:       "\033[40m",
	BgRed:         "\033[41m",
	BgGreen:       "\033[42m",
	BgYellow:      "\033[43m",
	BgBlue:        "\033[44m",
	BgMagenta:     "\033[45m",
	BgCyan:        "\033[46m",
	BgWhite:       "\033[47m",
	Bold:          "\033[1m",
	Dim:           "\033[2m",
	Italic:        "\033[3m",
	Underline:     "\033[4m",
	Blink:         "\033[5m",
	Reverse:       "\033[7m",
	Reset:         "\033[0m",

	Error:    "\033[31m",
	Warning:  "\033[33m",
	Success:  "\033[32m",
	Info:     "\033[36m",
	Debug:    "\033[95m",
	Header:   "\033[96m",
	Emphasis: "\033[93m",
}

// Log logs a formatted message with indentation, spacing, and color.
func Log(indentationTabs int, newlineBefore int, newlineAfter int, color string, content string, colorModeOverride ...bool) {
	useColor := GetColorMode()
	if len(colorModeOverride) > 0 {
		useColor = colorModeOverride[0]
	}

	if newlineBefore > 0 {
		fmt.Print(strings.Repeat("\n", newlineBefore-1))
	}

	indentation := strings.Repeat("\t", indentationTabs)
	var message string

	if color != "" && useColor {
		message = fmt.Sprintf("%s%s%s%s", indentation, color, content, Colors.Reset)
	} else {
		message = fmt.Sprintf("%s%s", indentation, content)
	}

	fmt.Print(message)

	if newlineAfter > 0 {
		fmt.Print(strings.Repeat("\n", newlineAfter))
	} else {
		fmt.Println()
	}
}

// LogNewline prints specified number of newlines.
func LogNewline(count ...int) {
	c := 1
	if len(count) > 0 {
		c = count[0]
	}
	if c > 1 {
		fmt.Print(strings.Repeat("\n", c-1))
	}
	fmt.Println()
}

// LogApplicationTitle logs a stylized application header with borders.
func LogApplicationTitle(title string, widthOpt ...int) {
	width := 60
	if len(widthOpt) > 0 {
		width = widthOpt[0]
	}
	useColor := GetColorMode()
	titleLength := len(title)

	if titleLength+2 > width-2 {
		width = titleLength + 4
	}

	padding := (width - 2 - titleLength) / 2
	paddedTitle := strings.Repeat(" ", padding) + title + strings.Repeat(" ", width-2-titleLength-padding)

	var topBorder, middleLine, bottomBorder, color string
	if useColor {
		topBorder = "╔" + strings.Repeat("═", width-2) + "╗"
		middleLine = "║" + paddedTitle + "║"
		bottomBorder = "╚" + strings.Repeat("═", width-2) + "╝"
		color = Colors.BrightMagenta + Colors.Bold
	} else {
		topBorder = "+" + strings.Repeat("-", width-2) + "+"
		middleLine = "|" + paddedTitle + "|"
		bottomBorder = "+" + strings.Repeat("-", width-2) + "+"
		color = ""
	}

	LogNewline(2)
	Log(0, 1, 0, color, topBorder, useColor)
	Log(0, 0, 0, color, middleLine, useColor)
	Log(0, 0, 1, color, bottomBorder, useColor)
	LogNewline(2)
}

// LogSectionHeader logs a section header with consistent divider lines.
func LogSectionHeader(title string, indentationTabs ...int) {
	indent := 0
	if len(indentationTabs) > 0 {
		indent = indentationTabs[0]
	}
	useColor := GetColorMode()
	var color string
	if useColor {
		color = Colors.Header + Colors.Bold
	}
	separator := strings.Repeat("=", 60)

	Log(indent, 1, 0, color, separator, useColor)
	Log(indent, 0, 0, color, title, useColor)
	Log(indent, 0, 1, color, separator, useColor)
	LogNewline()
}

// LogSubsection logs a subsection header.
func LogSubsection(title string, indentationTabs ...int) {
	indent := 0
	if len(indentationTabs) > 0 {
		indent = indentationTabs[0]
	}
	useColor := GetColorMode()
	var color string
	if useColor {
		color = Colors.BrightCyan
	}
	separator := strings.Repeat("-", 40)

	Log(indent, 1, 0, color, separator, useColor)
	Log(indent, 0, 0, color, title, useColor)
	Log(indent, 0, 0, color, separator, useColor)
	LogNewline()
}

// LogError logs an error message.
func LogError(message string, indentationTabs ...int) {
	indent := 0
	if len(indentationTabs) > 0 {
		indent = indentationTabs[0]
	}
	useColor := GetColorMode()
	prefix := "[ERROR]"
	var color string
	if useColor {
		prefix = "ERROR:"
		color = Colors.Error + Colors.Bold
	}
	Log(indent, 0, 0, color, fmt.Sprintf("%s %s", prefix, message), useColor)
}

// LogWarning logs a warning message.
func LogWarning(message string, indentationTabs ...int) {
	indent := 0
	if len(indentationTabs) > 0 {
		indent = indentationTabs[0]
	}
	useColor := GetColorMode()
	prefix := "[WARNING]"
	var color string
	if useColor {
		prefix = "WARNING:"
		color = Colors.Warning + Colors.Bold
	}
	Log(indent, 0, 0, color, fmt.Sprintf("%s %s", prefix, message), useColor)
}

// LogSuccess logs a success message.
func LogSuccess(message string, indentationTabs ...int) {
	indent := 0
	if len(indentationTabs) > 0 {
		indent = indentationTabs[0]
	}
	useColor := GetColorMode()
	prefix := "[OK]"
	var color string
	if useColor {
		prefix = "SUCCESS:"
		color = Colors.Success + Colors.Bold
	}
	Log(indent, 0, 0, color, fmt.Sprintf("%s %s", prefix, message), useColor)
}

// LogInfo logs an informational message.
func LogInfo(message string, indentationTabs ...int) {
	indent := 0
	if len(indentationTabs) > 0 {
		indent = indentationTabs[0]
	}
	useColor := GetColorMode()
	prefix := "[INFO]"
	var color string
	if useColor {
		prefix = "INFO:"
		color = Colors.Info
	}
	Log(indent, 0, 0, color, fmt.Sprintf("%s %s", prefix, message), useColor)
}

// LogDebug logs a debug message (default 2 tabs).
func LogDebug(message string, indentationTabs ...int) {
	indent := 2
	if len(indentationTabs) > 0 {
		indent = indentationTabs[0]
	}
	useColor := GetColorMode()
	prefix := "[DEBUG]"
	var color string
	if useColor {
		prefix = "DEBUG:"
		color = Colors.Debug + Colors.Bold
	}
	Log(indent, 0, 0, color, fmt.Sprintf("%s %s", prefix, message), useColor)
}

// LogStep logs a step in a multi-step process.
func LogStep(stepNumber int, totalSteps int, description string, indentationTabs ...int) {
	indent := 0
	if len(indentationTabs) > 0 {
		indent = indentationTabs[0]
	}
	useColor := GetColorMode()
	var color string
	if useColor {
		color = Colors.BrightBlue + Colors.Bold
	}
	LogNewline()
	Log(indent, 1, 0, color, fmt.Sprintf("[Step %d/%d] %s", stepNumber, totalSteps, description), useColor)
	LogNewline()
}

// LogFileSaved logs a file save operation.
func LogFileSaved(filepath string, indentationTabs ...int) {
	indent := 1
	if len(indentationTabs) > 0 {
		indent = indentationTabs[0]
	}
	useColor := GetColorMode()
	var color string
	if useColor {
		color = Colors.Success
	}
	Log(indent, 0, 0, color, fmt.Sprintf("Saved: %s", filepath), useColor)
}

// LogFinalResult logs a final execution result banner.
func LogFinalResult(success bool, message string, widthOpt ...int) {
	width := 60
	if len(widthOpt) > 0 {
		width = widthOpt[0]
	}
	useColor := GetColorMode()
	var color string
	if useColor {
		if success {
			color = Colors.Success + Colors.Bold
		} else {
			color = Colors.Error + Colors.Bold
		}
	}
	separator := strings.Repeat("=", width)

	LogNewline(2)
	Log(0, 1, 0, color, separator, useColor)
	if success {
		LogSuccess(message)
	} else {
		LogError(message)
	}
	Log(0, 0, 1, color, separator, useColor)
	LogNewline(2)
}

// --- Structured Tree Logger ---

type StructuredLogger struct{}

// LogBanner logs a top-level section banner.
func (s StructuredLogger) LogBanner(title string, widthOpt ...int) {
	LogBanner(title, widthOpt...)
}

// LogSection logs an indented category section.
func (s StructuredLogger) LogSection(category string, indentLevelOpt ...int) {
	LogSection(category, indentLevelOpt...)
}

// LogDetail logs a key-value metric in the tree.
func (s StructuredLogger) LogDetail(label string, value interface{}, indentLevelOpt ...int) {
	LogDetail(label, value, indentLevelOpt...)
}

// LogDecision logs a decision transition arrow.
func (s StructuredLogger) LogDecision(action string, detail string, indentLevelOpt ...int) {
	LogDecision(action, detail, indentLevelOpt...)
}

// LogMessage logs a raw message in the tree.
func (s StructuredLogger) LogMessage(message string, indentLevelOpt ...int) {
	LogMessage(message, indentLevelOpt...)
}

// LogBanner logs a top-level section banner.
func LogBanner(title string, widthOpt ...int) {
	width := 54
	if len(widthOpt) > 0 {
		width = widthOpt[0]
	}
	useColor := GetColorMode()
	minWidth := len(title) + 6
	if width < minWidth {
		width = minWidth
	}

	lineDashes := strings.Repeat("-", width-2)
	rawPadded := fmt.Sprintf("| [%s]", strings.ToUpper(title))
	padded := fmt.Sprintf("%-*s", width-1, rawPadded)

	if useColor {
		c := Colors.Header + Colors.Bold
		r := Colors.Reset
		top := fmt.Sprintf("%s+%s+%s", c, lineDashes, r)
		mid := fmt.Sprintf("%s%s|%s", c, padded, r)
		bot := fmt.Sprintf("%s+%s+%s", c, lineDashes, r)
		fmt.Printf("\n%s\n%s\n%s\n\n", top, mid, bot)
	} else {
		top := fmt.Sprintf("+%s+", lineDashes)
		mid := fmt.Sprintf("%s|", padded)
		bot := fmt.Sprintf("+%s+", lineDashes)
		fmt.Printf("\n%s\n%s\n%s\n\n", top, mid, bot)
	}
}

// LogSection logs an indented category header.
func LogSection(category string, indentLevelOpt ...int) {
	indentLevel := 0
	if len(indentLevelOpt) > 0 {
		indentLevel = indentLevelOpt[0]
	}
	useColor := GetColorMode()
	indent := strings.Repeat("  ", indentLevel)
	catStr := category
	if !strings.HasSuffix(catStr, ":") {
		catStr += ":"
	}

	if useColor {
		cTree := Colors.BrightCyan
		cCat := Colors.BrightCyan + Colors.Bold
		r := Colors.Reset
		fmt.Printf("\n%s  %s|--%s %s%s%s\n", indent, cTree, r, cCat, catStr, r)
	} else {
		fmt.Printf("\n%s  |-- %s\n", indent, catStr)
	}
}

// LogDetail logs a metric key-value detail item.
func LogDetail(label string, value interface{}, indentLevelOpt ...int) {
	indentLevel := 0
	if len(indentLevelOpt) > 0 {
		indentLevel = indentLevelOpt[0]
	}
	useColor := GetColorMode()
	indent := strings.Repeat("  ", indentLevel+1)
	formattedLabel := fmt.Sprintf("%-22s", label)

	if useColor {
		cTree := Colors.BrightCyan
		cLabel := Colors.Cyan + Colors.Bold
		cVal := Colors.BrightWhite + Colors.Bold
		r := Colors.Reset
		fmt.Printf("%s%s+--%s %s%s%s : %s%v%s\n", indent, cTree, r, cLabel, formattedLabel, r, cVal, value, r)
	} else {
		fmt.Printf("%s+-- %s : %v\n", indent, formattedLabel, value)
	}
}

// LogDecision logs a decision transition arrow.
func LogDecision(action string, detail string, indentLevelOpt ...int) {
	indentLevel := 0
	if len(indentLevelOpt) > 0 {
		indentLevel = indentLevelOpt[0]
	}
	useColor := GetColorMode()
	indent := strings.Repeat("  ", indentLevel)

	if useColor {
		cArrow := Colors.BrightYellow + Colors.Bold
		cAction := Colors.BrightGreen + Colors.Bold
		cDetail := Colors.BrightWhite
		r := Colors.Reset

		if strings.TrimSpace(detail) != "" {
			fmt.Printf("\n%s  %s+--> DECISION:%s %s%s%s -> %s%s%s\n\n", indent, cArrow, r, cAction, action, r, cDetail, detail, r)
		} else {
			fmt.Printf("\n%s  %s+--> DECISION:%s %s%s%s\n\n", indent, cArrow, r, cAction, action, r)
		}
	} else {
		if strings.TrimSpace(detail) != "" {
			fmt.Printf("\n%s  +--> DECISION: %s -> %s\n\n", indent, action, detail)
		} else {
			fmt.Printf("\n%s  +--> DECISION: %s\n\n", indent, action)
		}
	}
}

// LogMessage logs a message item in the tree.
func LogMessage(message string, indentLevelOpt ...int) {
	indentLevel := 0
	if len(indentLevelOpt) > 0 {
		indentLevel = indentLevelOpt[0]
	}
	useColor := GetColorMode()
	indent := strings.Repeat("  ", indentLevel)

	if useColor {
		cTree := Colors.BrightCyan
		cMsg := Colors.BrightWhite
		r := Colors.Reset
		fmt.Printf("%s%s|--%s %s%s%s\n", indent, cTree, r, cMsg, message, r)
	} else {
		fmt.Printf("%s|-- %s\n", indent, message)
	}
}

// LogTable logs a formatted table with optional headers and alignments.
func LogTable(rows [][]string, headers []string, alignments []string, colorMode ...bool) {
    useColor := GetColorMode()
    if len(colorMode) > 0 {
        useColor = colorMode[0]
    }
    // Determine column count
    colCount := 0
    if len(headers) > 0 {
        colCount = len(headers)
    } else if len(rows) > 0 {
        colCount = len(rows[0])
    }
    if colCount == 0 {
        return
    }
    // Compute max width per column
    colWidths := make([]int, colCount)
    for i, h := range headers {
        if len(h) > colWidths[i] {
            colWidths[i] = len(h)
        }
    }
    for _, row := range rows {
        for i, cell := range row {
            if len(cell) > colWidths[i] {
                colWidths[i] = len(cell)
            }
        }
    }
    // Default alignments to left
    if len(alignments) < colCount {
        newAlign := make([]string, colCount)
        copy(newAlign, alignments)
        for i := len(alignments); i < colCount; i++ {
            newAlign[i] = "left"
        }
        alignments = newAlign
    }
    // Border characters based on color mode
    var tl, tr, bl, br, horiz, vert, mid string
    if useColor {
        tl, tr, bl, br, horiz, vert, mid = "┌", "┐", "└", "┘", "─", "│", "├"
    } else {
        tl, tr, bl, br, horiz, vert, mid = "+", "+", "+", "+", "-", "|", "+"
    }
    // Helper to pad cells
    pad := func(content string, width int, align string) string {
        switch align {
        case "right":
            return fmt.Sprintf("%*s", width, content)
        case "center":
            left := (width - len(content)) / 2
            right := width - len(content) - left
            return fmt.Sprintf("%s%s%s", strings.Repeat(" ", left), content, strings.Repeat(" ", right))
        default: // left
            return fmt.Sprintf("%-*s", width, content)
        }
    }
    // Build top border
    var sb strings.Builder
    sb.WriteString(tl)
    for i, w := range colWidths {
        sb.WriteString(strings.Repeat(horiz, w+2))
        if i < colCount-1 {
            sb.WriteString(horiz)
        }
    }
    sb.WriteString(tr)
    Log(0, 1, 0, "", sb.String())
    // Header row
    if len(headers) > 0 {
        sb.Reset()
        sb.WriteString(vert)
        for i, h := range headers {
            padded := pad(h, colWidths[i], alignments[i])
            sb.WriteString(" " + padded + " " + vert)
        }
        Log(0, 0, 0, "", sb.String())
        // Separator after header
        sb.Reset()
        sb.WriteString(mid)
        for i, w := range colWidths {
            sb.WriteString(strings.Repeat(horiz, w+2))
            if i < colCount-1 {
                sb.WriteString(horiz)
            }
        }
        sb.WriteString(mid)
        Log(0, 0, 0, "", sb.String())
    }
    // Data rows
    for _, row := range rows {
        sb.Reset()
        sb.WriteString(vert)
        for i, cell := range row {
            padded := pad(cell, colWidths[i], alignments[i])
            sb.WriteString(" " + padded + " " + vert)
        }
        Log(0, 0, 0, "", sb.String())
    }
    // Bottom border
    sb.Reset()
    sb.WriteString(bl)
    for i, w := range colWidths {
        sb.WriteString(strings.Repeat(horiz, w+2))
        if i < colCount-1 {
            sb.WriteString(horiz)
        }
    }
    sb.WriteString(br)
    Log(0, 0, 1, "", sb.String())
}
