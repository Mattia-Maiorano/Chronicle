import 'dart:async';
import 'io_stub.dart' if (dart.library.io) 'dart:io';
import 'chronicle.dart';

// --- Geometry ---

class Size {
  final int width;
  final int height;

  const Size(this.width, this.height);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Size &&
          runtimeType == other.runtimeType &&
          width == other.width &&
          height == other.height;

  @override
  int get hashCode => width.hashCode ^ height.hashCode;
}

class Point {
  final int x;
  final int y;

  const Point(this.x, this.y);
}

class Segment {
  final String text;
  final String? style;

  const Segment(this.text, [this.style]);
}

class VisualMeter {
  static final RegExp _ansiRegex = RegExp(r'\x1b\[[0-9;]*[a-zA-Z]');

  static String stripAnsi(String text) {
    if (text.isEmpty) return '';
    return text.replaceAll(_ansiRegex, '');
  }

  static int measure(String text) {
    if (text.isEmpty) return 0;
    return stripAnsi(text).runes.length;
  }
}

class TerminalMetrics {
  static Size getSize() {
    try {
      if (stdout.hasTerminal) {
        return Size(stdout.terminalColumns, stdout.terminalLines);
      }
    } catch (_) {}
    return const Size(80, 24);
  }
}

// --- Layout Base ---

class RenderContext {
  final Size bounds;
  final bool colorMode;
  final bool asciiMode;

  const RenderContext(this.bounds, this.colorMode, this.asciiMode);
}

abstract class Renderable {
  Size measure(RenderContext ctx);
  List<List<Segment>> render(Size bounds, RenderContext ctx);
}

// --- Layout Policies ---

abstract class Policy {}

class Fixed implements Policy {
  final int size;
  const Fixed(this.size);
}

class Flex implements Policy {
  final int weight;
  const Flex([this.weight = 1]);
}

class Ratio implements Policy {
  final double percentage;
  const Ratio(this.percentage);
}

// --- Layout Primitives ---

class Text implements Renderable {
  static const String left = "left";
  static const String center = "center";
  static const String right = "right";

  final String text;
  final String? style;
  final String align;
  final String truncateStr;

  const Text(this.text, {this.style, this.align = left, this.truncateStr = "..."});

  @override
  Size measure(RenderContext ctx) => Size(VisualMeter.measure(text), 1);

  @override
  List<List<Segment>> render(Size bounds, RenderContext ctx) {
    if (bounds.width <= 0 || bounds.height <= 0) return [];

    int textLen = VisualMeter.measure(text);
    String displayText = text;

    if (textLen > bounds.width) {
      if (bounds.width >= truncateStr.length) {
        final clean = VisualMeter.stripAnsi(text);
        final runes = clean.runes.toList();
        int allowed = bounds.width - truncateStr.length;
        if (allowed < 0) allowed = 0;
        if (allowed > runes.length) allowed = runes.length;
        displayText = String.fromCharCodes(runes.sublist(0, allowed)) + truncateStr;
        textLen = bounds.width;
      } else {
        displayText = "";
        textLen = 0;
      }
    }

    int padTotal = bounds.width - textLen;
    if (padTotal < 0) padTotal = 0;
    int padLeft = 0, padRight = 0;

    if (align == center) {
      padLeft = padTotal ~/ 2;
      padRight = padTotal - padLeft;
    } else if (align == right) {
      padLeft = padTotal;
    } else {
      padRight = padTotal;
    }

    final row = <Segment>[];
    if (padLeft > 0) row.add(Segment(' ' * padLeft));
    row.add(Segment(displayText, ctx.colorMode ? style : null));
    if (padRight > 0) row.add(Segment(' ' * padRight));

    return [row];
  }
}

class Rule implements Renderable {
  final String? title;
  final String? style;
  final String character;

  const Rule({this.title, this.style, this.character = "─"});

  @override
  Size measure(RenderContext ctx) => Size(ctx.bounds.width, 1);

  @override
  List<List<Segment>> render(Size bounds, RenderContext ctx) {
    if (bounds.width <= 0 || bounds.height <= 0) return [];

    final ch = (ctx.colorMode && !ctx.asciiMode) ? character : "-";
    final s = ctx.colorMode ? style : null;

    if (title == null || title!.isEmpty) {
      return [
        [Segment(ch * bounds.width, s)]
      ];
    }

    final titleText = " $title ";
    final titleLen = VisualMeter.measure(titleText);

    if (titleLen >= bounds.width) {
      final runes = titleText.runes.toList();
      return [
        [Segment(String.fromCharCodes(runes.sublist(0, bounds.width.clamp(0, runes.length))), s)]
      ];
    }

    final leftDash = (bounds.width - titleLen) ~/ 2;
    final rightDash = bounds.width - titleLen - leftDash;

    final row = <Segment>[];
    if (leftDash > 0) row.add(Segment(ch * leftDash, s));
    row.add(Segment(titleText, s));
    if (rightDash > 0) row.add(Segment(ch * rightDash, s));

    return [row];
  }
}

class BorderGlyphs {
  final String tl, tr, bl, br, h, v;
  const BorderGlyphs(this.tl, this.tr, this.bl, this.br, this.h, this.v);
}

class Panel implements Renderable {
  static const String rounded = "rounded";
  static const String square = "square";
  static const String doubleBorder = "double";
  static const String chronicleTree = "chronicle_tree";

  static const Map<String, BorderGlyphs> _styles = {
    rounded: BorderGlyphs("╭", "╮", "╰", "╯", "─", "│"),
    square: BorderGlyphs("┌", "┐", "└", "┘", "─", "│"),
    doubleBorder: BorderGlyphs("╔", "╗", "╚", "╝", "═", "║"),
    chronicleTree: BorderGlyphs("+", "+", "+", "+", "-", "|"),
  };

  final Renderable child;
  final String? title;
  final String? subtitle;
  final String borderStyle;
  final int padding;
  final String? borderColor;

  const Panel(
    this.child, {
    this.title,
    this.subtitle,
    this.borderStyle = rounded,
    this.padding = 1,
    this.borderColor,
  });

  @override
  Size measure(RenderContext ctx) {
    final innerCtx = RenderContext(
      Size(
        (ctx.bounds.width - 2 - (padding * 2)).clamp(0, ctx.bounds.width),
        (ctx.bounds.height - 2).clamp(0, ctx.bounds.height),
      ),
      ctx.colorMode,
      ctx.asciiMode,
    );
    final childSize = child.measure(innerCtx);
    return Size(childSize.width + 2 + (padding * 2), childSize.height + 2);
  }

  @override
  List<List<Segment>> render(Size bounds, RenderContext ctx) {
    if (bounds.width < 2 || bounds.height < 2) return [];

    BorderGlyphs glyphs = _styles[borderStyle] ?? _styles[chronicleTree]!;
    if (!ctx.colorMode || ctx.asciiMode) {
      glyphs = _styles[chronicleTree]!;
    }

    final bStyle = ctx.colorMode ? borderColor : null;
    final lines = <List<Segment>>[];
    final innerW = bounds.width - 2;

    // Top Border
    final topRow = <Segment>[Segment(glyphs.tl, bStyle)];
    if (title != null && title!.isNotEmpty) {
      final tText = " $title ";
      final tLen = VisualMeter.measure(tText);
      if (tLen >= innerW) {
        final runes = tText.runes.toList();
        topRow.add(Segment(String.fromCharCodes(runes.sublist(0, innerW.clamp(0, runes.length))), bStyle));
      } else {
        topRow.add(Segment(glyphs.h, bStyle));
        topRow.add(Segment(tText, bStyle));
        final rem = innerW - 1 - tLen;
        if (rem > 0) topRow.add(Segment(glyphs.h * rem, bStyle));
      }
    } else {
      topRow.add(Segment(glyphs.h * innerW, bStyle));
    }
    topRow.add(Segment(glyphs.tr, bStyle));
    lines.add(topRow);

    // Inner Content
    final innerH = bounds.height - 2;
    final childW = (innerW - (padding * 2)).clamp(0, innerW);
    final innerBounds = Size(childW, innerH);
    final childLines = child.render(innerBounds, ctx);

    for (int y = 0; y < innerH; y++) {
      final row = <Segment>[Segment(glyphs.v, bStyle)];
      if (padding > 0) row.add(Segment(' ' * padding));

      if (y < childLines.length) {
        row.addAll(childLines[y]);
        int lineLen = 0;
        for (final s in childLines[y]) {
          lineLen += VisualMeter.measure(s.text);
        }
        final pad = childW - lineLen;
        if (pad > 0) row.add(Segment(' ' * pad));
      } else {
        row.add(Segment(' ' * childW));
      }

      if (padding > 0) row.add(Segment(' ' * padding));
      row.add(Segment(glyphs.v, bStyle));
      lines.add(row);
    }

    // Bottom Border
    final botRow = <Segment>[Segment(glyphs.bl, bStyle)];
    if (subtitle != null && subtitle!.isNotEmpty) {
      final sText = " $subtitle ";
      final sLen = VisualMeter.measure(sText);
      if (sLen >= innerW) {
        final runes = sText.runes.toList();
        botRow.add(Segment(String.fromCharCodes(runes.sublist(0, innerW.clamp(0, runes.length))), bStyle));
      } else {
        botRow.add(Segment(glyphs.h, bStyle));
        botRow.add(Segment(sText, bStyle));
        final rem = innerW - 1 - sLen;
        if (rem > 0) botRow.add(Segment(glyphs.h * rem, bStyle));
      }
    } else {
      botRow.add(Segment(glyphs.h * innerW, bStyle));
    }
    botRow.add(Segment(glyphs.br, bStyle));
    lines.add(botRow);

    return lines;
  }
}

class FlexSplitter implements Renderable {
  static const String horizontal = "horizontal";
  static const String vertical = "vertical";

  final String direction;
  final List<MapEntry<Renderable, Policy>> children = [];

  FlexSplitter([this.direction = horizontal]);

  void add(Renderable child, [Policy? policy]) {
    children.add(MapEntry(child, policy ?? const Flex(1)));
  }

  @override
  Size measure(RenderContext ctx) => ctx.bounds;

  @override
  List<List<Segment>> render(Size bounds, RenderContext ctx) {
    if (children.isEmpty) return [];

    final totalSize = direction == horizontal ? bounds.width : bounds.height;
    final sizes = List<int>.filled(children.length, 0);
    int remaining = totalSize;

    // 1. Fixed & Ratio
    for (int i = 0; i < children.length; i++) {
      final pol = children[i].value;
      if (pol is Fixed) {
        sizes[i] = pol.size;
        remaining -= pol.size;
      } else if (pol is Ratio) {
        final alloc = (totalSize * pol.percentage).floor();
        sizes[i] = alloc;
        remaining -= alloc;
      }
    }

    // 2. Flex
    int flexSum = 0;
    for (final entry in children) {
      if (entry.value is Flex) flexSum += (entry.value as Flex).weight;
    }

    if (flexSum > 0 && remaining > 0) {
      final flexUnit = remaining / flexSum;
      int remFlex = remaining;
      for (int i = 0; i < children.length; i++) {
        if (children[i].value is Flex) {
          final alloc = ((children[i].value as Flex).weight * flexUnit).floor();
          sizes[i] = alloc;
          remFlex -= alloc;
        }
      }
      if (remFlex > 0) {
        for (int i = 0; i < children.length; i++) {
          if (children[i].value is Flex) {
            sizes[i] += remFlex;
            break;
          }
        }
      }
    }

    final renderedChildren = <MapEntry<Size, List<List<Segment>>>>[];
    for (int i = 0; i < children.length; i++) {
      final cBounds = direction == horizontal
          ? Size(sizes[i], bounds.height)
          : Size(bounds.width, sizes[i]);
      final cCtx = RenderContext(cBounds, ctx.colorMode, ctx.asciiMode);
      final cLines = children[i].key.render(cBounds, cCtx);
      renderedChildren.add(MapEntry(cBounds, cLines));
    }

    final lines = <List<Segment>>[];
    if (direction == horizontal) {
      for (int y = 0; y < bounds.height; y++) {
        final row = <Segment>[];
        for (final rc in renderedChildren) {
          if (y < rc.value.length) {
            row.addAll(rc.value[y]);
            int cLen = 0;
            for (final s in rc.value[y]) {
              cLen += VisualMeter.measure(s.text);
            }
            final pad = rc.key.width - cLen;
            if (pad > 0) row.add(Segment(' ' * pad));
          } else {
            row.add(Segment(' ' * rc.key.width));
          }
        }
        lines.add(row);
      }
    } else {
      for (final rc in renderedChildren) {
        for (int y = 0; y < rc.key.height; y++) {
          if (y < rc.value.length) {
            lines.add(rc.value[y]);
          } else {
            lines.add([Segment(' ' * bounds.width)]);
          }
        }
      }
    }

    return lines;
  }
}

class Layout extends FlexSplitter {
  Layout([String direction = FlexSplitter.horizontal]) : super(direction);
}

// --- Components ---

class Badge implements Renderable {
  static const String pass = "PASS";
  static const String success = "SUCCESS";
  static const String fail = "FAIL";
  static const String error = "ERROR";
  static const String warn = "WARN";
  static const String warning = "WARNING";
  static const String info = "INFO";
  static const String running = "RUNNING";

  final String text;
  final String badgeType;
  final String? customStyle;

  const Badge(this.text, {this.badgeType = info, this.customStyle});

  @override
  Size measure(RenderContext ctx) => Size(text.length + 2, 1);

  @override
  List<List<Segment>> render(Size bounds, RenderContext ctx) {
    if (bounds.width <= 0 || bounds.height <= 0) return [];

    if (!ctx.colorMode) {
      return [
        [Segment("[$text]")]
      ];
    }

    String style = customStyle ??
        (() {
          switch (badgeType.toUpperCase()) {
            case pass:
            case success:
              return "\x1b[42;30;1m";
            case fail:
            case error:
              return "\x1b[41;97;1m";
            case warn:
            case warning:
              return "\x1b[43;30;1m";
            case running:
              return "\x1b[44;97;1m";
            default:
              return "\x1b[46;30;1m";
          }
        })();

    return [
      [Segment(" $text ", style)]
    ];
  }
}

class ProgressBar implements Renderable {
  static const List<String> _spinnerChars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];
  int total;
  int completed;
  final String? label;
  int _spinnerIdx = 0;

  ProgressBar({this.total = 100, this.completed = 0, this.label}) {
    if (total <= 0) total = 100;
  }

  void update(int newCompleted) {
    completed = newCompleted.clamp(0, total);
    _spinnerIdx = (_spinnerIdx + 1) % _spinnerChars.length;
  }

  @override
  Size measure(RenderContext ctx) => Size(ctx.bounds.width, 1);

  @override
  List<List<Segment>> render(Size bounds, RenderContext ctx) {
    if (bounds.width <= 0 || bounds.height <= 0) return [];

    final pct = (completed / total).clamp(0.0, 1.0);
    final pctStr = "${(pct * 100).toStringAsFixed(0).padLeft(3)}%";
    final spinner = (ctx.colorMode && !ctx.asciiMode) ? _spinnerChars[_spinnerIdx] : "*";

    final labelStr = (label != null && label!.isNotEmpty) ? "$label " : "";
    final fixedWidth = VisualMeter.measure(labelStr) + 1 + 1 + pctStr.length + 1;
    final barWidth = (bounds.width - fixedWidth).clamp(5, bounds.width);

    final filled = (barWidth * pct).floor();
    final empty = (barWidth - filled).clamp(0, barWidth);

    final fillChar = (ctx.colorMode && !ctx.asciiMode) ? "━" : "=";
    final emptyChar = (ctx.colorMode && !ctx.asciiMode) ? "╌" : "-";

    final row = <Segment>[];
    if (labelStr.isNotEmpty) row.add(Segment(labelStr, "\x1b[97m"));
    row.add(Segment("$spinner ", "\x1b[96;1m"));
    row.add(Segment(fillChar * filled, "\x1b[92;1m"));
    row.add(Segment(emptyChar * empty, "\x1b[90m"));
    row.add(Segment(" $pctStr", "\x1b[97;1m"));

    return [row];
  }
}

class RollingLogStream implements Renderable {
  final int maxLines;
  final List<String> lines = [];

  RollingLogStream([this.maxLines = 100]);

  void append(String line) {
    lines.add(line);
    if (lines.length > maxLines) {
      lines.removeAt(0);
    }
  }

  @override
  Size measure(RenderContext ctx) => Size(ctx.bounds.width, lines.length);

  @override
  List<List<Segment>> render(Size bounds, RenderContext ctx) {
    if (bounds.width <= 0 || bounds.height <= 0) return [];

    final start = (lines.length - bounds.height).clamp(0, lines.length);
    final visible = lines.sublist(start);

    final result = <List<Segment>>[];
    for (final line in visible) {
      String txt = ctx.colorMode ? line : VisualMeter.stripAnsi(line);
      if (VisualMeter.measure(txt) > bounds.width) {
        final clean = VisualMeter.stripAnsi(txt);
        final runes = clean.runes.toList();
        txt = String.fromCharCodes(runes.sublist(0, bounds.width.clamp(0, runes.length)));
      }
      result.add([Segment(txt)]);
    }
    return result;
  }
}

class Column {
  final String header;
  final int minWidth;
  final int? maxWidth;
  final int flex;
  final String align;

  const Column(
    this.header, {
    this.minWidth = 10,
    this.maxWidth,
    this.flex = 1,
    this.align = "left",
  });
}

class LiveTable implements Renderable {
  final List<Column> columns;
  final List<MapEntry<String, List<dynamic>>> rows = [];

  LiveTable(this.columns);

  void addRow(String id, List<dynamic> cells) {
    rows.add(MapEntry(id, cells));
  }

  void updateCell(String id, int colIdx, dynamic val) {
    for (int i = 0; i < rows.length; i++) {
      if (rows[i].key == id) {
        if (colIdx >= 0 && colIdx < rows[i].value.length) {
          rows[i].value[colIdx] = val;
        }
        break;
      }
    }
  }

  void updateRow(String id, List<dynamic> cells) {
    for (int i = 0; i < rows.length; i++) {
      if (rows[i].key == id) {
        rows[i] = MapEntry(id, cells);
        break;
      }
    }
  }

  @override
  Size measure(RenderContext ctx) => Size(ctx.bounds.width, rows.length + 2);

  @override
  List<List<Segment>> render(Size bounds, RenderContext ctx) {
    if (bounds.width <= 0 || bounds.height <= 0 || columns.isEmpty) return [];

    final numCols = columns.length;
    final colWidths = List<int>.filled(numCols, 0);
    int remaining = bounds.width - (numCols - 1);

    for (int i = 0; i < numCols; i++) {
      int minW = columns[i].minWidth > 0 ? columns[i].minWidth : VisualMeter.measure(columns[i].header);
      colWidths[i] = minW;
      remaining -= minW;
    }

    int flexSum = 0;
    for (final col in columns) {
      if (col.flex > 0) flexSum += col.flex;
    }

    if (flexSum > 0 && remaining > 0) {
      final flexUnit = remaining / flexSum;
      for (int i = 0; i < numCols; i++) {
        if (columns[i].flex > 0) {
          final alloc = (columns[i].flex * flexUnit).floor();
          colWidths[i] += alloc;
          remaining -= alloc;
        }
      }
      if (remaining > 0) colWidths[0] += remaining;
    }

    final lines = <List<Segment>>[];

    // Header Row
    final headerRow = <Segment>[];
    for (int i = 0; i < numCols; i++) {
      final w = colWidths[i];
      final tObj = Text(columns[i].header, style: "\x1b[96;1m", align: columns[i].align);
      final subCtx = RenderContext(Size(w, 1), ctx.colorMode, ctx.asciiMode);
      final tSegs = tObj.render(Size(w, 1), subCtx);
      if (tSegs.isNotEmpty) headerRow.addAll(tSegs[0]);
      if (i < numCols - 1) headerRow.add(const Segment(" "));
    }
    lines.add(headerRow);

    // Separator Row
    final sepChar = (ctx.colorMode && !ctx.asciiMode) ? "─" : "-";
    final sepRow = <Segment>[];
    for (int i = 0; i < numCols; i++) {
      sepRow.add(Segment(sepChar * colWidths[i], "\x1b[90m"));
      if (i < numCols - 1) sepRow.add(const Segment(" "));
    }
    lines.add(sepRow);

    // Data Rows
    for (final row in rows) {
      final rowSegs = <Segment>[];
      for (int i = 0; i < numCols; i++) {
        final w = colWidths[i];
        final val = i < row.value.length ? row.value[i] : null;
        final subCtx = RenderContext(Size(w, 1), ctx.colorMode, ctx.asciiMode);

        if (val is Renderable) {
          final rendered = val.render(Size(w, 1), subCtx);
          if (rendered.isNotEmpty) {
            rowSegs.addAll(rendered[0]);
            int lineLen = 0;
            for (final s in rendered[0]) {
              lineLen += VisualMeter.measure(s.text);
            }
            final pad = w - lineLen;
            if (pad > 0) rowSegs.add(Segment(' ' * pad));
          } else {
            rowSegs.add(Segment(' ' * w));
          }
        } else {
          final strVal = val?.toString() ?? "";
          final tObj = Text(strVal, align: columns[i].align);
          final rendered = tObj.render(Size(w, 1), subCtx);
          if (rendered.isNotEmpty) rowSegs.addAll(rendered[0]);
        }

        if (i < numCols - 1) rowSegs.add(const Segment(" "));
      }
      lines.add(rowSegs);
    }

    return lines;
  }
}

// --- Engine ---

class Canvas {
  final Size size;
  late final List<List<MapEntry<String, String?>>> _grid;

  Canvas(this.size) {
    _grid = List.generate(
      size.height,
      (_) => List.generate(size.width, (_) => const MapEntry(' ', null)),
    );
  }

  void clear() {
    for (int y = 0; y < size.height; y++) {
      for (int x = 0; x < size.width; x++) {
        _grid[y][x] = const MapEntry(' ', null);
      }
    }
  }

  void blit(int startX, int startY, List<Segment> segments) {
    if (startY < 0 || startY >= size.height) return;

    int currX = startX;
    for (final seg in segments) {
      final clean = VisualMeter.stripAnsi(seg.text);
      for (final char in clean.split('')) {
        if (currX >= 0 && currX < size.width) {
          _grid[startY][currX] = MapEntry(char, seg.style);
        }
        currX++;
        if (currX >= size.width) break;
      }
      if (currX >= size.width) break;
    }
  }

  List<String> renderToStrings() {
    final res = <String>[];
    for (int y = 0; y < size.height; y++) {
      final sb = StringBuffer();
      String? currentStyle;
      for (int x = 0; x < size.width; x++) {
        final cell = _grid[y][x];
        final char = cell.key;
        final style = cell.value;

        if (style != currentStyle) {
          if (currentStyle != null) sb.write("\x1b[0m");
          if (style != null) sb.write(style);
          currentStyle = style;
        }
        sb.write(char);
      }
      if (currentStyle != null) sb.write("\x1b[0m");
      res.add(sb.toString());
    }
    return res;
  }
}

class LiveEngine {
  static const String inline = "inline";
  static const String alternateScreen = "alternate_screen";

  final Renderable renderable;
  final String mode;
  final double refreshRateHz;
  bool colorMode;
  bool asciiMode;

  bool _running = false;
  Timer? _timer;
  Canvas? _canvas;
  int _renderedLines = 0;

  LiveEngine(
    this.renderable, {
    this.mode = inline,
    this.refreshRateHz = 10.0,
  })  : colorMode = getColorMode(),
        asciiMode = getAsciiMode();

  void start() {
    if (_running) return;
    _running = true;

    colorMode = getColorMode();
    asciiMode = getAsciiMode();

    if (colorMode) {
      stdout.write("\x1b[?25l"); // Hide cursor
    }
    if (mode == alternateScreen && colorMode) {
      stdout.write("\x1b[?1049h");
    }

    if (!colorMode) {
      refresh();
    }

    final intervalMs = colorMode ? (1000 / refreshRateHz).round() : 5000;
    _timer = Timer.periodic(Duration(milliseconds: intervalMs), (_) => refresh());
  }

  void stop() {
    if (!_running) return;
    _running = false;

    _timer?.cancel();
    _timer = null;

    if (colorMode) {
      if (mode == alternateScreen) {
        stdout.write("\x1b[?1049l");
      }
      stdout.write("\x1b[?25h"); // Show cursor
    }

    if (!colorMode) {
      refresh();
    }
  }

  void refresh() {
    Size size = TerminalMetrics.getSize();
    if (mode == inline) {
      final ctx = RenderContext(size, colorMode, asciiMode);
      final measured = renderable.measure(ctx);
      final h = (measured.height).clamp(1, size.height - 1);
      size = Size(size.width, h);
    }

    if (_canvas == null || _canvas!.size != size) {
      _canvas = Canvas(size);
    }

    _canvas!.clear();

    final rCtx = RenderContext(size, colorMode, asciiMode);
    final lines = renderable.render(size, rCtx);

    for (int y = 0; y < lines.length && y < size.height; y++) {
      _canvas!.blit(0, y, lines[y]);
    }

    final renderedStrings = _canvas!.renderToStrings();

    if (colorMode) {
      if (mode == inline && _renderedLines > 0) {
        stdout.write("\x1b[${_renderedLines}A");
      }

      for (final rStr in renderedStrings) {
        stdout.write("\x1b[2K$rStr\n");
      }
      _renderedLines = renderedStrings.length;
    } else {
      print("\n--- Live Snapshot ---");
      for (final rStr in renderedStrings) {
        print(rStr);
      }
      print("---------------------\n");
    }
  }
}
