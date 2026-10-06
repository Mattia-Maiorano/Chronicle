package chronicle

import java.util.Timer
import java.util.TimerTask
import java.util.regex.Pattern
import kotlin.math.max
import kotlin.math.min

// --- Geometry ---

data class Size(val width: Int, val height: Int)
data class Point(val x: Int, val y: Int)
data class Segment(val text: String, val style: String? = null)

object VisualMeter {
    private val ansiPattern = Pattern.compile("\\x1b\\[[0-9;]*[a-zA-Z]")

    fun stripAnsi(text: String): String {
        if (text.isEmpty()) return ""
        return ansiPattern.matcher(text).replaceAll("")
    }

    fun measure(text: String): Int {
        if (text.isEmpty()) return 0
        return stripAnsi(text).length
    }
}

object TerminalMetrics {
    fun getSize(): Size {
        // Fallback for terminal dimension
        return Size(80, 24)
    }
}

// --- Layout Base ---

data class RenderContext(
    val bounds: Size,
    val colorMode: Boolean = true,
    val asciiMode: Boolean = false
)

interface Renderable {
    fun measure(ctx: RenderContext): Size
    fun render(bounds: Size, ctx: RenderContext): List<List<Segment>>
}

// --- Layout Policies ---

sealed interface Policy
data class Fixed(val size: Int) : Policy
data class Flex(val weight: Int = 1) : Policy
data class Ratio(val percentage: Double) : Policy

// --- Layout Primitives ---

class Text(
    val text: String,
    val style: String? = null,
    val align: String = LEFT,
    val truncateStr: String = "..."
) : Renderable {
    companion object {
        const val LEFT = "left"
        const val CENTER = "center"
        const val RIGHT = "right"
    }

    override fun measure(ctx: RenderContext): Size =
        Size(VisualMeter.measure(text), 1)

    override fun render(bounds: Size, ctx: RenderContext): List<List<Segment>> {
        if (bounds.width <= 0 || bounds.height <= 0) return emptyList()

        var textLen = VisualMeter.measure(text)
        var displayText = text

        if (textLen > bounds.width) {
            if (bounds.width >= truncateStr.length) {
                val clean = VisualMeter.stripAnsi(text)
                val allowed = (bounds.width - truncateStr.length).coerceIn(0, clean.length)
                displayText = clean.substring(0, allowed) + truncateStr
                textLen = bounds.width
            } else {
                displayText = ""
                textLen = 0
            }
        }

        val padTotal = max(0, bounds.width - textLen)
        val padLeft: Int
        val padRight: Int
        when (align) {
            CENTER -> {
                padLeft = padTotal / 2
                padRight = padTotal - padLeft
            }
            RIGHT -> {
                padLeft = padTotal
                padRight = 0
            }
            else -> {
                padLeft = 0
                padRight = padTotal
            }
        }

        val row = mutableListOf<Segment>()
        if (padLeft > 0) row.add(Segment(" ".repeat(padLeft)))
        row.add(Segment(displayText, if (ctx.colorMode) style else null))
        if (padRight > 0) row.add(Segment(" ".repeat(padRight)))

        return listOf(row)
    }
}

class Rule(
    val title: String? = null,
    val style: String? = null,
    val character: String = "─"
) : Renderable {
    override fun measure(ctx: RenderContext): Size =
        Size(ctx.bounds.width, 1)

    override fun render(bounds: Size, ctx: RenderContext): List<List<Segment>> {
        if (bounds.width <= 0 || bounds.height <= 0) return emptyList()

        val ch = if (ctx.colorMode && !ctx.asciiMode) character else "-"
        val s = if (ctx.colorMode) style else null

        if (title.isNullOrEmpty()) {
            return listOf(listOf(Segment(ch.repeat(bounds.width), s)))
        }

        val titleText = " $title "
        val titleLen = VisualMeter.measure(titleText)
        if (titleLen >= bounds.width) {
            return listOf(listOf(Segment(titleText.substring(0, min(titleText.length, bounds.width)), s)))
        }

        val leftDash = (bounds.width - titleLen) / 2
        val rightDash = bounds.width - titleLen - leftDash

        val row = mutableListOf<Segment>()
        if (leftDash > 0) row.add(Segment(ch.repeat(leftDash), s))
        row.add(Segment(titleText, s))
        if (rightDash > 0) row.add(Segment(ch.repeat(rightDash), s))

        return listOf(row)
    }
}

data class BorderGlyphs(val tl: String, val tr: String, val bl: String, val br: String, val h: String, val v: String)

class Panel(
    val child: Renderable,
    val title: String? = null,
    val subtitle: String? = null,
    val borderStyle: String = ROUNDED,
    val padding: Int = 1,
    val borderColor: String? = null
) : Renderable {
    companion object {
        const val ROUNDED = "rounded"
        const val SQUARE = "square"
        const val DOUBLE = "double"
        const val CHRONICLE_TREE = "chronicle_tree"

        val styles = mapOf(
            ROUNDED to BorderGlyphs("╭", "╮", "╰", "╯", "─", "│"),
            SQUARE to BorderGlyphs("┌", "┐", "└", "┘", "─", "│"),
            DOUBLE to BorderGlyphs("╔", "╗", "╚", "╝", "═", "║"),
            CHRONICLE_TREE to BorderGlyphs("+", "+", "+", "+", "-", "|")
        )
    }

    override fun measure(ctx: RenderContext): Size {
        val innerCtx = RenderContext(
            Size(max(0, ctx.bounds.width - 2 - (padding * 2)), max(0, ctx.bounds.height - 2)),
            ctx.colorMode, ctx.asciiMode
        )
        val childSize = child.measure(innerCtx)
        return Size(childSize.width + 2 + (padding * 2), childSize.height + 2)
    }

    override fun render(bounds: Size, ctx: RenderContext): List<List<Segment>> {
        if (bounds.width < 2 || bounds.height < 2) return emptyList()

        var glyphs = styles[borderStyle] ?: styles[CHRONICLE_TREE]!!
        if (!ctx.colorMode || ctx.asciiMode) {
            glyphs = styles[CHRONICLE_TREE]!!
        }

        val bStyle = if (ctx.colorMode) borderColor else null
        val lines = ArrayList<List<Segment>>(bounds.height)
        val innerW = bounds.width - 2

        // Top Border
        val topRow = mutableListOf(Segment(glyphs.tl, bStyle))
        if (!title.isNullOrEmpty()) {
            val tText = " $title "
            val tLen = VisualMeter.measure(tText)
            if (tLen >= innerW) {
                topRow.add(Segment(tText.substring(0, min(tText.length, innerW)), bStyle))
            } else {
                topRow.add(Segment(glyphs.h, bStyle))
                topRow.add(Segment(tText, bStyle))
                val rem = innerW - 1 - tLen
                if (rem > 0) topRow.add(Segment(glyphs.h.repeat(rem), bStyle))
            }
        } else {
            topRow.add(Segment(glyphs.h.repeat(innerW), bStyle))
        }
        topRow.add(Segment(glyphs.tr, bStyle))
        lines.add(topRow)

        // Inner Content
        val innerH = bounds.height - 2
        val childW = max(0, innerW - (padding * 2))
        val innerBounds = Size(childW, innerH)
        val childLines = child.render(innerBounds, ctx)

        for (y in 0 until innerH) {
            val row = mutableListOf(Segment(glyphs.v, bStyle))
            if (padding > 0) row.add(Segment(" ".repeat(padding)))

            if (y < childLines.size) {
                row.addAll(childLines[y])
                var lineLen = 0
                for (s in childLines[y]) lineLen += VisualMeter.measure(s.text)
                val pad = childW - lineLen
                if (pad > 0) row.add(Segment(" ".repeat(pad)))
            } else {
                row.add(Segment(" ".repeat(childW)))
            }

            if (padding > 0) row.add(Segment(" ".repeat(padding)))
            row.add(Segment(glyphs.v, bStyle))
            lines.add(row)
        }

        // Bottom Border
        val botRow = mutableListOf(Segment(glyphs.bl, bStyle))
        if (!subtitle.isNullOrEmpty()) {
            val sText = " $subtitle "
            val sLen = VisualMeter.measure(sText)
            if (sLen >= innerW) {
                botRow.add(Segment(sText.substring(0, min(sText.length, innerW)), bStyle))
            } else {
                botRow.add(Segment(glyphs.h, bStyle))
                botRow.add(Segment(sText, bStyle))
                val rem = innerW - 1 - sLen
                if (rem > 0) botRow.add(Segment(glyphs.h.repeat(rem), bStyle))
            }
        } else {
            botRow.add(Segment(glyphs.h.repeat(innerW), bStyle))
        }
        botRow.add(Segment(glyphs.br, bStyle))
        lines.add(botRow)

        return lines
    }
}

open class FlexSplitter(val direction: String = HORIZONTAL) : Renderable {
    companion object {
        const val HORIZONTAL = "horizontal"
        const val VERTICAL = "vertical"
    }

    data class ChildItem(val child: Renderable, val policy: Policy)

    val children = mutableListOf<ChildItem>()

    fun add(child: Renderable, policy: Policy = Flex(1)) {
        children.add(ChildItem(child, policy))
    }

    override fun measure(ctx: RenderContext): Size = ctx.bounds

    override fun render(bounds: Size, ctx: RenderContext): List<List<Segment>> {
        if (children.isEmpty()) return emptyList()

        val totalSize = if (direction == HORIZONTAL) bounds.width else bounds.height
        val sizes = IntArray(children.size) { 0 }
        var remaining = totalSize

        // 1. Fixed & Ratio
        for (i in children.indices) {
            when (val pol = children[i].policy) {
                is Fixed -> {
                    sizes[i] = pol.size
                    remaining -= pol.size
                }
                is Ratio -> {
                    val alloc = (totalSize * pol.percentage).toInt()
                    sizes[i] = alloc
                    remaining -= alloc
                }
                is Flex -> {}
            }
        }

        // 2. Flex
        var flexSum = 0
        for (item in children) {
            if (item.policy is Flex) flexSum += item.policy.weight
        }

        if (flexSum > 0 && remaining > 0) {
            val flexUnit = remaining.toDouble() / flexSum
            var remFlex = remaining
            for (i in children.indices) {
                if (children[i].policy is Flex) {
                    val alloc = ((children[i].policy as Flex).weight * flexUnit).toInt()
                    sizes[i] = alloc
                    remFlex -= alloc
                }
            }
            if (remFlex > 0) {
                for (i in children.indices) {
                    if (children[i].policy is Flex) {
                        sizes[i] += remFlex
                        break
                    }
                }
            }
        }

        val renderedChildren = children.mapIndexed { i, item ->
            val cBounds = if (direction == HORIZONTAL) Size(sizes[i], bounds.height) else Size(bounds.width, sizes[i])
            val cCtx = RenderContext(cBounds, ctx.colorMode, ctx.asciiMode)
            Pair(cBounds, item.child.render(cBounds, cCtx))
        }

        val lines = mutableListOf<List<Segment>>()
        if (direction == HORIZONTAL) {
            for (y in 0 until bounds.height) {
                val row = mutableListOf<Segment>()
                for ((cBounds, cLines) in renderedChildren) {
                    if (y < cLines.size) {
                        row.addAll(cLines[y])
                        var cLen = 0
                        for (s in cLines[y]) cLen += VisualMeter.measure(s.text)
                        val pad = cBounds.width - cLen
                        if (pad > 0) row.add(Segment(" ".repeat(pad)))
                    } else {
                        row.add(Segment(" ".repeat(cBounds.width)))
                    }
                }
                lines.add(row)
            }
        } else {
            for ((cBounds, cLines) in renderedChildren) {
                for (y in 0 until cBounds.height) {
                    if (y < cLines.size) {
                        lines.add(cLines[y])
                    } else {
                        lines.add(listOf(Segment(" ".repeat(bounds.width))))
                    }
                }
            }
        }

        return lines
    }
}

class Layout(direction: String = FlexSplitter.HORIZONTAL) : FlexSplitter(direction)

// --- Components ---

class Badge(
    val text: String,
    val badgeType: String = INFO,
    val customStyle: String? = null
) : Renderable {
    companion object {
        const val PASS = "PASS"
        const val SUCCESS = "SUCCESS"
        const val FAIL = "FAIL"
        const val ERROR = "ERROR"
        const val WARN = "WARN"
        const val WARNING = "WARNING"
        const val INFO = "INFO"
        const val RUNNING = "RUNNING"
    }

    override fun measure(ctx: RenderContext): Size = Size(text.length + 2, 1)

    override fun render(bounds: Size, ctx: RenderContext): List<List<Segment>> {
        if (bounds.width <= 0 || bounds.height <= 0) return emptyList()

        if (!ctx.colorMode) {
            return listOf(listOf(Segment("[$text]")))
        }

        val style = customStyle ?: when (badgeType.uppercase()) {
            PASS, SUCCESS -> "\u001B[42;30;1m"
            FAIL, ERROR -> "\u001B[41;97;1m"
            WARN, WARNING -> "\u001B[43;30;1m"
            RUNNING -> "\u001B[44;97;1m"
            else -> "\u001B[46;30;1m"
        }

        return listOf(listOf(Segment(" $text ", style)))
    }
}

class ProgressBar(
    var total: Int = 100,
    var completed: Int = 0,
    val label: String? = null
) : Renderable {
    private val lock = Any()
    private val spinnerChars = listOf("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    private var spinnerIdx = 0

    init {
        if (total <= 0) total = 100
    }

    fun update(newCompleted: Int) = synchronized(lock) {
        completed = newCompleted.coerceIn(0, total)
        spinnerIdx = (spinnerIdx + 1) % spinnerChars.size
    }

    override fun measure(ctx: RenderContext): Size = Size(ctx.bounds.width, 1)

    override fun render(bounds: Size, ctx: RenderContext): List<List<Segment>> = synchronized(lock) {
        if (bounds.width <= 0 || bounds.height <= 0) return emptyList()

        val pct = (completed.toDouble() / total).coerceIn(0.0, 1.0)
        val pctStr = "${String.format("%3.0f", pct * 100)}%"
        val spinner = if (ctx.colorMode && !ctx.asciiMode) spinnerChars[spinnerIdx] else "*"

        val labelStr = if (!label.isNullOrEmpty()) "$label " else ""
        val fixedWidth = VisualMeter.measure(labelStr) + 1 + 1 + pctStr.length + 1
        val barWidth = max(5, bounds.width - fixedWidth)

        val filled = (barWidth * pct).toInt()
        val empty = max(0, barWidth - filled)

        val fillChar = if (ctx.colorMode && !ctx.asciiMode) "━" else "="
        val emptyChar = if (ctx.colorMode && !ctx.asciiMode) "╌" else "-"

        val row = mutableListOf<Segment>()
        if (labelStr.isNotEmpty()) row.add(Segment(labelStr, "\u001B[97m"))
        row.add(Segment("$spinner ", "\u001B[96;1m"))
        row.add(Segment(fillChar.repeat(filled), "\u001B[92;1m"))
        row.add(Segment(emptyChar.repeat(empty), "\u001B[90m"))
        row.add(Segment(" $pctStr", "\u001B[97;1m"))

        listOf(row)
    }
}

class RollingLogStream(val maxLines: Int = 100) : Renderable {
    private val lock = Any()
    val lines = mutableListOf<String>()

    fun append(line: String) = synchronized(lock) {
        lines.add(line)
        if (lines.size > maxLines) {
            lines.removeAt(0)
        }
    }

    override fun measure(ctx: RenderContext): Size = synchronized(lock) {
        Size(ctx.bounds.width, lines.size)
    }

    override fun render(bounds: Size, ctx: RenderContext): List<List<Segment>> = synchronized(lock) {
        if (bounds.width <= 0 || bounds.height <= 0) return emptyList()

        val start = max(0, lines.size - bounds.height)
        val visible = lines.subList(start, lines.size)

        val result = mutableListOf<List<Segment>>()
        for (line in visible) {
            var txt = if (ctx.colorMode) line else VisualMeter.stripAnsi(line)
            if (VisualMeter.measure(txt) > bounds.width) {
                val clean = VisualMeter.stripAnsi(txt)
                txt = clean.substring(0, min(clean.length, bounds.width))
            }
            result.add(listOf(Segment(txt)))
        }
        result
    }
}

data class Column(
    val header: String,
    val minWidth: Int = 10,
    val maxWidth: Int? = null,
    val flex: Int = 1,
    val align: String = "left"
)

class LiveTable(val columns: List<Column>) : Renderable {
    private val lock = Any()
    val rows = mutableListOf<Pair<String, MutableList<Any?>>>()

    fun addRow(id: String, cells: List<Any?>) = synchronized(lock) {
        rows.add(Pair(id, cells.toMutableList()))
    }

    fun updateCell(id: String, colIdx: Int, value: Any?) = synchronized(lock) {
        for (row in rows) {
            if (row.first == id) {
                if (colIdx in 0 until row.second.size) {
                    row.second[colIdx] = value
                }
                break
            }
        }
    }

    fun updateRow(id: String, cells: List<Any?>) = synchronized(lock) {
        for (i in rows.indices) {
            if (rows[i].first == id) {
                rows[i] = Pair(id, cells.toMutableList())
                break
            }
        }
    }

    override fun measure(ctx: RenderContext): Size = synchronized(lock) {
        Size(ctx.bounds.width, rows.size + 2)
    }

    override fun render(bounds: Size, ctx: RenderContext): List<List<Segment>> = synchronized(lock) {
        if (bounds.width <= 0 || bounds.height <= 0 || columns.isEmpty()) return emptyList()

        val numCols = columns.size
        val colWidths = IntArray(numCols) { 0 }
        var remaining = bounds.width - (numCols - 1)

        for (i in 0 until numCols) {
            val minW = if (columns[i].minWidth > 0) columns[i].minWidth else VisualMeter.measure(columns[i].header)
            colWidths[i] = minW
            remaining -= minW
        }

        var flexSum = 0
        for (col in columns) {
            if (col.flex > 0) flexSum += col.flex
        }

        if (flexSum > 0 && remaining > 0) {
            val flexUnit = remaining.toDouble() / flexSum
            for (i in 0 until numCols) {
                if (columns[i].flex > 0) {
                    val alloc = (columns[i].flex * flexUnit).toInt()
                    colWidths[i] += alloc
                    remaining -= alloc
                }
            }
            if (remaining > 0) colWidths[0] += remaining
        }

        val lines = mutableListOf<List<Segment>>()

        // Header Row
        val headerRow = mutableListOf<Segment>()
        for (i in 0 until numCols) {
            val w = colWidths[i]
            val tObj = Text(columns[i].header, style = "\u001B[96;1m", align = columns[i].align)
            val subCtx = RenderContext(Size(w, 1), ctx.colorMode, ctx.asciiMode)
            val tSegs = tObj.render(Size(w, 1), subCtx)
            if (tSegs.isNotEmpty()) headerRow.addAll(tSegs[0])
            if (i < numCols - 1) headerRow.add(Segment(" "))
        }
        lines.add(headerRow)

        // Separator Row
        val sepChar = if (ctx.colorMode && !ctx.asciiMode) "─" else "-"
        val sepRow = mutableListOf<Segment>()
        for (i in 0 until numCols) {
            sepRow.add(Segment(sepChar.repeat(colWidths[i]), "\u001B[90m"))
            if (i < numCols - 1) sepRow.add(Segment(" "))
        }
        lines.add(sepRow)

        // Data Rows
        for (row in rows) {
            val rowSegs = mutableListOf<Segment>()
            for (i in 0 until numCols) {
                val w = colWidths[i]
                val value = if (i < row.second.size) row.second[i] else null
                val subCtx = RenderContext(Size(w, 1), ctx.colorMode, ctx.asciiMode)

                if (value is Renderable) {
                    val rendered = value.render(Size(w, 1), subCtx)
                    if (rendered.isNotEmpty()) {
                        rowSegs.addAll(rendered[0])
                        var lineLen = 0
                        for (s in rendered[0]) lineLen += VisualMeter.measure(s.text)
                        val pad = w - lineLen
                        if (pad > 0) rowSegs.add(Segment(" ".repeat(pad)))
                    } else {
                        rowSegs.add(Segment(" ".repeat(w)))
                    }
                } else {
                    val strVal = value?.toString() ?: ""
                    val tObj = Text(strVal, align = columns[i].align)
                    val rendered = tObj.render(Size(w, 1), subCtx)
                    if (rendered.isNotEmpty()) rowSegs.addAll(rendered[0])
                }

                if (i < numCols - 1) rowSegs.add(Segment(" "))
            }
            lines.add(rowSegs)
        }

        lines
    }
}

// --- Engine ---

class Canvas(val size: Size) {
    private val grid = Array(size.height) { Array(size.width) { Pair(' ', null as String?) } }

    fun clear() {
        for (y in 0 until size.height) {
            for (x in 0 until size.width) {
                grid[y][x] = Pair(' ', null)
            }
        }
    }

    fun blit(startX: Int, startY: Int, segments: List<Segment>) {
        if (startY < 0 || startY >= size.height) return

        var currX = startX
        for (seg in segments) {
            val clean = VisualMeter.stripAnsi(seg.text)
            for (ch in clean) {
                if (currX in 0 until size.width) {
                    grid[startY][currX] = Pair(ch, seg.style)
                }
                currX++
                if (currX >= size.width) break
            }
            if (currX >= size.width) break
        }
    }

    fun renderToStrings(): List<String> {
        val res = ArrayList<String>(size.height)
        for (y in 0 until size.height) {
            val sb = StringBuilder()
            var currentStyle: String? = null
            for (x in 0 until size.width) {
                val (ch, style) = grid[y][x]
                if (style != currentStyle) {
                    if (currentStyle != null) sb.append("\u001B[0m")
                    if (style != null) sb.append(style)
                    currentStyle = style
                }
                sb.append(ch)
            }
            if (currentStyle != null) sb.append("\u001B[0m")
            res.add(sb.toString())
        }
        return res
    }
}

class LiveEngine(
    val renderable: Renderable,
    val mode: String = INLINE,
    val refreshRateHz: Double = 10.0
) {
    companion object {
        const val INLINE = "inline"
        const val ALTERNATE_SCREEN = "alternate_screen"
    }

    var colorMode: Boolean = getColorMode()
    var asciiMode: Boolean = getAsciiMode()

    private val lock = Any()
    private var running = false
    private var timer: Timer? = null
    private var canvas: Canvas? = null
    private var renderedLines = 0

    fun start() = synchronized(lock) {
        if (running) return
        running = true

        colorMode = getColorMode()
        asciiMode = getAsciiMode()

        if (colorMode) {
            print("\u001B[?25l") // Hide cursor
        }
        if (mode == ALTERNATE_SCREEN && colorMode) {
            print("\u001B[?1049h")
        }

        if (!colorMode) {
            refresh()
        }

        Runtime.getRuntime().addShutdownHook(Thread {
            stop()
        })

        val intervalMs = if (colorMode) (1000.0 / refreshRateHz).toLong() else 5000L
        timer = Timer(true).apply {
            scheduleAtFixedRate(object : TimerTask() {
                override fun run() {
                    refresh()
                }
            }, intervalMs, intervalMs)
        }
    }

    fun stop() = synchronized(lock) {
        if (!running) return
        running = false

        timer?.cancel()
        timer = null

        if (colorMode) {
            if (mode == ALTERNATE_SCREEN) {
                print("\u001B[?1049l")
            }
            print("\u001B[?25h") // Show cursor
        }

        if (!colorMode) {
            refresh()
        }
        System.out.flush()
    }

    fun refresh() = synchronized(lock) {
        var size = TerminalMetrics.getSize()
        if (mode == INLINE) {
            val ctx = RenderContext(size, colorMode, asciiMode)
            val measured = renderable.measure(ctx)
            val h = min(measured.height, size.height - 1)
            size = Size(size.width, h)
        }

        if (canvas == null || canvas?.size != size) {
            canvas = Canvas(size)
        }

        canvas?.clear()

        val rCtx = RenderContext(size, colorMode, asciiMode)
        val lines = renderable.render(size, rCtx)

        for (y in lines.indices) {
            if (y >= size.height) break
            canvas?.blit(0, y, lines[y])
        }

        val renderedStrings = canvas?.renderToStrings() ?: emptyList()

        if (colorMode) {
            if (mode == INLINE && renderedLines > 0) {
                print("\u001B[${renderedLines}A")
            }

            for (rStr in renderedStrings) {
                print("\u001B[2K$rStr\n")
            }
            renderedLines = renderedStrings.size
        } else {
            println("\n--- Live Snapshot ---")
            for (rStr in renderedStrings) {
                println(rStr)
            }
            println("---------------------\n")
        }
        System.out.flush()
    }
}
