package chronicle

private var _colorMode: Boolean = true

fun setColorMode(enabled: Boolean = true) {
    _colorMode = enabled
}

fun getColorMode(): Boolean = _colorMode

fun setColorlessMode(enabled: Boolean = true) {
    _colorMode = !enabled
}

fun setAsciiMode(enabled: Boolean = true) {
    setColorlessMode(enabled)
}

fun getAsciiMode(): Boolean = !_colorMode

object Colors {
    // Text colors
    const val BLACK = "\u001B[30m"
    const val RED = "\u001B[31m"
    const val GREEN = "\u001B[32m"
    const val YELLOW = "\u001B[33m"
    const val BLUE = "\u001B[34m"
    const val MAGENTA = "\u001B[35m"
    const val CYAN = "\u001B[36m"
    const val WHITE = "\u001B[37m"

    // Bright text colors
    const val BRIGHT_BLACK = "\u001B[90m"
    const val BRIGHT_RED = "\u001B[91m"
    const val BRIGHT_GREEN = "\u001B[92m"
    const val BRIGHT_YELLOW = "\u001B[93m"
    const val BRIGHT_BLUE = "\u001B[94m"
    const val BRIGHT_MAGENTA = "\u001B[95m"
    const val BRIGHT_CYAN = "\u001B[96m"
    const val BRIGHT_WHITE = "\u001B[97m"

    // Background colors
    const val BG_BLACK = "\u001B[40m"
    const val BG_RED = "\u001B[41m"
    const val BG_GREEN = "\u001B[42m"
    const val BG_YELLOW = "\u001B[43m"
    const val BG_BLUE = "\u001B[44m"
    const val BG_MAGENTA = "\u001B[45m"
    const val BG_CYAN = "\u001B[46m"
    const val BG_WHITE = "\u001B[47m"

    // Styles
    const val BOLD = "\u001B[1m"
    const val DIM = "\u001B[2m"
    const val ITALIC = "\u001B[3m"
    const val UNDERLINE = "\u001B[4m"
    const val BLINK = "\u001B[5m"
    const val REVERSE = "\u001B[7m"

    // Reset
    const val RESET = "\u001B[0m"

    // Semantic colors
    val ERROR get() = RED
    val WARNING get() = YELLOW
    val SUCCESS get() = GREEN
    val INFO get() = CYAN
    val DEBUG get() = BRIGHT_MAGENTA
    val HEADER get() = BRIGHT_CYAN
    val EMPHASIS get() = BRIGHT_YELLOW
}

fun log(
    indentationTabs: Int = 0,
    newlineBefore: Int = 0,
    newlineAfter: Int = 0,
    color: String? = null,
    content: String = "",
    colorMode: Boolean? = null
) {
    val useColor = colorMode ?: _colorMode

    if (newlineBefore > 0) {
        print("\n".repeat(newlineBefore - 1))
    }

    val indentation = "\t".repeat(indentationTabs)
    val message = if (color != null && useColor) {
        "$indentation$color$content${Colors.RESET}"
    } else {
        "$indentation$content"
    }

    print(message)

    if (newlineAfter > 0) {
        print("\n".repeat(newlineAfter))
    } else {
        println()
    }
}

fun logNewline(count: Int = 1) {
    if (count > 1) {
        print("\n".repeat(count - 1))
    }
    println()
}

fun logApplicationTitle(title: String, width: Int = 60, colorMode: Boolean? = null) {
    val useColor = colorMode ?: _colorMode
    var calcWidth = width
    val titleLength = title.length
    if (titleLength + 2 > calcWidth - 2) {
        calcWidth = titleLength + 4
    }

    val padding = (calcWidth - 2 - titleLength) / 2
    val paddedTitle = " ".repeat(padding) + title + " ".repeat(calcWidth - 2 - titleLength - padding)

    val topBorder: String
    val middleLine: String
    val bottomBorder: String
    val color: String?

    if (useColor) {
        topBorder = "╔" + "═".repeat(calcWidth - 2) + "╗"
        middleLine = "║" + paddedTitle + "║"
        bottomBorder = "╚" + "═".repeat(calcWidth - 2) + "╝"
        color = Colors.BRIGHT_MAGENTA + Colors.BOLD
    } else {
        topBorder = "+" + "-".repeat(calcWidth - 2) + "+"
        middleLine = "|" + paddedTitle + "|"
        bottomBorder = "+" + "-".repeat(calcWidth - 2) + "+"
        color = null
    }

    logNewline(2)
    log(0, 1, 0, color, topBorder, useColor)
    log(0, 0, 0, color, middleLine, useColor)
    log(0, 0, 1, color, bottomBorder, useColor)
    logNewline(2)
}

fun logSectionHeader(title: String, indentationTabs: Int = 0, colorMode: Boolean? = null) {
    val useColor = colorMode ?: _colorMode
    val color = if (useColor) Colors.HEADER + Colors.BOLD else null
    val separator = "=".repeat(60)

    log(indentationTabs, 1, 0, color, separator, useColor)
    log(indentationTabs, 0, 0, color, title, useColor)
    log(indentationTabs, 0, 1, color, separator, useColor)
    logNewline()
}

fun logSubsection(title: String, indentationTabs: Int = 0, colorMode: Boolean? = null) {
    val useColor = colorMode ?: _colorMode
    val color = if (useColor) Colors.BRIGHT_CYAN else null
    val separator = "-".repeat(40)

    log(indentationTabs, 1, 0, color, separator, useColor)
    log(indentationTabs, 0, 0, color, title, useColor)
    log(indentationTabs, 0, 0, color, separator, useColor)
    logNewline()
}

fun logError(
    message: String,
    indentationTabs: Int = 0,
    newlineBefore: Int = 0,
    newlineAfter: Int = 0,
    colorMode: Boolean? = null
) {
    val useColor = colorMode ?: _colorMode
    val prefix = if (useColor) "ERROR:" else "[ERROR]"
    val color = if (useColor) Colors.ERROR + Colors.BOLD else null
    log(indentationTabs, newlineBefore, newlineAfter, color, "$prefix $message", useColor)
}

fun logWarning(
    message: String,
    indentationTabs: Int = 0,
    newlineBefore: Int = 0,
    newlineAfter: Int = 0,
    colorMode: Boolean? = null
) {
    val useColor = colorMode ?: _colorMode
    val prefix = if (useColor) "WARNING:" else "[WARNING]"
    val color = if (useColor) Colors.WARNING + Colors.BOLD else null
    log(indentationTabs, newlineBefore, newlineAfter, color, "$prefix $message", useColor)
}

fun logSuccess(
    message: String,
    indentationTabs: Int = 0,
    newlineBefore: Int = 0,
    newlineAfter: Int = 0,
    colorMode: Boolean? = null
) {
    val useColor = colorMode ?: _colorMode
    val prefix = if (useColor) "SUCCESS:" else "[OK]"
    val color = if (useColor) Colors.SUCCESS + Colors.BOLD else null
    log(indentationTabs, newlineBefore, newlineAfter, color, "$prefix $message", useColor)
}

fun logInfo(
    message: String,
    indentationTabs: Int = 0,
    newlineBefore: Int = 0,
    newlineAfter: Int = 0,
    colorMode: Boolean? = null
) {
    val useColor = colorMode ?: _colorMode
    val prefix = if (useColor) "INFO:" else "[INFO]"
    val color = if (useColor) Colors.INFO else null
    log(indentationTabs, newlineBefore, newlineAfter, color, "$prefix $message", useColor)
}

fun logDebug(
    message: String,
    indentationTabs: Int = 2,
    newlineBefore: Int = 0,
    newlineAfter: Int = 0,
    colorMode: Boolean? = null
) {
    val useColor = colorMode ?: _colorMode
    val prefix = if (useColor) "DEBUG:" else "[DEBUG]"
    val color = if (useColor) Colors.DEBUG + Colors.BOLD else null
    log(indentationTabs, newlineBefore, newlineAfter, color, "$prefix $message", useColor)
}

fun logStep(
    stepNumber: Int,
    totalSteps: Int,
    description: String,
    indentationTabs: Int = 0,
    colorMode: Boolean? = null
) {
    val useColor = colorMode ?: _colorMode
    val color = if (useColor) Colors.BRIGHT_BLUE + Colors.BOLD else null
    logNewline()
    log(indentationTabs, 1, 0, color, "[Step $stepNumber/$totalSteps] $description", useColor)
    logNewline()
}

fun logFileSaved(
    filepath: String,
    indentationTabs: Int = 1,
    colorMode: Boolean? = null
) {
    val useColor = colorMode ?: _colorMode
    val prefix = "Saved:"
    val color = if (useColor) Colors.SUCCESS else null
    log(indentationTabs, 0, 0, color, "$prefix $filepath", useColor)
}

fun logFinalResult(
    success: Boolean,
    message: String,
    width: Int = 60,
    colorMode: Boolean? = null
) {
    val useColor = colorMode ?: _colorMode
    val color = if (useColor) {
        if (success) Colors.SUCCESS + Colors.BOLD else Colors.ERROR + Colors.BOLD
    } else null
    val separator = "=".repeat(width)

    logNewline(2)
    log(0, 1, 0, color, separator, useColor)
    if (success) {
        logSuccess(message, 0, 0, 1, useColor)
    } else {
        logError(message, 0, 0, 1, useColor)
    }
    log(0, 0, 1, color, separator, useColor)
    logNewline(2)
}

// Tree Structured Logger

fun logBanner(title: String, width: Int = 54, colorMode: Boolean? = null) {
    val useColor = colorMode ?: _colorMode
    var calcWidth = width
    val minWidth = title.length + 6
    if (calcWidth < minWidth) {
        calcWidth = minWidth
    }

    val lineDashes = "-".repeat(calcWidth - 2)
    val rawPadded = "| [${title.uppercase()}]"
    val padded = rawPadded.padEnd(calcWidth - 1)

    if (useColor) {
        val c = Colors.HEADER + Colors.BOLD
        val r = Colors.RESET
        val top = "$c+$lineDashes+$r"
        val mid = "$c$padded|$r"
        val bot = "$c+$lineDashes+$r"
        println("\n$top\n$mid\n$bot\n")
    } else {
        val top = "+$lineDashes+"
        val mid = "$padded|"
        val bot = "+$lineDashes+"
        println("\n$top\n$mid\n$bot\n")
    }
}

fun logSection(category: String, indentLevel: Int = 0, colorMode: Boolean? = null) {
    val useColor = colorMode ?: _colorMode
    val indent = "  ".repeat(indentLevel)
    val catStr = if (category.endsWith(":")) category else "$category:"

    if (useColor) {
        val cTree = Colors.BRIGHT_CYAN
        val cCat = Colors.BRIGHT_CYAN + Colors.BOLD
        val r = Colors.RESET
        println("\n$indent  $cTree|--$r $cCat$catStr$r")
    } else {
        println("\n$indent  |-- $catStr")
    }
}

fun logDetail(label: Any, value: Any?, indentLevel: Int = 0, colorMode: Boolean? = null) {
    val useColor = colorMode ?: _colorMode
    val indent = "  ".repeat(indentLevel + 1)
    val formattedLabel = label.toString().padEnd(22)

    if (useColor) {
        val cTree = Colors.BRIGHT_CYAN
        val cLabel = Colors.CYAN + Colors.BOLD
        val cVal = Colors.BRIGHT_WHITE + Colors.BOLD
        val r = Colors.RESET
        println("$indent$cTree+--$r $cLabel$formattedLabel$r : $cVal$value$r")
    } else {
        println("$indent+-- $formattedLabel : $value")
    }
}

fun logDecision(action: String, detail: String? = null, indentLevel: Int = 0, colorMode: Boolean? = null) {
    val useColor = colorMode ?: _colorMode
    val indent = "  ".repeat(indentLevel)

    if (useColor) {
        val cArrow = Colors.BRIGHT_YELLOW + Colors.BOLD
        val cAction = Colors.BRIGHT_GREEN + Colors.BOLD
        val cDetail = Colors.BRIGHT_WHITE
        val r = Colors.RESET

        if (!detail.isNullOrBlank()) {
            println("\n$indent  $cArrow+--> DECISION:$r $cAction$action$r -> $cDetail$detail$r\n")
        } else {
            println("\n$indent  $cArrow+--> DECISION:$r $cAction$action$r\n")
        }
    } else {
        if (!detail.isNullOrBlank()) {
            println("\n$indent  +--> DECISION: $action -> $detail\n")
        } else {
            println("\n$indent  +--> DECISION: $action\n")
        }
    }
}

fun logMessage(message: String, indentLevel: Int = 0, colorMode: Boolean? = null) {
    val useColor = colorMode ?: _colorMode
    val indent = "  ".repeat(indentLevel)

    if (useColor) {
        val cTree = Colors.BRIGHT_CYAN
        val cMsg = Colors.BRIGHT_WHITE
        val r = Colors.RESET
        println("$indent$cTree|--$r $cMsg$message$r")
    } else {
        println("$indent|-- $message")
    }
}

object StructuredLogger {
    fun logBanner(title: String, width: Int = 54, colorMode: Boolean? = null) =
        chronicle.logBanner(title, width, colorMode)

    fun logSection(category: String, indentLevel: Int = 0, colorMode: Boolean? = null) =
        chronicle.logSection(category, indentLevel, colorMode)

    fun logDetail(label: Any, value: Any?, indentLevel: Int = 0, colorMode: Boolean? = null) =
        chronicle.logDetail(label, value, indentLevel, colorMode)

    fun logDecision(action: String, detail: String? = null, indentLevel: Int = 0, colorMode: Boolean? = null) =
        chronicle.logDecision(action, detail, indentLevel, colorMode)

    fun logMessage(message: String, indentLevel: Int = 0, colorMode: Boolean? = null) =
        chronicle.logMessage(message, indentLevel, colorMode)

    // Snake_case aliases
    fun log_banner(title: String, width: Int = 54, colorMode: Boolean? = null) =
        logBanner(title, width, colorMode)

    fun log_section(category: String, indentLevel: Int = 0, colorMode: Boolean? = null) =
        logSection(category, indentLevel, colorMode)

    fun log_detail(label: Any, value: Any?, indentLevel: Int = 0, colorMode: Boolean? = null) =
        logDetail(label, value, indentLevel, colorMode)

    fun log_decision(action: String, detail: String? = null, indentLevel: Int = 0, colorMode: Boolean? = null) =
        logDecision(action, detail, indentLevel, colorMode)

    fun log_message(message: String, indentLevel: Int = 0, colorMode: Boolean? = null) =
        logMessage(message, indentLevel, colorMode)
}

typealias AsciiLogger = StructuredLogger
typealias KeeperLogger = StructuredLogger
