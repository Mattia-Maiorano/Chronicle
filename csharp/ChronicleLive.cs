using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;

namespace Chronicle
{
    // --- Geometry ---

    public class Size
    {
        public int Width { get; set; }
        public int Height { get; set; }

        public Size(int width, int height)
        {
            Width = width;
            Height = height;
        }

        public override bool Equals(object? obj) =>
            obj is Size other && Width == other.Width && Height == other.Height;

        public override int GetHashCode() => HashCode.Combine(Width, Height);
    }

    public class Point
    {
        public int X { get; set; }
        public int Y { get; set; }

        public Point(int x, int y)
        {
            X = x;
            Y = y;
        }
    }

    public class Segment
    {
        public string Text { get; set; }
        public string? Style { get; set; }

        public Segment(string text, string? style = null)
        {
            Text = text;
            Style = style;
        }
    }

    public static class VisualMeter
    {
        private static readonly Regex AnsiRegex = new Regex(@"\x1b\[[0-9;]*[a-zA-Z]", RegexOptions.Compiled);

        public static string StripAnsi(string text)
        {
            if (string.IsNullOrEmpty(text)) return string.Empty;
            return AnsiRegex.Replace(text, string.Empty);
        }

        public static int Measure(string text)
        {
            if (string.IsNullOrEmpty(text)) return 0;
            return StripAnsi(text).Length;
        }
    }

    public static class TerminalMetrics
    {
        public static Size GetSize()
        {
            try
            {
                if (Console.WindowWidth > 0 && Console.WindowHeight > 0)
                {
                    return new Size(Console.WindowWidth, Console.WindowHeight);
                }
            }
            catch
            {
                // Fallback for non-interactive environments
            }
            return new Size(80, 24);
        }
    }

    // --- Layout Base ---

    public class RenderContext
    {
        public Size Bounds { get; set; }
        public bool ColorMode { get; set; }
        public bool AsciiMode { get; set; }

        public RenderContext(Size bounds, bool colorMode = true, bool asciiMode = false)
        {
            Bounds = bounds;
            ColorMode = colorMode;
            AsciiMode = asciiMode;
        }
    }

    public interface IRenderable
    {
        Size Measure(RenderContext ctx);
        List<List<Segment>> Render(Size bounds, RenderContext ctx);
    }

    // --- Layout Policies ---

    public interface IPolicy { }

    public class Fixed : IPolicy
    {
        public int Size { get; }
        public Fixed(int size) => Size = size;
    }

    public class Flex : IPolicy
    {
        public int Weight { get; }
        public Flex(int weight = 1) => Weight = weight;
    }

    public class Ratio : IPolicy
    {
        public double Percentage { get; }
        public Ratio(double percentage) => Percentage = percentage;
    }

    // --- Layout Primitives ---

    public class Text : IRenderable
    {
        public const string LEFT = "left";
        public const string CENTER = "center";
        public const string RIGHT = "right";

        public string Content { get; set; }
        public string? Style { get; set; }
        public string Align { get; set; }
        public string TruncateStr { get; set; }

        public Text(string content, string? style = null, string align = LEFT, string truncateStr = "...")
        {
            Content = content;
            Style = style;
            Align = align;
            TruncateStr = truncateStr;
        }

        public Size Measure(RenderContext ctx) =>
            new Size(VisualMeter.Measure(Content), 1);

        public List<List<Segment>> Render(Size bounds, RenderContext ctx)
        {
            if (bounds.Width <= 0 || bounds.Height <= 0)
                return new List<List<Segment>>();

            int textLen = VisualMeter.Measure(Content);
            string displayText = Content;

            if (textLen > bounds.Width)
            {
                if (bounds.Width >= TruncateStr.Length)
                {
                    string clean = VisualMeter.StripAnsi(Content);
                    int allowed = bounds.Width - TruncateStr.Length;
                    if (allowed < 0) allowed = 0;
                    if (allowed > clean.Length) allowed = clean.Length;
                    displayText = clean.Substring(0, allowed) + TruncateStr;
                    textLen = bounds.Width;
                }
                else
                {
                    displayText = string.Empty;
                    textLen = 0;
                }
            }

            int padTotal = Math.Max(0, bounds.Width - textLen);
            int padLeft = 0, padRight = 0;

            if (Align == CENTER)
            {
                padLeft = padTotal / 2;
                padRight = padTotal - padLeft;
            }
            else if (Align == RIGHT)
            {
                padLeft = padTotal;
            }
            else
            {
                padRight = padTotal;
            }

            string? style = ctx.ColorMode ? Style : null;
            var row = new List<Segment>();
            if (padLeft > 0) row.Add(new Segment(new string(' ', padLeft)));
            row.Add(new Segment(displayText, style));
            if (padRight > 0) row.Add(new Segment(new string(' ', padRight)));

            return new List<List<Segment>> { row };
        }
    }

    public class Rule : IRenderable
    {
        public string? Title { get; set; }
        public string? Style { get; set; }
        public string Character { get; set; }

        public Rule(string? title = null, string? style = null, string character = "─")
        {
            Title = title;
            Style = style;
            Character = character;
        }

        public Size Measure(RenderContext ctx) =>
            new Size(ctx.Bounds.Width, 1);

        public List<List<Segment>> Render(Size bounds, RenderContext ctx)
        {
            if (bounds.Width <= 0 || bounds.Height <= 0)
                return new List<List<Segment>>();

            string ch = (ctx.ColorMode && !ctx.AsciiMode) ? Character : "-";
            string? style = ctx.ColorMode ? Style : null;

            if (string.IsNullOrEmpty(Title))
            {
                string line = new string(ch[0], bounds.Width);
                return new List<List<Segment>> { new List<Segment> { new Segment(line, style) } };
            }

            string titleText = $" {Title} ";
            int titleLen = VisualMeter.Measure(titleText);

            if (titleLen >= bounds.Width)
            {
                string line = titleText.Substring(0, Math.Min(titleText.Length, bounds.Width));
                return new List<List<Segment>> { new List<Segment> { new Segment(line, style) } };
            }

            int leftDash = (bounds.Width - titleLen) / 2;
            int rightDash = bounds.Width - titleLen - leftDash;

            var row = new List<Segment>();
            if (leftDash > 0) row.Add(new Segment(new string(ch[0], leftDash), style));
            row.Add(new Segment(titleText, style));
            if (rightDash > 0) row.Add(new Segment(new string(ch[0], rightDash), style));

            return new List<List<Segment>> { row };
        }
    }

    public class Panel : IRenderable
    {
        public const string ROUNDED = "rounded";
        public const string SQUARE = "square";
        public const string DOUBLE = "double";
        public const string CHRONICLE_TREE = "chronicle_tree";

        public class BorderGlyphs
        {
            public string TL { get; }
            public string TR { get; }
            public string BL { get; }
            public string BR { get; }
            public string H { get; }
            public string V { get; }

            public BorderGlyphs(string tl, string tr, string bl, string br, string h, string v)
            {
                TL = tl; TR = tr; BL = bl; BR = br; H = h; V = v;
            }
        }

        private static readonly Dictionary<string, BorderGlyphs> Styles = new Dictionary<string, BorderGlyphs>
        {
            [ROUNDED] = new BorderGlyphs("╭", "╮", "╰", "╯", "─", "│"),
            [SQUARE] = new BorderGlyphs("┌", "┐", "└", "┘", "─", "│"),
            [DOUBLE] = new BorderGlyphs("╔", "╗", "╚", "╝", "═", "║"),
            [CHRONICLE_TREE] = new BorderGlyphs("+", "+", "+", "+", "-", "|")
        };

        public IRenderable Child { get; set; }
        public string? Title { get; set; }
        public string? Subtitle { get; set; }
        public string BorderStyle { get; set; }
        public int Padding { get; set; }
        public string? BorderColor { get; set; }

        public Panel(IRenderable child, string? title = null, string? subtitle = null, string borderStyle = ROUNDED)
        {
            Child = child;
            Title = title;
            Subtitle = subtitle;
            BorderStyle = borderStyle;
            Padding = 1;
            BorderColor = null;
        }

        public Size Measure(RenderContext ctx)
        {
            var innerCtx = new RenderContext(
                new Size(Math.Max(0, ctx.Bounds.Width - 2 - (Padding * 2)), Math.Max(0, ctx.Bounds.Height - 2)),
                ctx.ColorMode, ctx.AsciiMode
            );
            var childSize = Child.Measure(innerCtx);
            return new Size(childSize.Width + 2 + (Padding * 2), childSize.Height + 2);
        }

        public List<List<Segment>> Render(Size bounds, RenderContext ctx)
        {
            if (bounds.Width < 2 || bounds.Height < 2)
                return new List<List<Segment>>();

            BorderGlyphs glyphs;
            if (!ctx.ColorMode || ctx.AsciiMode || !Styles.TryGetValue(BorderStyle, out glyphs!))
            {
                glyphs = Styles[CHRONICLE_TREE];
            }

            string? bStyle = ctx.ColorMode ? BorderColor : null;
            var lines = new List<List<Segment>>(bounds.Height);
            int innerW = bounds.Width - 2;

            // Top Border
            var topRow = new List<Segment> { new Segment(glyphs.TL, bStyle) };
            if (!string.IsNullOrEmpty(Title))
            {
                string tText = $" {Title} ";
                int tLen = VisualMeter.Measure(tText);
                if (tLen >= innerW)
                {
                    topRow.Add(new Segment(tText.Substring(0, Math.Min(tText.Length, innerW)), bStyle));
                }
                else
                {
                    topRow.Add(new Segment(glyphs.H, bStyle));
                    topRow.Add(new Segment(tText, bStyle));
                    int rem = innerW - 1 - tLen;
                    if (rem > 0) topRow.Add(new Segment(new string(glyphs.H[0], rem), bStyle));
                }
            }
            else
            {
                topRow.Add(new Segment(new string(glyphs.H[0], innerW), bStyle));
            }
            topRow.Add(new Segment(glyphs.TR, bStyle));
            lines.Add(topRow);

            // Inner Content
            int innerH = bounds.Height - 2;
            int childW = Math.Max(0, innerW - (Padding * 2));
            var innerBounds = new Size(childW, innerH);
            var childLines = Child.Render(innerBounds, ctx);

            for (int y = 0; y < innerH; y++)
            {
                var row = new List<Segment> { new Segment(glyphs.V, bStyle) };
                if (Padding > 0) row.Add(new Segment(new string(' ', Padding)));

                if (y < childLines.Count)
                {
                    row.AddRange(childLines[y]);
                    int lineLen = 0;
                    foreach (var s in childLines[y]) lineLen += VisualMeter.Measure(s.Text);
                    int pad = childW - lineLen;
                    if (pad > 0) row.Add(new Segment(new string(' ', pad)));
                }
                else
                {
                    row.Add(new Segment(new string(' ', childW)));
                }

                if (Padding > 0) row.Add(new Segment(new string(' ', Padding)));
                row.Add(new Segment(glyphs.V, bStyle));
                lines.Add(row);
            }

            // Bottom Border
            var botRow = new List<Segment> { new Segment(glyphs.BL, bStyle) };
            if (!string.IsNullOrEmpty(Subtitle))
            {
                string sText = $" {Subtitle} ";
                int sLen = VisualMeter.Measure(sText);
                if (sLen >= innerW)
                {
                    botRow.Add(new Segment(sText.Substring(0, Math.Min(sText.Length, innerW)), bStyle));
                }
                else
                {
                    botRow.Add(new Segment(glyphs.H, bStyle));
                    botRow.Add(new Segment(sText, bStyle));
                    int rem = innerW - 1 - sLen;
                    if (rem > 0) botRow.Add(new Segment(new string(glyphs.H[0], rem), bStyle));
                }
            }
            else
            {
                botRow.Add(new Segment(new string(glyphs.H[0], innerW), bStyle));
            }
            botRow.Add(new Segment(glyphs.BR, bStyle));
            lines.Add(botRow);

            return lines;
        }
    }

    public class FlexSplitter : IRenderable
    {
        public const string HORIZONTAL = "horizontal";
        public const string VERTICAL = "vertical";

        public class ChildItem
        {
            public IRenderable Child { get; }
            public IPolicy Policy { get; }
            public ChildItem(IRenderable child, IPolicy policy)
            {
                Child = child;
                Policy = policy;
            }
        }

        public string Direction { get; set; }
        public List<ChildItem> Children { get; } = new List<ChildItem>();

        public FlexSplitter(string direction = HORIZONTAL)
        {
            Direction = direction;
        }

        public void Add(IRenderable child, IPolicy? policy = null)
        {
            Children.Add(new ChildItem(child, policy ?? new Flex(1)));
        }

        public Size Measure(RenderContext ctx) => ctx.Bounds;

        public List<List<Segment>> Render(Size bounds, RenderContext ctx)
        {
            if (Children.Count == 0)
                return new List<List<Segment>>();

            int totalSize = Direction == HORIZONTAL ? bounds.Width : bounds.Height;
            int[] sizes = new int[Children.Count];
            int remaining = totalSize;

            // 1. Fixed & Ratio
            for (int i = 0; i < Children.Count; i++)
            {
                if (Children[i].Policy is Fixed fix)
                {
                    sizes[i] = fix.Size;
                    remaining -= fix.Size;
                }
                else if (Children[i].Policy is Ratio rat)
                {
                    int alloc = (int)(totalSize * rat.Percentage);
                    sizes[i] = alloc;
                    remaining -= alloc;
                }
            }

            // 2. Flex
            int flexSum = 0;
            foreach (var item in Children)
            {
                if (item.Policy is Flex flx) flexSum += flx.Weight;
            }

            if (flexSum > 0 && remaining > 0)
            {
                double flexUnit = (double)remaining / flexSum;
                int remFlex = remaining;
                for (int i = 0; i < Children.Count; i++)
                {
                    if (Children[i].Policy is Flex flx)
                    {
                        int alloc = (int)(flx.Weight * flexUnit);
                        sizes[i] = alloc;
                        remFlex -= alloc;
                    }
                }
                if (remFlex > 0)
                {
                    for (int i = 0; i < Children.Count; i++)
                    {
                        if (Children[i].Policy is Flex)
                        {
                            sizes[i] += remFlex;
                            break;
                        }
                    }
                }
            }

            var renderedChildren = new List<(Size cBounds, List<List<Segment>> cLines)>(Children.Count);
            for (int i = 0; i < Children.Count; i++)
            {
                var cBounds = Direction == HORIZONTAL
                    ? new Size(sizes[i], bounds.Height)
                    : new Size(bounds.Width, sizes[i]);
                var cCtx = new RenderContext(cBounds, ctx.ColorMode, ctx.AsciiMode);
                var cLines = Children[i].Child.Render(cBounds, cCtx);
                renderedChildren.Add((cBounds, cLines));
            }

            var lines = new List<List<Segment>>();
            if (Direction == HORIZONTAL)
            {
                for (int y = 0; y < bounds.Height; y++)
                {
                    var row = new List<Segment>();
                    foreach (var rc in renderedChildren)
                    {
                        if (y < rc.cLines.Count)
                        {
                            row.AddRange(rc.cLines[y]);
                            int cLen = 0;
                            foreach (var s in rc.cLines[y]) cLen += VisualMeter.Measure(s.Text);
                            int pad = rc.cBounds.Width - cLen;
                            if (pad > 0) row.Add(new Segment(new string(' ', pad)));
                        }
                        else
                        {
                            row.Add(new Segment(new string(' ', rc.cBounds.Width)));
                        }
                    }
                    lines.Add(row);
                }
            }
            else
            {
                foreach (var rc in renderedChildren)
                {
                    for (int y = 0; y < rc.cBounds.Height; y++)
                    {
                        if (y < rc.cLines.Count)
                        {
                            lines.Add(rc.cLines[y]);
                        }
                        else
                        {
                            lines.Add(new List<Segment> { new Segment(new string(' ', bounds.Width)) });
                        }
                    }
                }
            }

            return lines;
        }
    }

    public class Layout : FlexSplitter
    {
        public Layout(string direction = HORIZONTAL) : base(direction) { }
    }

    // --- Components ---

    public class Badge : IRenderable
    {
        public const string PASS = "PASS";
        public const string SUCCESS = "SUCCESS";
        public const string FAIL = "FAIL";
        public const string ERROR = "ERROR";
        public const string WARN = "WARN";
        public const string WARNING = "WARNING";
        public const string INFO = "INFO";
        public const string RUNNING = "RUNNING";

        public string Text { get; set; }
        public string BadgeType { get; set; }
        public string? CustomStyle { get; set; }

        public Badge(string text, string badgeType = INFO, string? customStyle = null)
        {
            Text = text;
            BadgeType = badgeType;
            CustomStyle = customStyle;
        }

        public Size Measure(RenderContext ctx) => new Size(Text.Length + 2, 1);

        public List<List<Segment>> Render(Size bounds, RenderContext ctx)
        {
            if (bounds.Width <= 0 || bounds.Height <= 0)
                return new List<List<Segment>>();

            if (!ctx.ColorMode)
            {
                return new List<List<Segment>> { new List<Segment> { new Segment($"[{Text}]") } };
            }

            string style = CustomStyle ?? BadgeType.ToUpper() switch
            {
                PASS or SUCCESS => "\x1b[42;30;1m",
                FAIL or ERROR => "\x1b[41;97;1m",
                WARN or WARNING => "\x1b[43;30;1m",
                RUNNING => "\x1b[44;97;1m",
                _ => "\x1b[46;30;1m"
            };

            return new List<List<Segment>> { new List<Segment> { new Segment($" {Text} ", style) } };
        }
    }

    public class ProgressBar : IRenderable
    {
        private readonly object _lock = new object();
        private readonly string[] _spinnerChars = { "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏" };
        private int _spinnerIdx = 0;

        public int Total { get; set; }
        public int Completed { get; set; }
        public string? Label { get; set; }

        public ProgressBar(int total = 100, int completed = 0, string? label = null)
        {
            Total = total <= 0 ? 100 : total;
            Completed = completed;
            Label = label;
        }

        public void Update(int completed)
        {
            lock (_lock)
            {
                Completed = Math.Min(completed, Total);
                _spinnerIdx = (_spinnerIdx + 1) % _spinnerChars.Length;
            }
        }

        public Size Measure(RenderContext ctx) => new Size(ctx.Bounds.Width, 1);

        public List<List<Segment>> Render(Size bounds, RenderContext ctx)
        {
            lock (_lock)
            {
                if (bounds.Width <= 0 || bounds.Height <= 0)
                    return new List<List<Segment>>();

                double pct = Math.Clamp((double)Completed / Total, 0.0, 1.0);
                string pctStr = $"{pct * 100,3:0}%";
                string spinner = (ctx.ColorMode && !ctx.AsciiMode) ? _spinnerChars[_spinnerIdx] : "*";

                string labelStr = !string.IsNullOrEmpty(Label) ? Label + " " : string.Empty;
                int fixedWidth = VisualMeter.Measure(labelStr) + 1 + 1 + pctStr.Length + 1;
                int barWidth = Math.Max(5, bounds.Width - fixedWidth);

                int filled = (int)(barWidth * pct);
                int empty = Math.Max(0, barWidth - filled);

                string fillChar = (ctx.ColorMode && !ctx.AsciiMode) ? "━" : "=";
                string emptyChar = (ctx.ColorMode && !ctx.AsciiMode) ? "╌" : "-";

                var row = new List<Segment>();
                if (!string.IsNullOrEmpty(labelStr)) row.Add(new Segment(labelStr, "\x1b[97m"));
                row.Add(new Segment(spinner + " ", "\x1b[96;1m"));
                row.Add(new Segment(new string(fillChar[0], filled), "\x1b[92;1m"));
                row.Add(new Segment(new string(emptyChar[0], empty), "\x1b[90m"));
                row.Add(new Segment(" " + pctStr, "\x1b[97;1m"));

                return new List<List<Segment>> { row };
            }
        }
    }

    public class RollingLogStream : IRenderable
    {
        private readonly object _lock = new object();
        public int MaxLines { get; }
        public List<string> Lines { get; }

        public RollingLogStream(int maxLines = 100)
        {
            MaxLines = maxLines <= 0 ? 100 : maxLines;
            Lines = new List<string>();
        }

        public void Append(string line)
        {
            lock (_lock)
            {
                Lines.Add(line);
                if (Lines.Count > MaxLines)
                {
                    Lines.RemoveAt(0);
                }
            }
        }

        public Size Measure(RenderContext ctx)
        {
            lock (_lock)
            {
                return new Size(ctx.Bounds.Width, Lines.Count);
            }
        }

        public List<List<Segment>> Render(Size bounds, RenderContext ctx)
        {
            lock (_lock)
            {
                if (bounds.Width <= 0 || bounds.Height <= 0)
                    return new List<List<Segment>>();

                int start = Math.Max(0, Lines.Count - bounds.Height);
                var visible = Lines.GetRange(start, Lines.Count - start);

                var result = new List<List<Segment>>(visible.Count);
                foreach (var line in visible)
                {
                    string txt = ctx.ColorMode ? line : VisualMeter.StripAnsi(line);
                    if (VisualMeter.Measure(txt) > bounds.Width)
                    {
                        string clean = VisualMeter.StripAnsi(txt);
                        txt = clean.Substring(0, Math.Min(clean.Length, bounds.Width));
                    }
                    result.Add(new List<Segment> { new Segment(txt) });
                }
                return result;
            }
        }
    }

    public class Column
    {
        public string Header { get; set; }
        public int MinWidth { get; set; }
        public int? MaxWidth { get; set; }
        public int Flex { get; set; }
        public string Align { get; set; }

        public Column(string header, int minWidth = 10, int? maxWidth = null, int flex = 1, string align = "left")
        {
            Header = header;
            MinWidth = minWidth;
            MaxWidth = maxWidth;
            Flex = flex;
            Align = align;
        }
    }

    public class LiveTable : IRenderable
    {
        private readonly object _lock = new object();
        public List<Column> Columns { get; }
        public List<(string Id, List<object> Cells)> Rows { get; } = new List<(string, List<object>)>();

        public LiveTable(List<Column> columns)
        {
            Columns = columns;
        }

        public void AddRow(string id, List<object> cells)
        {
            lock (_lock)
            {
                Rows.Add((id, cells));
            }
        }

        public void UpdateCell(string id, int colIdx, object val)
        {
            lock (_lock)
            {
                for (int i = 0; i < Rows.Count; i++)
                {
                    if (Rows[i].Id == id)
                    {
                        if (colIdx >= 0 && colIdx < Rows[i].Cells.Count)
                        {
                            Rows[i].Cells[colIdx] = val;
                        }
                        break;
                    }
                }
            }
        }

        public void UpdateRow(string id, List<object> cells)
        {
            lock (_lock)
            {
                for (int i = 0; i < Rows.Count; i++)
                {
                    if (Rows[i].Id == id)
                    {
                        Rows[i] = (id, cells);
                        break;
                    }
                }
            }
        }

        public Size Measure(RenderContext ctx)
        {
            lock (_lock)
            {
                return new Size(ctx.Bounds.Width, Rows.Count + 2);
            }
        }

        public List<List<Segment>> Render(Size bounds, RenderContext ctx)
        {
            lock (_lock)
            {
                if (bounds.Width <= 0 || bounds.Height <= 0 || Columns.Count == 0)
                    return new List<List<Segment>>();

                int numCols = Columns.Count;
                int[] colWidths = new int[numCols];
                int remaining = bounds.Width - (numCols - 1);

                for (int i = 0; i < numCols; i++)
                {
                    int minW = Columns[i].MinWidth > 0 ? Columns[i].MinWidth : VisualMeter.Measure(Columns[i].Header);
                    colWidths[i] = minW;
                    remaining -= minW;
                }

                int flexSum = 0;
                foreach (var col in Columns)
                {
                    if (col.Flex > 0) flexSum += col.Flex;
                }

                if (flexSum > 0 && remaining > 0)
                {
                    double flexUnit = (double)remaining / flexSum;
                    for (int i = 0; i < numCols; i++)
                    {
                        if (Columns[i].Flex > 0)
                        {
                            int alloc = (int)(Columns[i].Flex * flexUnit);
                            colWidths[i] += alloc;
                            remaining -= alloc;
                        }
                    }
                    if (remaining > 0) colWidths[0] += remaining;
                }

                var lines = new List<List<Segment>>();

                // Header Row
                var headerRow = new List<Segment>();
                for (int i = 0; i < numCols; i++)
                {
                    int w = colWidths[i];
                    var tObj = new Text(Columns[i].Header, "\x1b[96;1m", Columns[i].Align);
                    var subCtx = new RenderContext(new Size(w, 1), ctx.ColorMode, ctx.AsciiMode);
                    var tSegs = tObj.Render(new Size(w, 1), subCtx);
                    if (tSegs.Count > 0) headerRow.AddRange(tSegs[0]);
                    if (i < numCols - 1) headerRow.Add(new Segment(" "));
                }
                lines.Add(headerRow);

                // Separator Row
                string sepChar = (ctx.ColorMode && !ctx.AsciiMode) ? "─" : "-";
                var sepRow = new List<Segment>();
                for (int i = 0; i < numCols; i++)
                {
                    sepRow.Add(new Segment(new string(sepChar[0], colWidths[i]), "\x1b[90m"));
                    if (i < numCols - 1) sepRow.Add(new Segment(" "));
                }
                lines.Add(sepRow);

                // Data Rows
                foreach (var row in Rows)
                {
                    var rowSegs = new List<Segment>();
                    for (int i = 0; i < numCols; i++)
                    {
                        int w = colWidths[i];
                        object? val = i < row.Cells.Count ? row.Cells[i] : null;
                        var subCtx = new RenderContext(new Size(w, 1), ctx.ColorMode, ctx.AsciiMode);

                        if (val is IRenderable rend)
                        {
                            var rendered = rend.Render(new Size(w, 1), subCtx);
                            if (rendered.Count > 0)
                            {
                                rowSegs.AddRange(rendered[0]);
                                int lineLen = 0;
                                foreach (var s in rendered[0]) lineLen += VisualMeter.Measure(s.Text);
                                int pad = w - lineLen;
                                if (pad > 0) rowSegs.Add(new Segment(new string(' ', pad)));
                            }
                            else
                            {
                                rowSegs.Add(new Segment(new string(' ', w)));
                            }
                        }
                        else
                        {
                            string strVal = val?.ToString() ?? string.Empty;
                            var tObj = new Text(strVal, null, Columns[i].Align);
                            var rendered = tObj.Render(new Size(w, 1), subCtx);
                            if (rendered.Count > 0) rowSegs.AddRange(rendered[0]);
                        }

                        if (i < numCols - 1) rowSegs.Add(new Segment(" "));
                    }
                    lines.Add(rowSegs);
                }

                return lines;
            }
        }
    }

    // --- Engine ---

    public class Canvas
    {
        public Size Size { get; }
        private readonly (char Char, string? Style)[,] _grid;

        public Canvas(Size size)
        {
            Size = size;
            _grid = new (char, string?)[size.Height, size.Width];
            Clear();
        }

        public void Clear()
        {
            for (int y = 0; y < Size.Height; y++)
            {
                for (int x = 0; x < Size.Width; x++)
                {
                    _grid[y, x] = (' ', null);
                }
            }
        }

        public void Blit(int startX, int startY, List<Segment> segments)
        {
            if (startY < 0 || startY >= Size.Height) return;

            int currX = startX;
            foreach (var seg in segments)
            {
                string clean = VisualMeter.StripAnsi(seg.Text);
                foreach (char ch in clean)
                {
                    if (currX >= 0 && currX < Size.Width)
                    {
                        _grid[startY, currX] = (ch, seg.Style);
                    }
                    currX++;
                    if (currX >= Size.Width) break;
                }
                if (currX >= Size.Width) break;
            }
        }

        public List<string> RenderToStrings()
        {
            var res = new List<string>(Size.Height);
            for (int y = 0; y < Size.Height; y++)
            {
                var sb = new StringBuilder();
                string? currentStyle = null;
                for (int x = 0; x < Size.Width; x++)
                {
                    var (ch, style) = _grid[y, x];
                    if (style != currentStyle)
                    {
                        if (currentStyle != null) sb.Append("\x1b[0m");
                        if (style != null) sb.Append(style);
                        currentStyle = style;
                    }
                    sb.Append(ch);
                }
                if (currentStyle != null) sb.Append("\x1b[0m");
                res.Add(sb.ToString());
            }
            return res;
        }
    }

    public class LiveEngine : IDisposable
    {
        public const string INLINE = "inline";
        public const string ALTERNATE_SCREEN = "alternate_screen";

        public IRenderable Renderable { get; }
        public string Mode { get; }
        public double RefreshRateHz { get; }
        public bool ColorMode { get; set; }
        public bool AsciiMode { get; set; }

        private readonly object _lock = new object();
        private bool _running;
        private Timer? _timer;
        private Canvas? _canvas;
        private int _renderedLines;

        public LiveEngine(IRenderable renderable, string mode = INLINE, double refreshRateHz = 10.0)
        {
            Renderable = renderable;
            Mode = mode;
            RefreshRateHz = refreshRateHz > 0 ? refreshRateHz : 10.0;
            ColorMode = ChronicleLogger.GetColorMode();
            AsciiMode = ChronicleLogger.GetAsciiMode();
        }

        public void Start()
        {
            lock (_lock)
            {
                if (_running) return;
                _running = true;
            }

            ColorMode = ChronicleLogger.GetColorMode();
            AsciiMode = ChronicleLogger.GetAsciiMode();

            if (ColorMode)
            {
                Console.Write("\x1b[?25l"); // Hide cursor
            }
            if (Mode == ALTERNATE_SCREEN && ColorMode)
            {
                Console.Write("\x1b[?1049h"); // Alternate screen
            }

            if (!ColorMode)
            {
                Refresh();
            }

            Console.CancelKeyPress += OnCancelKeyPress;

            int intervalMs = ColorMode ? (int)(1000.0 / RefreshRateHz) : 5000;
            _timer = new Timer(_ => Refresh(), null, intervalMs, intervalMs);
        }

        private void OnCancelKeyPress(object? sender, ConsoleCancelEventArgs e)
        {
            Stop();
        }

        public void Stop()
        {
            lock (_lock)
            {
                if (!_running) return;
                _running = false;
            }

            _timer?.Dispose();
            _timer = null;

            if (ColorMode)
            {
                if (Mode == ALTERNATE_SCREEN)
                {
                    Console.Write("\x1b[?1049l");
                }
                Console.Write("\x1b[?25h"); // Show cursor
            }

            if (!ColorMode)
            {
                Refresh();
            }
        }

        public void Refresh()
        {
            lock (_lock)
            {
                var size = TerminalMetrics.GetSize();
                if (Mode == INLINE)
                {
                    var ctx = new RenderContext(size, ColorMode, AsciiMode);
                    var measured = Renderable.Measure(ctx);
                    int h = Math.Min(measured.Height, size.Height - 1);
                    size = new Size(size.Width, h);
                }

                if (_canvas == null || !_canvas.Size.Equals(size))
                {
                    _canvas = new Canvas(size);
                }

                _canvas.Clear();

                var rCtx = new RenderContext(size, ColorMode, AsciiMode);
                var lines = Renderable.Render(size, rCtx);

                for (int y = 0; y < lines.Count && y < size.Height; y++)
                {
                    _canvas.Blit(0, y, lines[y]);
                }

                var renderedStrings = _canvas.RenderToStrings();

                if (ColorMode)
                {
                    if (Mode == INLINE && _renderedLines > 0)
                    {
                        Console.Write($"\x1b[{_renderedLines}A");
                    }

                    foreach (var rStr in renderedStrings)
                    {
                        Console.Write("\x1b[2K" + rStr + "\n");
                    }
                    _renderedLines = renderedStrings.Count;
                }
                else
                {
                    Console.WriteLine("\n--- Live Snapshot ---");
                    foreach (var rStr in renderedStrings)
                    {
                        Console.WriteLine(rStr);
                    }
                    Console.WriteLine("---------------------\n");
                }
            }
        }

        public void Dispose()
        {
            Stop();
        }
    }
}
