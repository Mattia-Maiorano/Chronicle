using System;
using System.Text;

namespace Chronicle
{
    public static class ChronicleLogger
    {
        private static readonly object _lock = new object();
        private static bool _colorMode = true;

        public static void SetColorMode(bool enabled = true)
        {
            lock (_lock)
            {
                _colorMode = enabled;
            }
        }

        public static bool GetColorMode()
        {
            lock (_lock)
            {
                return _colorMode;
            }
        }

        public static void SetColorlessMode(bool enabled = true) => SetColorMode(!enabled);
        public static void SetAsciiMode(bool enabled = true) => SetColorlessMode(enabled);
        public static bool GetAsciiMode() => !GetColorMode();

        public static class Colors
        {
            // Text colors
            public const string BLACK = "\u001b[30m";
            public const string RED = "\u001b[31m";
            public const string GREEN = "\u001b[32m";
            public const string YELLOW = "\u001b[33m";
            public const string BLUE = "\u001b[34m";
            public const string MAGENTA = "\u001b[35m";
            public const string CYAN = "\u001b[36m";
            public const string WHITE = "\u001b[37m";

            // Bright text colors
            public const string BRIGHT_BLACK = "\u001b[90m";
            public const string BRIGHT_RED = "\u001b[91m";
            public const string BRIGHT_GREEN = "\u001b[92m";
            public const string BRIGHT_YELLOW = "\u001b[93m";
            public const string BRIGHT_BLUE = "\u001b[94m";
            public const string BRIGHT_MAGENTA = "\u001b[95m";
            public const string BRIGHT_CYAN = "\u001b[96m";
            public const string BRIGHT_WHITE = "\u001b[97m";

            // Background colors
            public const string BG_BLACK = "\u001b[40m";
            public const string BG_RED = "\u001b[41m";
            public const string BG_GREEN = "\u001b[42m";
            public const string BG_YELLOW = "\u001b[43m";
            public const string BG_BLUE = "\u001b[44m";
            public const string BG_MAGENTA = "\u001b[45m";
            public const string BG_CYAN = "\u001b[46m";
            public const string BG_WHITE = "\u001b[47m";

            // Styles
            public const string BOLD = "\u001b[1m";
            public const string DIM = "\u001b[2m";
            public const string ITALIC = "\u001b[3m";
            public const string UNDERLINE = "\u001b[4m";
            public const string BLINK = "\u001b[5m";
            public const string REVERSE = "\u001b[7m";

            // Reset
            public const string RESET = "\u001b[0m";

            // Semantic colors
            public static string ERROR => RED;
            public static string WARNING => YELLOW;
            public static string SUCCESS => GREEN;
            public static string INFO => CYAN;
            public static string DEBUG => BRIGHT_MAGENTA;
            public static string HEADER => BRIGHT_CYAN;
            public static string EMPHASIS => BRIGHT_YELLOW;
        }

        private static void WriteOutput(string message)
        {
#if UNITY_ENGINE || UNITY_5_3_OR_NEWER
            UnityEngine.Debug.Log(message);
#else
            Console.Write(message);
#endif
        }

        public static void Log(
            int indentationTabs = 0,
            int newlineBefore = 0,
            int newlineAfter = 0,
            string? color = null,
            string content = "",
            bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();

            if (newlineBefore > 0)
            {
                WriteOutput(new string('\n', newlineBefore - 1));
            }

            string indentation = new string('\t', indentationTabs);
            string message = (color != null && useColor)
                ? $"{indentation}{color}{content}{Colors.RESET}"
                : $"{indentation}{content}";

            WriteOutput(message);

            if (newlineAfter > 0)
            {
                WriteOutput(new string('\n', newlineAfter));
            }
            else
            {
                WriteOutput("\n");
            }
        }

        public static void LogNewline(int count = 1)
        {
            if (count > 1)
            {
                WriteOutput(new string('\n', count - 1));
            }
            WriteOutput("\n");
        }

        public static void LogApplicationTitle(string title, int width = 60, bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();
            int titleLength = title.Length;
            if (titleLength + 2 > width - 2)
            {
                width = titleLength + 4;
            }

            int padding = (width - 2 - titleLength) / 2;
            string paddedTitle = new string(' ', padding) + title + new string(' ', width - 2 - titleLength - padding);

            string topBorder, middleLine, bottomBorder;
            string? color;

            if (useColor)
            {
                topBorder = "╔" + new string('═', width - 2) + "╗";
                middleLine = "║" + paddedTitle + "║";
                bottomBorder = "╚" + new string('═', width - 2) + "╝";
                color = Colors.BRIGHT_MAGENTA + Colors.BOLD;
            }
            else
            {
                topBorder = "+" + new string('-', width - 2) + "+";
                middleLine = "|" + paddedTitle + "|";
                bottomBorder = "+" + new string('-', width - 2) + "+";
                color = null;
            }

            LogNewline(2);
            Log(0, 1, 0, color, topBorder, useColor);
            Log(0, 0, 0, color, middleLine, useColor);
            Log(0, 0, 1, color, bottomBorder, useColor);
            LogNewline(2);
        }

        public static void LogSectionHeader(string title, int indentationTabs = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();
            string? color = useColor ? Colors.HEADER + Colors.BOLD : null;
            string separator = new string('=', 60);

            Log(indentationTabs, 1, 0, color, separator, useColor);
            Log(indentationTabs, 0, 0, color, title, useColor);
            Log(indentationTabs, 0, 1, color, separator, useColor);
            LogNewline();
        }

        public static void LogSubsection(string title, int indentationTabs = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();
            string? color = useColor ? Colors.BRIGHT_CYAN : null;
            string separator = new string('-', 40);

            Log(indentationTabs, 1, 0, color, separator, useColor);
            Log(indentationTabs, 0, 0, color, title, useColor);
            Log(indentationTabs, 0, 0, color, separator, useColor);
            LogNewline();
        }

        public static void LogError(string message, int indentationTabs = 0, int newlineBefore = 0, int newlineAfter = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();
            string prefix = useColor ? "ERROR:" : "[ERROR]";
            string? color = useColor ? Colors.ERROR + Colors.BOLD : null;
            Log(indentationTabs, newlineBefore, newlineAfter, color, $"{prefix} {message}", useColor);
        }

        public static void LogWarning(string message, int indentationTabs = 0, int newlineBefore = 0, int newlineAfter = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();
            string prefix = useColor ? "WARNING:" : "[WARNING]";
            string? color = useColor ? Colors.WARNING + Colors.BOLD : null;
            Log(indentationTabs, newlineBefore, newlineAfter, color, $"{prefix} {message}", useColor);
        }

        public static void LogSuccess(string message, int indentationTabs = 0, int newlineBefore = 0, int newlineAfter = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();
            string prefix = useColor ? "SUCCESS:" : "[OK]";
            string? color = useColor ? Colors.SUCCESS + Colors.BOLD : null;
            Log(indentationTabs, newlineBefore, newlineAfter, color, $"{prefix} {message}", useColor);
        }

        public static void LogInfo(string message, int indentationTabs = 0, int newlineBefore = 0, int newlineAfter = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();
            string prefix = useColor ? "INFO:" : "[INFO]";
            string? color = useColor ? Colors.INFO : null;
            Log(indentationTabs, newlineBefore, newlineAfter, color, $"{prefix} {message}", useColor);
        }

        public static void LogDebug(string message, int indentationTabs = 2, int newlineBefore = 0, int newlineAfter = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();
            string prefix = useColor ? "DEBUG:" : "[DEBUG]";
            string? color = useColor ? Colors.DEBUG + Colors.BOLD : null;
            Log(indentationTabs, newlineBefore, newlineAfter, color, $"{prefix} {message}", useColor);
        }

        public static void LogStep(int stepNumber, int totalSteps, string description, int indentationTabs = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();
            string? color = useColor ? Colors.BRIGHT_BLUE + Colors.BOLD : null;
            LogNewline();
            Log(indentationTabs, 1, 0, color, $"[Step {stepNumber}/{totalSteps}] {description}", useColor);
            LogNewline();
        }

        public static void LogFileSaved(string filepath, int indentationTabs = 1, bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();
            string prefix = "Saved:";
            string? color = useColor ? Colors.SUCCESS : null;
            Log(indentationTabs, 0, 0, color, $"{prefix} {filepath}", useColor);
        }

        public static void LogFinalResult(bool success, string message, int width = 60, bool? colorMode = null)
        {
            bool useColor = colorMode ?? GetColorMode();
            string? color = useColor ? (success ? Colors.SUCCESS + Colors.BOLD : Colors.ERROR + Colors.BOLD) : null;
            string separator = new string('=', width);

            LogNewline(2);
            Log(0, 1, 0, color, separator, useColor);
            if (success)
            {
                LogSuccess(message, 0, 0, 1, useColor);
            }
            else
            {
                LogError(message, 0, 0, 1, useColor);
            }
            Log(0, 0, 1, color, separator, useColor);
            LogNewline(2);
        }
    }

    public static class StructuredLogger
    {
        public static void LogBanner(string title, int width = 54, bool? colorMode = null)
        {
            bool useColor = colorMode ?? ChronicleLogger.GetColorMode();
            int minWidth = title.Length + 6;
            if (width < minWidth)
            {
                width = minWidth;
            }

            string lineDashes = new string('-', width - 2);
            string rawPadded = $"| [{title.ToUpper()}]";
            string padded = rawPadded.PadRight(width - 1);

            if (useColor)
            {
                string c = ChronicleLogger.Colors.HEADER + ChronicleLogger.Colors.BOLD;
                string r = ChronicleLogger.Colors.RESET;
                string top = $"{c}+{lineDashes}+{r}";
                string mid = $"{c}{padded}|{r}";
                string bot = $"{c}+{lineDashes}+{r}";
                Console.Write($"\n{top}\n{mid}\n{bot}\n\n");
            }
            else
            {
                string top = $"+{lineDashes}+";
                string mid = $"{padded}|";
                string bot = $"+{lineDashes}+";
                Console.Write($"\n{top}\n{mid}\n{bot}\n\n");
            }
        }

        public static void LogSection(string category, int indentLevel = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? ChronicleLogger.GetColorMode();
            string indent = new string(' ', indentLevel * 2);
            string catStr = category.EndsWith(":") ? category : $"{category}:";

            if (useColor)
            {
                string cTree = ChronicleLogger.Colors.BRIGHT_CYAN;
                string cCat = ChronicleLogger.Colors.BRIGHT_CYAN + ChronicleLogger.Colors.BOLD;
                string r = ChronicleLogger.Colors.RESET;
                Console.Write($"\n{indent}  {cTree}|--{r} {cCat}{catStr}{r}\n");
            }
            else
            {
                Console.Write($"\n{indent}  |-- {catStr}\n");
            }
        }

        public static void LogDetail(object label, object? value, int indentLevel = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? ChronicleLogger.GetColorMode();
            string indent = new string(' ', (indentLevel + 1) * 2);
            string formattedLabel = label.ToString()?.PadRight(22) ?? "".PadRight(22);

            if (useColor)
            {
                string cTree = ChronicleLogger.Colors.BRIGHT_CYAN;
                string cLabel = ChronicleLogger.Colors.CYAN + ChronicleLogger.Colors.BOLD;
                string cVal = ChronicleLogger.Colors.BRIGHT_WHITE + ChronicleLogger.Colors.BOLD;
                string r = ChronicleLogger.Colors.RESET;
                Console.Write($"{indent}{cTree}+--{r} {cLabel}{formattedLabel}{r} : {cVal}{value}{r}\n");
            }
            else
            {
                Console.Write($"{indent}+-- {formattedLabel} : {value}\n");
            }
        }

        public static void LogDecision(string action, string? detail = null, int indentLevel = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? ChronicleLogger.GetColorMode();
            string indent = new string(' ', indentLevel * 2);

            if (useColor)
            {
                string cArrow = ChronicleLogger.Colors.BRIGHT_YELLOW + ChronicleLogger.Colors.BOLD;
                string cAction = ChronicleLogger.Colors.BRIGHT_GREEN + ChronicleLogger.Colors.BOLD;
                string cDetail = ChronicleLogger.Colors.BRIGHT_WHITE;
                string r = ChronicleLogger.Colors.RESET;

                if (!string.IsNullOrWhiteSpace(detail))
                {
                    Console.Write($"\n{indent}  {cArrow}+--> DECISION:{r} {cAction}{action}{r} -> {cDetail}{detail}{r}\n\n");
                }
                else
                {
                    Console.Write($"\n{indent}  {cArrow}+--> DECISION:{r} {cAction}{action}{r}\n\n");
                }
            }
            else
            {
                if (!string.IsNullOrWhiteSpace(detail))
                {
                    Console.Write($"\n{indent}  +--> DECISION: {action} -> {detail}\n\n");
                }
                else
                {
                    Console.Write($"\n{indent}  +--> DECISION: {action}\n\n");
                }
            }
        }

        public static void LogMessage(string message, int indentLevel = 0, bool? colorMode = null)
        {
            bool useColor = colorMode ?? ChronicleLogger.GetColorMode();
            string indent = new string(' ', indentLevel * 2);

            if (useColor)
            {
                string cTree = ChronicleLogger.Colors.BRIGHT_CYAN;
                string cMsg = ChronicleLogger.Colors.BRIGHT_WHITE;
                string r = ChronicleLogger.Colors.RESET;
                Console.Write($"{indent}{cTree}|--{r} {cMsg}{message}{r}\n");
            }
            else
            {
                Console.Write($"{indent}|-- {message}\n");
            }
        }
        
        // Table logging
        public static void LogTable(List<List<string>> rows, List<string>? headers = null, List<string>? alignments = null, bool? colorMode = null)
        {
            bool useColor = colorMode ?? ChronicleLogger.GetColorMode();
            int colCount = Math.Max(headers?.Count ?? 0, rows.Any() ? rows.Max(r => r.Count) : 0);
            if (colCount == 0) return;

            var colWidths = new int[colCount];
            foreach (var r in rows)
            {
                for (int i = 0; i < r.Count; i++)
                {
                    colWidths[i] = Math.Max(colWidths[i], r[i].Length);
                }
            }
            if (headers != null)
            {
                for (int i = 0; i < headers.Count; i++)
                {
                    colWidths[i] = Math.Max(colWidths[i], headers[i].Length);
                }
            }

            var aligns = alignments?.Take(colCount).ToArray() ?? Enumerable.Repeat("<", colCount).ToArray();

            var chars = useColor
                ? new Dictionary<string, string> { { "tl", "┌" }, { "tm", "┬" }, { "tr", "┐" }, { "ml", "├" }, { "mm", "┼" }, { "mr", "┤" }, { "bl", "└" }, { "bm", "┴" }, { "br", "┘" }, { "h", "─" }, { "v", "│" }, { "color", ChronicleLogger.Colors.BRIGHT_CYAN } }
                : new Dictionary<string, string> { { "tl", "+" }, { "tm", "+" }, { "tr", "+" }, { "ml", "+" }, { "mm", "+" }, { "mr", "+" }, { "bl", "+" }, { "bm", "+" }, { "br", "+" }, { "h", "-" }, { "v", "|" }, { "color", null } };

            string MakeLine(string left, string sep, string right)
            {
                var line = left;
                for (int i = 0; i < colWidths.Length; i++)
                {
                    line += new string(chars["h"][0], colWidths[i] + 2);
                    line += i < colWidths.Length - 1 ? sep : right;
                }
                return line;
            }

            var top = MakeLine(chars["tl"], chars["tm"], chars["tr"]);
            var middle = MakeLine(chars["ml"], chars["mm"], chars["mr"]);
            var bottom = MakeLine(chars["bl"], chars["bm"], chars["br"]);

            string FormatRow(List<string> cells)
            {
                var parts = new List<string>();
                for (int i = 0; i < colCount; i++)
                {
                    var cell = i < cells.Count ? cells[i] : "";
                    var width = colWidths[i];
                    var align = aligns[i];
                    if (align == ">")
                        parts.Add($" {cell.PadLeft(width)} ");
                    else
                        parts.Add($" {cell.PadRight(width)} ");
                }
                return chars["v"] + string.Join(chars["v"], parts) + chars["v"];
            }

            var lines = new List<string> { top };
            if (headers != null)
            {
                lines.Add(FormatRow(headers));
                lines.Add(middle);
            }
            foreach (var r in rows)
            {
                var padded = new List<string>(r);
                if (padded.Count < colCount) padded.AddRange(Enumerable.Repeat("", colCount - padded.Count));
                lines.Add(FormatRow(padded));
            }
            lines.Add(bottom);

            foreach (var line in lines)
            {
                if (chars["color"] != null && useColor)
                    Console.Write($"{chars["color"]}{line}{ChronicleLogger.Colors.RESET}\n");
                else
                    Console.Write($"{line}\n");
            }
        }

        // Snake_case aliases
        public static void log_banner(string title, int width = 54, bool? colorMode = null) => LogBanner(title, width, colorMode);
        public static void log_section(string category, int indentLevel = 0, bool? colorMode = null) => LogSection(category, indentLevel, colorMode);
        public static void log_detail(object label, object? value, int indentLevel = 0, bool? colorMode = null) => LogDetail(label, value, indentLevel, colorMode);
        public static void log_decision(string action, string? detail = null, int indentLevel = 0, bool? colorMode = null) => LogDecision(action, detail, indentLevel, colorMode);
        public static void log_message(string message, int indentLevel = 0, bool? colorMode = null) => LogMessage(message, indentLevel, colorMode);
        public static void log_table(List<List<string>> rows, List<string>? headers = null, List<string>? alignments = null, bool? colorMode = null) => LogTable(rows, headers, alignments, colorMode);
    }
}
