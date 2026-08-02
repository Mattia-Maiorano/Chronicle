import 'io_stub.dart' if (dart.library.io) 'dart:io';

bool _colorMode = true;

void setColorMode([bool enabled = true]) {
  _colorMode = enabled;
}

bool getColorMode() {
  return _colorMode;
}

void setColorlessMode([bool enabled = true]) {
  _colorMode = !enabled;
}

void setAsciiMode([bool enabled = true]) {
  setColorlessMode(enabled);
}

bool getAsciiMode() {
  return !_colorMode;
}

class Colors {
  // Text colors
  static const String black = '\x1B[30m';
  static const String red = '\x1B[31m';
  static const String green = '\x1B[32m';
  static const String yellow = '\x1B[33m';
  static const String blue = '\x1B[34m';
  static const String magenta = '\x1B[35m';
  static const String cyan = '\x1B[36m';
  static const String white = '\x1B[37m';

  // Bright text colors
  static const String brightBlack = '\x1B[90m';
  static const String brightRed = '\x1B[91m';
  static const String brightGreen = '\x1B[92m';
  static const String brightYellow = '\x1B[93m';
  static const String brightBlue = '\x1B[94m';
  static const String brightMagenta = '\x1B[95m';
  static const String brightCyan = '\x1B[96m';
  static const String brightWhite = '\x1B[97m';

  // Background colors
  static const String bgBlack = '\x1B[40m';
  static const String bgRed = '\x1B[41m';
  static const String bgGreen = '\x1B[42m';
  static const String bgYellow = '\x1B[43m';
  static const String bgBlue = '\x1B[44m';
  static const String bgMagenta = '\x1B[45m';
  static const String bgCyan = '\x1B[46m';
  static const String bgWhite = '\x1B[47m';

  // Styles
  static const String bold = '\x1B[1m';
  static const String dim = '\x1B[2m';
  static const String italic = '\x1B[3m';
  static const String underline = '\x1B[4m';
  static const String blink = '\x1B[5m';
  static const String reverse = '\x1B[7m';

  // Reset
  static const String reset = '\x1B[0m';

  // Semantic colors
  static String get error => red;
  static String get warning => yellow;
  static String get success => green;
  static String get info => cyan;
  static String get debug => brightMagenta;
  static String get header => brightCyan;
  static String get emphasis => brightYellow;
}

void _write(String msg) {
  try {
    stdout.write(msg);
  } catch (_) {
    print(msg);
  }
}

void log({
  int indentationTabs = 0,
  int newlineBefore = 0,
  int newlineAfter = 0,
  String? color,
  String content = "",
  bool? colorMode,
}) {
  final useColor = colorMode ?? _colorMode;

  if (newlineBefore > 0) {
    _write('\n' * (newlineBefore - 1));
  }

  final indentation = '\t' * indentationTabs;
  late final String message;

  if (color != null && useColor) {
    message = "$indentation$color$content${Colors.reset}";
  } else {
    message = "$indentation$content";
  }

  _write(message);

  if (newlineAfter > 0) {
    _write('\n' * newlineAfter);
  } else {
    _write('\n');
  }
}

void logNewline([int count = 1]) {
  if (count > 1) {
    _write('\n' * (count - 1));
  }
  _write('\n');
}

void logApplicationTitle(String title, {int width = 60, bool? colorMode}) {
  final useColor = colorMode ?? _colorMode;

  var calcWidth = width;
  final titleLength = title.length;
  if (titleLength + 2 > calcWidth - 2) {
    calcWidth = titleLength + 4;
  }

  final padding = (calcWidth - 2 - titleLength) ~/ 2;
  final paddedTitle = (" " * padding) + title + (" " * (calcWidth - 2 - titleLength - padding));

  late final String topBorder;
  late final String middleLine;
  late final String bottomBorder;
  late final String? color;

  if (useColor) {
    topBorder = "╔${"═" * (calcWidth - 2)}╗";
    middleLine = "║$paddedTitle║";
    bottomBorder = "╚${"═" * (calcWidth - 2)}╝";
    color = "${Colors.brightMagenta}${Colors.bold}";
  } else {
    topBorder = "+${"-" * (calcWidth - 2)}+";
    middleLine = "|$paddedTitle|";
    bottomBorder = "+${"-" * (calcWidth - 2)}+";
    color = null;
  }

  logNewline(2);
  log(indentationTabs: 0, newlineBefore: 1, newlineAfter: 0, color: color, content: topBorder, colorMode: useColor);
  log(indentationTabs: 0, newlineBefore: 0, newlineAfter: 0, color: color, content: middleLine, colorMode: useColor);
  log(indentationTabs: 0, newlineBefore: 0, newlineAfter: 1, color: color, content: bottomBorder, colorMode: useColor);
  logNewline(2);
}

void logSectionHeader(String title, {int indentationTabs = 0, bool? colorMode}) {
  final useColor = colorMode ?? _colorMode;
  final color = useColor ? "${Colors.header}${Colors.bold}" : null;
  final separator = "=" * 60;

  log(indentationTabs: indentationTabs, newlineBefore: 1, newlineAfter: 0, color: color, content: separator, colorMode: useColor);
  log(indentationTabs: indentationTabs, newlineBefore: 0, newlineAfter: 0, color: color, content: title, colorMode: useColor);
  log(indentationTabs: indentationTabs, newlineBefore: 0, newlineAfter: 1, color: color, content: separator, colorMode: useColor);
  logNewline();
}

void logSubsection(String title, {int indentationTabs = 0, bool? colorMode}) {
  final useColor = colorMode ?? _colorMode;
  final color = useColor ? Colors.brightCyan : null;
  final separator = "-" * 40;

  log(indentationTabs: indentationTabs, newlineBefore: 1, newlineAfter: 0, color: color, content: separator, colorMode: useColor);
  log(indentationTabs: indentationTabs, newlineBefore: 0, newlineAfter: 0, color: color, content: title, colorMode: useColor);
  log(indentationTabs: indentationTabs, newlineBefore: 0, newlineAfter: 0, color: color, content: separator, colorMode: useColor);
  logNewline();
}

void logError(
  String message, {
  int indentationTabs = 0,
  int newlineBefore = 0,
  int newlineAfter = 0,
  bool? colorMode,
}) {
  final useColor = colorMode ?? _colorMode;
  final prefix = useColor ? "ERROR:" : "[ERROR]";
  final color = useColor ? "${Colors.error}${Colors.bold}" : null;
  log(
    indentationTabs: indentationTabs,
    newlineBefore: newlineBefore,
    newlineAfter: newlineAfter,
    color: color,
    content: "$prefix $message",
    colorMode: useColor,
  );
}

void logWarning(
  String message, {
  int indentationTabs = 0,
  int newlineBefore = 0,
  int newlineAfter = 0,
  bool? colorMode,
}) {
  final useColor = colorMode ?? _colorMode;
  final prefix = useColor ? "WARNING:" : "[WARNING]";
  final color = useColor ? "${Colors.warning}${Colors.bold}" : null;
  log(
    indentationTabs: indentationTabs,
    newlineBefore: newlineBefore,
    newlineAfter: newlineAfter,
    color: color,
    content: "$prefix $message",
    colorMode: useColor,
  );
}

void logSuccess(
  String message, {
  int indentationTabs = 0,
  int newlineBefore = 0,
  int newlineAfter = 0,
  bool? colorMode,
}) {
  final useColor = colorMode ?? _colorMode;
  final prefix = useColor ? "SUCCESS:" : "[OK]";
  final color = useColor ? "${Colors.success}${Colors.bold}" : null;
  log(
    indentationTabs: indentationTabs,
    newlineBefore: newlineBefore,
    newlineAfter: newlineAfter,
    color: color,
    content: "$prefix $message",
    colorMode: useColor,
  );
}

void logInfo(
  String message, {
  int indentationTabs = 0,
  int newlineBefore = 0,
  int newlineAfter = 0,
  bool? colorMode,
}) {
  final useColor = colorMode ?? _colorMode;
  final prefix = useColor ? "INFO:" : "[INFO]";
  final color = useColor ? Colors.info : null;
  log(
    indentationTabs: indentationTabs,
    newlineBefore: newlineBefore,
    newlineAfter: newlineAfter,
    color: color,
    content: "$prefix $message",
    colorMode: useColor,
  );
}

void logDebug(
  String message, {
  int indentationTabs = 2,
  int newlineBefore = 0,
  int newlineAfter = 0,
  bool? colorMode,
}) {
  final useColor = colorMode ?? _colorMode;
  final prefix = useColor ? "DEBUG:" : "[DEBUG]";
  final color = useColor ? "${Colors.debug}${Colors.bold}" : null;
  log(
    indentationTabs: indentationTabs,
    newlineBefore: newlineBefore,
    newlineAfter: newlineAfter,
    color: color,
    content: "$prefix $message",
    colorMode: useColor,
  );
}

void logStep(
  int stepNumber,
  int totalSteps,
  String description, {
  int indentationTabs = 0,
  bool? colorMode,
}) {
  final useColor = colorMode ?? _colorMode;
  final color = useColor ? "${Colors.brightBlue}${Colors.bold}" : null;
  logNewline();
  log(
    indentationTabs: indentationTabs,
    newlineBefore: 1,
    newlineAfter: 0,
    color: color,
    content: "[Step $stepNumber/$totalSteps] $description",
    colorMode: useColor,
  );
  logNewline();
}

void logFileSaved(
  String filepath, {
  int indentationTabs = 1,
  bool? colorMode,
}) {
  final useColor = colorMode ?? _colorMode;
  const prefix = "Saved:";
  final color = useColor ? Colors.success : null;
  log(
    indentationTabs: indentationTabs,
    newlineBefore: 0,
    newlineAfter: 0,
    color: color,
    content: "$prefix $filepath",
    colorMode: useColor,
  );
}

void logFinalResult(
  bool success,
  String message, {
  int width = 60,
  bool? colorMode,
}) {
  final useColor = colorMode ?? _colorMode;
  final color = useColor
      ? (success ? "${Colors.success}${Colors.bold}" : "${Colors.error}${Colors.bold}")
      : null;
  final separator = "=" * width;

  logNewline(2);
  log(indentationTabs: 0, newlineBefore: 1, newlineAfter: 0, color: color, content: separator, colorMode: useColor);
  if (success) {
    logSuccess(message, newlineAfter: 1, colorMode: useColor);
  } else {
    logError(message, newlineAfter: 1, colorMode: useColor);
  }
  log(indentationTabs: 0, newlineBefore: 0, newlineAfter: 1, color: color, content: separator, colorMode: useColor);
  logNewline(2);
}

// Tree Structured Logger

void logBanner(String title, {int width = 54, bool? colorMode}) =>
    _logBanner(title, width: width, colorMode: colorMode);

void logSection(String category, {int indentLevel = 0, bool? colorMode}) =>
    _logSection(category, indentLevel: indentLevel, colorMode: colorMode);

void logDetail(Object label, Object value, {int indentLevel = 0, bool? colorMode}) =>
    _logDetail(label, value, indentLevel: indentLevel, colorMode: colorMode);

void logDecision(String action, {String? detail, int indentLevel = 0, bool? colorMode}) =>
    _logDecision(action, detail: detail, indentLevel: indentLevel, colorMode: colorMode);

void logMessage(String message, {int indentLevel = 0, bool? colorMode}) =>
    _logMessage(message, indentLevel: indentLevel, colorMode: colorMode);

void _logBanner(String title, {int width = 54, bool? colorMode}) {
  final useColor = colorMode ?? _colorMode;
  var calcWidth = width;
  final minWidth = title.length + 6;
  if (calcWidth < minWidth) {
    calcWidth = minWidth;
  }

  final lineDashes = "-" * (calcWidth - 2);
  final padded = "| [${title.toUpperCase()}]".padRight(calcWidth - 1);

  if (useColor) {
    final c = "${Colors.header}${Colors.bold}";
    const r = Colors.reset;
    final top = "$c+$lineDashes+$r";
    final mid = "$c$padded|$r";
    final bot = "$c+$lineDashes+$r";
    _write("\n$top\n$mid\n$bot\n\n");
  } else {
    final top = "+$lineDashes+";
    final mid = "$padded|";
    final bot = "+$lineDashes+";
    _write("\n$top\n$mid\n$bot\n\n");
  }
}

void _logSection(String category, {int indentLevel = 0, bool? colorMode}) {
  final useColor = colorMode ?? _colorMode;
  final indent = "  " * indentLevel;
  final catStr = category.endsWith(":") ? category : "$category:";

  if (useColor) {
    const cTree = Colors.brightCyan;
    final cCat = "${Colors.brightCyan}${Colors.bold}";
    const r = Colors.reset;
    _write("\n$indent  $cTree|--$r $cCat$catStr$r\n");
  } else {
    _write("\n$indent  |-- $catStr\n");
  }
}

void _logDetail(Object label, Object value, {int indentLevel = 0, bool? colorMode}) {
  final useColor = colorMode ?? _colorMode;
  final indent = "  " * (indentLevel + 1);
  final formattedLabel = label.toString().padRight(22);

  if (useColor) {
    const cTree = Colors.brightCyan;
    final cLabel = "${Colors.cyan}${Colors.bold}";
    final cVal = "${Colors.brightWhite}${Colors.bold}";
    const r = Colors.reset;
    _write("$indent$cTree+--$r $cLabel$formattedLabel$r : $cVal$value$r\n");
  } else {
    _write("$indent+-- $formattedLabel : $value\n");
  }
}

void _logDecision(String action, {String? detail, int indentLevel = 0, bool? colorMode}) {
  final useColor = colorMode ?? _colorMode;
  final indent = "  " * indentLevel;

  if (useColor) {
    final cArrow = "${Colors.brightYellow}${Colors.bold}";
    final cAction = "${Colors.brightGreen}${Colors.bold}";
    const cDetail = Colors.brightWhite;
    const r = Colors.reset;

    if (detail != null && detail.trim().isNotEmpty) {
      _write("\n$indent  $cArrow+--> DECISION:$r $cAction$action$r -> $cDetail$detail$r\n\n");
    } else {
      _write("\n$indent  $cArrow+--> DECISION:$r $cAction$action$r\n\n");
    }
  } else {
    if (detail != null && detail.trim().isNotEmpty) {
      _write("\n$indent  +--> DECISION: $action -> $detail\n\n");
    } else {
      _write("\n$indent  +--> DECISION: $action\n\n");
    }
  }
}

void _logMessage(String message, {int indentLevel = 0, bool? colorMode}) {
  final useColor = colorMode ?? _colorMode;
  final indent = "  " * indentLevel;

  if (useColor) {
    const cTree = Colors.brightCyan;
    const cMsg = Colors.brightWhite;
    const r = Colors.reset;
    _write("$indent$cTree|--$r $cMsg$message$r\n");
  } else {
    _write("$indent|-- $message\n");
  }
}

class StructuredLogger {
  static void logBanner(String title, {int width = 54, bool? colorMode}) =>
      _logBanner(title, width: width, colorMode: colorMode);

  static void logSection(String category, {int indentLevel = 0, bool? colorMode}) =>
      _logSection(category, indentLevel: indentLevel, colorMode: colorMode);

  static void logDetail(Object label, Object value, {int indentLevel = 0, bool? colorMode}) =>
      _logDetail(label, value, indentLevel: indentLevel, colorMode: colorMode);

  static void logDecision(String action, {String? detail, int indentLevel = 0, bool? colorMode}) =>
      _logDecision(action, detail: detail, indentLevel: indentLevel, colorMode: colorMode);

  static void logMessage(String message, {int indentLevel = 0, bool? colorMode}) =>
      _logMessage(message, indentLevel: indentLevel, colorMode: colorMode);

  // Snake_case compatibility
  static void log_banner(String title, {int width = 54, bool? colorMode}) =>
      _logBanner(title, width: width, colorMode: colorMode);

  static void log_section(String category, {int indentLevel = 0, bool? colorMode}) =>
      _logSection(category, indentLevel: indentLevel, colorMode: colorMode);

  static void log_detail(Object label, Object value, {int indentLevel = 0, bool? colorMode}) =>
      _logDetail(label, value, indentLevel: indentLevel, colorMode: colorMode);

  static void log_decision(String action, {String? detail, int indentLevel = 0, bool? colorMode}) =>
      _logDecision(action, detail: detail, indentLevel: indentLevel, colorMode: colorMode);

  static void log_message(String message, {int indentLevel = 0, bool? colorMode}) =>
      _logMessage(message, indentLevel: indentLevel, colorMode: colorMode);
}

typedef AsciiLogger = StructuredLogger;
typedef KeeperLogger = StructuredLogger;

