package chronicle

import (
	"fmt"
	"os"
	"os/signal"
	"regexp"
	"strings"
	"sync"
	"syscall"
	"time"
)

// --- Geometry ---

// Size represents 2D dimensions.
type Size struct {
	Width  int
	Height int
}

// Point represents a 2D coordinate.
type Point struct {
	X int
	Y int
}

// Segment represents a piece of text with optional ANSI style.
type Segment struct {
	Text  string
	Style string
}

// VisualMeter provides helpers for measuring visual string lengths in the terminal.
type VisualMeter struct{}

var ansiRegex = regexp.MustCompile(`\x1b\[[0-9;]*[a-zA-Z]`)

// StripANSI removes all ANSI escape sequences from a string.
func (VisualMeter) StripANSI(text string) string {
	return ansiRegex.ReplaceAllString(text, "")
}

// Measure returns the visual column width of a string.
func (v VisualMeter) Measure(text string) int {
	clean := v.StripANSI(text)
	return len([]rune(clean))
}

var visualMeter VisualMeter

// TerminalMetrics provides terminal dimension helpers.
type TerminalMetrics struct{}

// GetSize returns the current terminal dimensions or fallback 80x24.
func (TerminalMetrics) GetSize() Size {
	// Fallback standard terminal size
	return Size{Width: 80, Height: 24}
}

var terminalMetrics TerminalMetrics

// --- Layout Base ---

// RenderContext contains rendering configuration and terminal bounds.
type RenderContext struct {
	Bounds    Size
	ColorMode bool
	AsciiMode bool
}

// Renderable is implemented by all visual dashboard components.
type Renderable interface {
	Measure(ctx RenderContext) Size
	Render(bounds Size, ctx RenderContext) [][]Segment
}

// --- Layout Policies ---

// Policy defines sizing policy for splitter layout.
type Policy interface {
	isPolicy()
}

// FixedPolicy gives a fixed number of cells.
type FixedPolicy struct {
	Size int
}

func (FixedPolicy) isPolicy() {}

// FlexPolicy distributes remaining space proportionally by weight.
type FlexPolicy struct {
	Weight int
}

func (FlexPolicy) isPolicy() {}

// RatioPolicy gives a percentage (0.0 - 1.0) of total space.
type RatioPolicy struct {
	Percentage float64
}

func (RatioPolicy) isPolicy() {}

// Helper constructors for policies
func Fixed(size int) FixedPolicy          { return FixedPolicy{Size: size} }
func Flex(weight int) FlexPolicy          { return FlexPolicy{Weight: weight} }
func Ratio(percentage float64) RatioPolicy { return RatioPolicy{Percentage: percentage} }

// --- Layout Primitives ---

const (
	AlignLeft   = "left"
	AlignCenter = "center"
	AlignRight  = "right"
)

// Text represents a styled text block with alignment and truncation.
type Text struct {
	Content     string
	Style       string
	Align       string
	TruncateStr string
}

func NewText(content string, style string, align string) *Text {
	if align == "" {
		align = AlignLeft
	}
	return &Text{
		Content:     content,
		Style:       style,
		Align:       align,
		TruncateStr: "...",
	}
}

func (t *Text) Measure(ctx RenderContext) Size {
	return Size{Width: visualMeter.Measure(t.Content), Height: 1}
}

func (t *Text) Render(bounds Size, ctx RenderContext) [][]Segment {
	if bounds.Width <= 0 || bounds.Height <= 0 {
		return [][]Segment{}
	}

	textLen := visualMeter.Measure(t.Content)
	displayText := t.Content

	if textLen > bounds.Width {
		if bounds.Width >= len(t.TruncateStr) {
			clean := visualMeter.StripANSI(t.Content)
			runes := []rune(clean)
			allowed := bounds.Width - len(t.TruncateStr)
			if allowed < 0 {
				allowed = 0
			}
			if allowed > len(runes) {
				allowed = len(runes)
			}
			displayText = string(runes[:allowed]) + t.TruncateStr
			textLen = bounds.Width
		} else {
			displayText = ""
			textLen = 0
		}
	}

	padTotal := bounds.Width - textLen
	if padTotal < 0 {
		padTotal = 0
	}
	var padLeft, padRight int
	switch t.Align {
	case AlignCenter:
		padLeft = padTotal / 2
		padRight = padTotal - padLeft
	case AlignRight:
		padLeft = padTotal
		padRight = 0
	default:
		padLeft = 0
		padRight = padTotal
	}

	style := ""
	if ctx.ColorMode {
		style = t.Style
	}

	row := []Segment{}
	if padLeft > 0 {
		row = append(row, Segment{Text: strings.Repeat(" ", padLeft)})
	}
	row = append(row, Segment{Text: displayText, Style: style})
	if padRight > 0 {
		row = append(row, Segment{Text: strings.Repeat(" ", padRight)})
	}

	return [][]Segment{row}
}

// Rule represents a horizontal line across the container with optional title.
type Rule struct {
	Title     string
	Style     string
	Character string
}

func NewRule(title string, style string, character string) *Rule {
	if character == "" {
		character = "─"
	}
	return &Rule{Title: title, Style: style, Character: character}
}

func (r *Rule) Measure(ctx RenderContext) Size {
	return Size{Width: ctx.Bounds.Width, Height: 1}
}

func (r *Rule) Render(bounds Size, ctx RenderContext) [][]Segment {
	if bounds.Width <= 0 || bounds.Height <= 0 {
		return [][]Segment{}
	}

	ch := r.Character
	if !ctx.ColorMode || ctx.AsciiMode {
		ch = "-"
	}

	style := ""
	if ctx.ColorMode {
		style = r.Style
	}

	if r.Title == "" {
		return [][]Segment{{Segment{Text: strings.Repeat(ch, bounds.Width), Style: style}}}
	}

	titleText := fmt.Sprintf(" %s ", r.Title)
	titleLen := visualMeter.Measure(titleText)
	if titleLen >= bounds.Width {
		runes := []rune(titleText)
		if len(runes) > bounds.Width {
			runes = runes[:bounds.Width]
		}
		return [][]Segment{{Segment{Text: string(runes), Style: style}}}
	}

	leftDash := (bounds.Width - titleLen) / 2
	rightDash := bounds.Width - titleLen - leftDash

	row := []Segment{}
	if leftDash > 0 {
		row = append(row, Segment{Text: strings.Repeat(ch, leftDash), Style: style})
	}
	row = append(row, Segment{Text: titleText, Style: style})
	if rightDash > 0 {
		row = append(row, Segment{Text: strings.Repeat(ch, rightDash), Style: style})
	}

	return [][]Segment{row}
}

// Panel Border styles
const (
	BorderRounded       = "rounded"
	BorderSquare        = "square"
	BorderDouble        = "double"
	BorderChronicleTree = "chronicle_tree"
)

type BorderGlyphs struct {
	TL, TR, BL, BR, H, V string
}

var borderStyles = map[string]BorderGlyphs{
	BorderRounded:       {"╭", "╮", "╰", "╯", "─", "│"},
	BorderSquare:        {"┌", "┐", "└", "┘", "─", "│"},
	BorderDouble:        {"╔", "╗", "╚", "╝", "═", "║"},
	BorderChronicleTree: {"+", "+", "+", "+", "-", "|"},
}

// Panel wraps a renderable component in styled borders.
type Panel struct {
	Child       Renderable
	Title       string
	Subtitle    string
	BorderStyle string
	Padding     int
	BorderColor string
}

func NewPanel(child Renderable, title string, subtitle string, borderStyle string) *Panel {
	if borderStyle == "" {
		borderStyle = BorderRounded
	}
	return &Panel{
		Child:       child,
		Title:       title,
		Subtitle:    subtitle,
		BorderStyle: borderStyle,
		Padding:     1,
		BorderColor: "",
	}
}

func (p *Panel) Measure(ctx RenderContext) Size {
	innerCtx := RenderContext{
		Bounds:    Size{Width: ctx.Bounds.Width - 2 - (p.Padding * 2), Height: ctx.Bounds.Height - 2},
		ColorMode: ctx.ColorMode,
		AsciiMode: ctx.AsciiMode,
	}
	childSize := p.Child.Measure(innerCtx)
	return Size{
		Width:  childSize.Width + 2 + (p.Padding * 2),
		Height: childSize.Height + 2,
	}
}

func (p *Panel) Render(bounds Size, ctx RenderContext) [][]Segment {
	if bounds.Width < 2 || bounds.Height < 2 {
		return [][]Segment{}
	}

	glyphs, exists := borderStyles[p.BorderStyle]
	if !exists || !ctx.ColorMode || ctx.AsciiMode {
		glyphs = borderStyles[BorderChronicleTree]
	}

	bStyle := ""
	if ctx.ColorMode {
		bStyle = p.BorderColor
	}

	lines := make([][]Segment, 0, bounds.Height)

	// Top Border
	innerW := bounds.Width - 2
	topRow := []Segment{{Text: glyphs.TL, Style: bStyle}}
	if p.Title != "" {
		tText := fmt.Sprintf(" %s ", p.Title)
		tLen := visualMeter.Measure(tText)
		if tLen >= innerW {
			runes := []rune(tText)
			if len(runes) > innerW {
				runes = runes[:innerW]
			}
			topRow = append(topRow, Segment{Text: string(runes), Style: bStyle})
		} else {
			topRow = append(topRow, Segment{Text: glyphs.H, Style: bStyle})
			topRow = append(topRow, Segment{Text: tText, Style: bStyle})
			topRow = append(topRow, Segment{Text: strings.Repeat(glyphs.H, innerW-1-tLen), Style: bStyle})
		}
	} else {
		topRow = append(topRow, Segment{Text: strings.Repeat(glyphs.H, innerW), Style: bStyle})
	}
	topRow = append(topRow, Segment{Text: glyphs.TR, Style: bStyle})
	lines = append(lines, topRow)

	// Inner Content
	innerH := bounds.Height - 2
	innerBounds := Size{Width: innerW - (p.Padding * 2), Height: innerH}
	if innerBounds.Width < 0 {
		innerBounds.Width = 0
	}
	childLines := p.Child.Render(innerBounds, ctx)

	for y := 0; y < innerH; y++ {
		row := []Segment{{Text: glyphs.V, Style: bStyle}}
		if p.Padding > 0 {
			row = append(row, Segment{Text: strings.Repeat(" ", p.Padding)})
		}

		if y < len(childLines) {
			row = append(row, childLines[y]...)
			lineLen := 0
			for _, seg := range childLines[y] {
				lineLen += visualMeter.Measure(seg.Text)
			}
			pad := innerBounds.Width - lineLen
			if pad > 0 {
				row = append(row, Segment{Text: strings.Repeat(" ", pad)})
			}
		} else {
			row = append(row, Segment{Text: strings.Repeat(" ", innerBounds.Width)})
		}

		if p.Padding > 0 {
			row = append(row, Segment{Text: strings.Repeat(" ", p.Padding)})
		}
		row = append(row, Segment{Text: glyphs.V, Style: bStyle})
		lines = append(lines, row)
	}

	// Bottom Border
	botRow := []Segment{{Text: glyphs.BL, Style: bStyle}}
	if p.Subtitle != "" {
		sText := fmt.Sprintf(" %s ", p.Subtitle)
		sLen := visualMeter.Measure(sText)
		if sLen >= innerW {
			runes := []rune(sText)
			if len(runes) > innerW {
				runes = runes[:innerW]
			}
			botRow = append(botRow, Segment{Text: string(runes), Style: bStyle})
		} else {
			botRow = append(botRow, Segment{Text: glyphs.H, Style: bStyle})
			botRow = append(botRow, Segment{Text: sText, Style: bStyle})
			botRow = append(botRow, Segment{Text: strings.Repeat(glyphs.H, innerW-1-sLen), Style: bStyle})
		}
	} else {
		botRow = append(botRow, Segment{Text: strings.Repeat(glyphs.H, innerW), Style: bStyle})
	}
	botRow = append(botRow, Segment{Text: glyphs.BR, Style: bStyle})
	lines = append(lines, botRow)

	return lines
}

// Splitter directions
const (
	DirectionHorizontal = "horizontal"
	DirectionVertical   = "vertical"
)

type SplitterChild struct {
	Child  Renderable
	Policy Policy
}

// FlexSplitter / Layout arranges children horizontally or vertically according to flex policies.
type FlexSplitter struct {
	Direction string
	Children  []SplitterChild
}

func NewLayout(direction string) *FlexSplitter {
	if direction == "" {
		direction = DirectionHorizontal
	}
	return &FlexSplitter{Direction: direction, Children: []SplitterChild{}}
}

func (s *FlexSplitter) Add(child Renderable, policy Policy) {
	if policy == nil {
		policy = Flex(1)
	}
	s.Children = append(s.Children, SplitterChild{Child: child, Policy: policy})
}

func (s *FlexSplitter) Measure(ctx RenderContext) Size {
	return ctx.Bounds
}

func (s *FlexSplitter) Render(bounds Size, ctx RenderContext) [][]Segment {
	if len(s.Children) == 0 {
		return [][]Segment{}
	}

	totalSize := bounds.Width
	if s.Direction == DirectionVertical {
		totalSize = bounds.Height
	}

	sizes := make([]int, len(s.Children))
	remaining := totalSize

	// 1. Fixed & Ratio
	for i, item := range s.Children {
		switch p := item.Policy.(type) {
		case FixedPolicy:
			sizes[i] = p.Size
			remaining -= p.Size
		case RatioPolicy:
			alloc := int(float64(totalSize) * p.Percentage)
			sizes[i] = alloc
			remaining -= alloc
		}
	}

	// 2. Flex
	flexSum := 0
	for _, item := range s.Children {
		if f, ok := item.Policy.(FlexPolicy); ok {
			flexSum += f.Weight
		}
	}

	if flexSum > 0 && remaining > 0 {
		flexUnit := float64(remaining) / float64(flexSum)
		remFlex := remaining
		for i, item := range s.Children {
			if f, ok := item.Policy.(FlexPolicy); ok {
				alloc := int(float64(f.Weight) * flexUnit)
				sizes[i] = alloc
				remFlex -= alloc
			}
		}
		if remFlex > 0 {
			for i, item := range s.Children {
				if _, ok := item.Policy.(FlexPolicy); ok {
					sizes[i] += remFlex
					break
				}
			}
		}
	}

	type renderedChild struct {
		bounds Size
		lines  [][]Segment
	}
	rendered := make([]renderedChild, len(s.Children))
	for i, item := range s.Children {
		cBounds := Size{Width: sizes[i], Height: bounds.Height}
		if s.Direction == DirectionVertical {
			cBounds = Size{Width: bounds.Width, Height: sizes[i]}
		}
		cCtx := RenderContext{Bounds: cBounds, ColorMode: ctx.ColorMode, AsciiMode: ctx.AsciiMode}
		cLines := item.Child.Render(cBounds, cCtx)
		rendered[i] = renderedChild{bounds: cBounds, lines: cLines}
	}

	lines := [][]Segment{}
	if s.Direction == DirectionHorizontal {
		for y := 0; y < bounds.Height; y++ {
			row := []Segment{}
			for _, rc := range rendered {
				if y < len(rc.lines) {
					row = append(row, rc.lines[y]...)
					cLen := 0
					for _, seg := range rc.lines[y] {
						cLen += visualMeter.Measure(seg.Text)
					}
					pad := rc.bounds.Width - cLen
					if pad > 0 {
						row = append(row, Segment{Text: strings.Repeat(" ", pad)})
					}
				} else {
					row = append(row, Segment{Text: strings.Repeat(" ", rc.bounds.Width)})
				}
			}
			lines = append(lines, row)
		}
	} else {
		for _, rc := range rendered {
			for y := 0; y < rc.bounds.Height; y++ {
				if y < len(rc.lines) {
					lines = append(lines, rc.lines[y])
				} else {
					lines = append(lines, []Segment{{Text: strings.Repeat(" ", bounds.Width)}})
				}
			}
		}
	}

	return lines
}

// --- Components ---

// Badge types
const (
	BadgePass    = "PASS"
	BadgeSuccess = "SUCCESS"
	BadgeFail    = "FAIL"
	BadgeError   = "ERROR"
	BadgeWarn    = "WARN"
	BadgeWarning = "WARNING"
	BadgeInfo    = "INFO"
	BadgeRunning = "RUNNING"
)

// Badge represents a styled status tag.
type Badge struct {
	Text        string
	BadgeType   string
	CustomStyle string
}

func NewBadge(text string, badgeType string) *Badge {
	if badgeType == "" {
		badgeType = BadgeInfo
	}
	return &Badge{Text: text, BadgeType: badgeType}
}

func (b *Badge) Measure(ctx RenderContext) Size {
	return Size{Width: len(b.Text) + 2, Height: 1}
}

func (b *Badge) Render(bounds Size, ctx RenderContext) [][]Segment {
	if bounds.Width <= 0 || bounds.Height <= 0 {
		return [][]Segment{}
	}

	if !ctx.ColorMode {
		return [][]Segment{{{Text: fmt.Sprintf("[%s]", b.Text)}}}
	}

	var style string
	if b.CustomStyle != "" {
		style = b.CustomStyle
	} else {
		switch strings.ToUpper(b.BadgeType) {
		case BadgePass, BadgeSuccess:
			style = "\x1b[42;30;1m" // Green BG, Black Bold Text
		case BadgeFail, BadgeError:
			style = "\x1b[41;97;1m" // Red BG, White Bold Text
		case BadgeWarn, BadgeWarning:
			style = "\x1b[43;30;1m" // Yellow BG, Black Bold Text
		case BadgeRunning:
			style = "\x1b[44;97;1m" // Blue BG, White Bold Text
		default:
			style = "\x1b[46;30;1m" // Cyan BG, Black Bold Text
		}
	}

	return [][]Segment{{{Text: fmt.Sprintf(" %s ", b.Text), Style: style}}}
}

// ProgressBar represents an animated progress indicator with spinner.
type ProgressBar struct {
	mu           sync.Mutex
	Total        int
	Completed    int
	Label        string
	spinnerIdx   int
	spinnerChars []string
}

func NewProgressBar(total int, completed int, label string) *ProgressBar {
	if total <= 0 {
		total = 100
	}
	return &ProgressBar{
		Total:        total,
		Completed:    completed,
		Label:        label,
		spinnerIdx:   0,
		spinnerChars: []string{"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"},
	}
}

func (p *ProgressBar) Update(completed int) {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.Completed = completed
	if p.Completed > p.Total {
		p.Completed = p.Total
	}
	p.spinnerIdx = (p.spinnerIdx + 1) % len(p.spinnerChars)
}

func (p *ProgressBar) Measure(ctx RenderContext) Size {
	return Size{Width: ctx.Bounds.Width, Height: 1}
}

func (p *ProgressBar) Render(bounds Size, ctx RenderContext) [][]Segment {
	p.mu.Lock()
	defer p.mu.Unlock()

	if bounds.Width <= 0 || bounds.Height <= 0 {
		return [][]Segment{}
	}

	pct := float64(p.Completed) / float64(p.Total)
	if pct < 0 {
		pct = 0
	}
	if pct > 1 {
		pct = 1
	}

	pctStr := fmt.Sprintf("%3.0f%%", pct*100)
	spinner := p.spinnerChars[p.spinnerIdx]
	if !ctx.ColorMode || ctx.AsciiMode {
		spinner = "*"
	}

	labelStr := ""
	if p.Label != "" {
		labelStr = p.Label + " "
	}

	fixedWidth := visualMeter.Measure(labelStr) + 1 + 1 + len(pctStr) + 1 // label + spinner + space + pct + space
	barWidth := bounds.Width - fixedWidth
	if barWidth < 5 {
		barWidth = 5
	}

	filled := int(float64(barWidth) * pct)
	empty := barWidth - filled
	if empty < 0 {
		empty = 0
	}

	fillChar := "━"
	emptyChar := "╌"
	if !ctx.ColorMode || ctx.AsciiMode {
		fillChar = "="
		emptyChar = "-"
	}

	row := []Segment{}
	if labelStr != "" {
		row = append(row, Segment{Text: labelStr, Style: "\x1b[97m"})
	}
	row = append(row, Segment{Text: spinner + " ", Style: "\x1b[96;1m"})
	row = append(row, Segment{Text: strings.Repeat(fillChar, filled), Style: "\x1b[92;1m"})
	row = append(row, Segment{Text: strings.Repeat(emptyChar, empty), Style: "\x1b[90m"})
	row = append(row, Segment{Text: " " + pctStr, Style: "\x1b[97;1m"})

	return [][]Segment{row}
}

// RollingLogStream maintains a ring buffer of log lines.
type RollingLogStream struct {
	mu       sync.Mutex
	MaxLines int
	Lines    []string
}

func NewRollingLogStream(maxLines int) *RollingLogStream {
	if maxLines <= 0 {
		maxLines = 100
	}
	return &RollingLogStream{MaxLines: maxLines, Lines: make([]string, 0, maxLines)}
}

func (s *RollingLogStream) Append(line string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.Lines = append(s.Lines, line)
	if len(s.Lines) > s.MaxLines {
		s.Lines = s.Lines[len(s.Lines)-s.MaxLines:]
	}
}

func (s *RollingLogStream) Measure(ctx RenderContext) Size {
	s.mu.Lock()
	defer s.mu.Unlock()
	return Size{Width: ctx.Bounds.Width, Height: len(s.Lines)}
}

func (s *RollingLogStream) Render(bounds Size, ctx RenderContext) [][]Segment {
	s.mu.Lock()
	defer s.mu.Unlock()

	if bounds.Width <= 0 || bounds.Height <= 0 {
		return [][]Segment{}
	}

	start := len(s.Lines) - bounds.Height
	if start < 0 {
		start = 0
	}
	visible := s.Lines[start:]

	result := make([][]Segment, 0, len(visible))
	for _, line := range visible {
		txt := line
		if !ctx.ColorMode {
			txt = visualMeter.StripANSI(line)
		}
		tLen := visualMeter.Measure(txt)
		if tLen > bounds.Width {
			runes := []rune(visualMeter.StripANSI(txt))
			if len(runes) > bounds.Width {
				runes = runes[:bounds.Width]
			}
			txt = string(runes)
		}
		result = append(result, []Segment{{Text: txt}})
	}

	return result
}

// Column defines column layout properties for LiveTable.
type Column struct {
	Header   string
	MinWidth int
	MaxWidth int
	Flex     int
	Align    string
}

type TableRow struct {
	ID    string
	Cells []interface{}
}

// LiveTable displays a real-time reactive grid.
type LiveTable struct {
	mu      sync.Mutex
	Columns []Column
	Rows    []TableRow
}

func NewLiveTable(columns []Column) *LiveTable {
	return &LiveTable{Columns: columns, Rows: []TableRow{}}
}

func (t *LiveTable) AddRow(id string, cells []interface{}) {
	t.mu.Lock()
	defer t.mu.Unlock()
	t.Rows = append(t.Rows, TableRow{ID: id, Cells: cells})
}

func (t *LiveTable) UpdateCell(id string, colIdx int, val interface{}) {
	t.mu.Lock()
	defer t.mu.Unlock()
	for i := range t.Rows {
		if t.Rows[i].ID == id {
			if colIdx >= 0 && colIdx < len(t.Rows[i].Cells) {
				t.Rows[i].Cells[colIdx] = val
			}
			break
		}
	}
}

func (t *LiveTable) UpdateRow(id string, cells []interface{}) {
	t.mu.Lock()
	defer t.mu.Unlock()
	for i := range t.Rows {
		if t.Rows[i].ID == id {
			t.Rows[i].Cells = cells
			break
		}
	}
}

func (t *LiveTable) Measure(ctx RenderContext) Size {
	t.mu.Lock()
	defer t.mu.Unlock()
	return Size{Width: ctx.Bounds.Width, Height: len(t.Rows) + 2}
}

func (t *LiveTable) Render(bounds Size, ctx RenderContext) [][]Segment {
	t.mu.Lock()
	defer t.mu.Unlock()

	if bounds.Width <= 0 || bounds.Height <= 0 || len(t.Columns) == 0 {
		return [][]Segment{}
	}

	numCols := len(t.Columns)
	colWidths := make([]int, numCols)
	remaining := bounds.Width - (numCols - 1) // accounts for spaces between columns

	for i, col := range t.Columns {
		minW := col.MinWidth
		if minW <= 0 {
			minW = visualMeter.Measure(col.Header)
		}
		colWidths[i] = minW
		remaining -= minW
	}

	flexSum := 0
	for _, col := range t.Columns {
		if col.Flex > 0 {
			flexSum += col.Flex
		}
	}

	if flexSum > 0 && remaining > 0 {
		flexUnit := float64(remaining) / float64(flexSum)
		for i, col := range t.Columns {
			if col.Flex > 0 {
				alloc := int(float64(col.Flex) * flexUnit)
				colWidths[i] += alloc
				remaining -= alloc
			}
		}
		if remaining > 0 {
			colWidths[0] += remaining
		}
	}

	lines := [][]Segment{}

	// Header Row
	headerRow := []Segment{}
	for i, col := range t.Columns {
		w := colWidths[i]
		tObj := NewText(col.Header, "\x1b[96;1m", col.Align)
		subCtx := RenderContext{Bounds: Size{Width: w, Height: 1}, ColorMode: ctx.ColorMode, AsciiMode: ctx.AsciiMode}
		tSegs := tObj.Render(Size{Width: w, Height: 1}, subCtx)
		if len(tSegs) > 0 {
			headerRow = append(headerRow, tSegs[0]...)
		}
		if i < numCols-1 {
			headerRow = append(headerRow, Segment{Text: " "})
		}
	}
	lines = append(lines, headerRow)

	// Separator Row
	sepChar := "─"
	if !ctx.ColorMode || ctx.AsciiMode {
		sepChar = "-"
	}
	sepRow := []Segment{}
	for i, w := range colWidths {
		sepRow = append(sepRow, Segment{Text: strings.Repeat(sepChar, w), Style: "\x1b[90m"})
		if i < numCols-1 {
			sepRow = append(sepRow, Segment{Text: " "})
		}
	}
	lines = append(lines, sepRow)

	// Data Rows
	for _, row := range t.Rows {
		rowSegs := []Segment{}
		for i, col := range t.Columns {
			w := colWidths[i]
			var val interface{}
			if i < len(row.Cells) {
				val = row.Cells[i]
			}

			subCtx := RenderContext{Bounds: Size{Width: w, Height: 1}, ColorMode: ctx.ColorMode, AsciiMode: ctx.AsciiMode}
			if rend, ok := val.(Renderable); ok {
				rendered := rend.Render(Size{Width: w, Height: 1}, subCtx)
				if len(rendered) > 0 {
					rowSegs = append(rowSegs, rendered[0]...)
					lineLen := 0
					for _, s := range rendered[0] {
						lineLen += visualMeter.Measure(s.Text)
					}
					pad := w - lineLen
					if pad > 0 {
						rowSegs = append(rowSegs, Segment{Text: strings.Repeat(" ", pad)})
					}
				} else {
					rowSegs = append(rowSegs, Segment{Text: strings.Repeat(" ", w)})
				}
			} else {
				strVal := fmt.Sprintf("%v", val)
				tObj := NewText(strVal, "", col.Align)
				rendered := tObj.Render(Size{Width: w, Height: 1}, subCtx)
				if len(rendered) > 0 {
					rowSegs = append(rowSegs, rendered[0]...)
				}
			}

			if i < numCols-1 {
				rowSegs = append(rowSegs, Segment{Text: " "})
			}
		}
		lines = append(lines, rowSegs)
	}

	return lines
}

// --- Engine ---

// Canvas represents a 2D text buffer for clipping and coordinate blitting.
type Canvas struct {
	Size Size
	Grid [][][2]string // [y][x] -> [char, style]
}

func NewCanvas(size Size) *Canvas {
	grid := make([][][2]string, size.Height)
	for y := 0; y < size.Height; y++ {
		row := make([][2]string, size.Width)
		for x := 0; x < size.Width; x++ {
			row[x] = [2]string{" ", ""}
		}
		grid[y] = row
	}
	return &Canvas{Size: size, Grid: grid}
}

func (c *Canvas) Clear() {
	for y := 0; y < c.Size.Height; y++ {
		for x := 0; x < c.Size.Width; x++ {
			c.Grid[y][x] = [2]string{" ", ""}
		}
	}
}

func (c *Canvas) Blit(startX, startY int, segments []Segment) {
	if startY < 0 || startY >= c.Size.Height {
		return
	}

	currX := startX
	for _, seg := range segments {
		clean := visualMeter.StripANSI(seg.Text)
		for _, ch := range clean {
			if currX >= 0 && currX < c.Size.Width {
				c.Grid[startY][currX] = [2]string{string(ch), seg.Style}
			}
			currX++
			if currX >= c.Size.Width {
				break
			}
		}
		if currX >= c.Size.Width {
			break
		}
	}
}

func (c *Canvas) RenderToStrings() []string {
	res := make([]string, c.Size.Height)
	for y := 0; y < c.Size.Height; y++ {
		var sb strings.Builder
		currentStyle := ""
		for x := 0; x < c.Size.Width; x++ {
			cell := c.Grid[y][x]
			char := cell[0]
			style := cell[1]

			if style != currentStyle {
				if currentStyle != "" {
					sb.WriteString("\x1b[0m")
				}
				if style != "" {
					sb.WriteString(style)
				}
				currentStyle = style
			}
			sb.WriteString(char)
		}
		if currentStyle != "" {
			sb.WriteString("\x1b[0m")
		}
		res[y] = sb.String()
	}
	return res
}

// Engine Modes
const (
	ModeInline          = "inline"
	ModeAlternateScreen = "alternate_screen"
)

// LiveEngine orchestrates terminal rendering loops.
type LiveEngine struct {
	Renderable    Renderable
	Mode          string
	RefreshRateHz float64
	ColorMode     bool
	AsciiMode     bool

	mu            sync.Mutex
	running       bool
	stopChan      chan struct{}
	canvas        *Canvas
	renderedLines int
}

func NewLiveEngine(renderable Renderable, mode string, refreshRateHz float64) *LiveEngine {
	if mode == "" {
		mode = ModeInline
	}
	if refreshRateHz <= 0 {
		refreshRateHz = 10.0
	}
	return &LiveEngine{
		Renderable:    renderable,
		Mode:          mode,
		RefreshRateHz: refreshRateHz,
		ColorMode:     GetColorMode(),
		AsciiMode:     GetAsciiMode(),
	}
}

func (e *LiveEngine) Start() {
	e.mu.Lock()
	if e.running {
		e.mu.Unlock()
		return
	}
	e.running = true
	e.stopChan = make(chan struct{})
	e.ColorMode = GetColorMode()
	e.AsciiMode = GetAsciiMode()
	e.mu.Unlock()

	if e.ColorMode {
		os.Stdout.WriteString("\x1b[?25l") // Hide cursor
	}
	if e.Mode == ModeAlternateScreen && e.ColorMode {
		os.Stdout.WriteString("\x1b[?1049h") // Alternate buffer
	}

	if !e.ColorMode {
		e.Refresh()
	}

	// Signals
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		select {
		case <-sigChan:
			e.Stop()
			os.Exit(0)
		case <-e.stopChan:
			return
		}
	}()

	interval := time.Duration(float64(time.Second) / e.RefreshRateHz)
	if !e.ColorMode {
		interval = 5 * time.Second
	}

	go func() {
		ticker := time.NewTicker(interval)
		defer ticker.Stop()
		for {
			select {
			case <-ticker.C:
				e.Refresh()
			case <-e.stopChan:
				return
			}
		}
	}()
}

func (e *LiveEngine) Stop() {
	e.mu.Lock()
	if !e.running {
		e.mu.Unlock()
		return
	}
	e.running = false
	close(e.stopChan)
	e.mu.Unlock()

	if e.ColorMode {
		if e.Mode == ModeAlternateScreen {
			os.Stdout.WriteString("\x1b[?1049l") // Exit alternate buffer
		}
		os.Stdout.WriteString("\x1b[?25h") // Show cursor
	}

	if !e.ColorMode {
		e.Refresh()
	}
}

func (e *LiveEngine) Refresh() {
	e.mu.Lock()
	defer e.mu.Unlock()

	size := terminalMetrics.GetSize()
	if e.Mode == ModeInline {
		ctx := RenderContext{Bounds: size, ColorMode: e.ColorMode, AsciiMode: e.AsciiMode}
		measured := e.Renderable.Measure(ctx)
		height := measured.Height
		if height > size.Height-1 {
			height = size.Height - 1
		}
		size = Size{Width: size.Width, Height: height}
	}

	if e.canvas == nil || e.canvas.Size != size {
		e.canvas = NewCanvas(size)
	}

	e.canvas.Clear()

	ctx := RenderContext{Bounds: size, ColorMode: e.ColorMode, AsciiMode: e.AsciiMode}
	lines := e.Renderable.Render(size, ctx)

	for y, l := range lines {
		if y >= size.Height {
			break
		}
		e.canvas.Blit(0, y, l)
	}

	renderedStrings := e.canvas.RenderToStrings()

	if e.ColorMode {
		if e.Mode == ModeInline && e.renderedLines > 0 {
			os.Stdout.WriteString(fmt.Sprintf("\x1b[%dA", e.renderedLines))
		}

		for _, rStr := range renderedStrings {
			os.Stdout.WriteString("\x1b[2K" + rStr + "\n")
		}
		e.renderedLines = len(renderedStrings)
	} else {
		fmt.Printf("\n--- Live Snapshot ---\n")
		for _, rStr := range renderedStrings {
			fmt.Println(rStr)
		}
		fmt.Printf("---------------------\n\n")
	}
}
