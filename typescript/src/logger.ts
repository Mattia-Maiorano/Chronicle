/**
 * Chronicle Logger for TypeScript / Node.js
 * Provides structured, colorized, and colorless console output matching SPEC.md.
 */

declare const process: any;

let _colorMode: boolean = true;


export function setColorMode(enabled: boolean = true): void {
  _colorMode = enabled;
}

export function getColorMode(): boolean {
  return _colorMode;
}

export function setColorlessMode(enabled: boolean = true): void {
  _colorMode = !enabled;
}

export function setAsciiMode(enabled: boolean = true): void {
  setColorlessMode(enabled);
}

export function getAsciiMode(): boolean {
  return !_colorMode;
}

export const Colors = {
  // Text colors
  BLACK: '\x1b[30m',
  RED: '\x1b[31m',
  GREEN: '\x1b[32m',
  YELLOW: '\x1b[33m',
  BLUE: '\x1b[34m',
  MAGENTA: '\x1b[35m',
  CYAN: '\x1b[36m',
  WHITE: '\x1b[37m',

  // Bright text colors
  BRIGHT_BLACK: '\x1b[90m',
  BRIGHT_RED: '\x1b[91m',
  BRIGHT_GREEN: '\x1b[92m',
  BRIGHT_YELLOW: '\x1b[93m',
  BRIGHT_BLUE: '\x1b[94m',
  BRIGHT_MAGENTA: '\x1b[95m',
  BRIGHT_CYAN: '\x1b[96m',
  BRIGHT_WHITE: '\x1b[97m',

  // Background colors
  BG_BLACK: '\x1b[40m',
  BG_RED: '\x1b[41m',
  BG_GREEN: '\x1b[42m',
  BG_YELLOW: '\x1b[43m',
  BG_BLUE: '\x1b[44m',
  BG_MAGENTA: '\x1b[45m',
  BG_CYAN: '\x1b[46m',
  BG_WHITE: '\x1b[47m',

  // Styles
  BOLD: '\x1b[1m',
  DIM: '\x1b[2m',
  ITALIC: '\x1b[3m',
  UNDERLINE: '\x1b[4m',
  BLINK: '\x1b[5m',
  REVERSE: '\x1b[7m',

  // Reset
  RESET: '\x1b[0m',

  // Semantic colors
  get ERROR() { return this.RED; },
  get WARNING() { return this.YELLOW; },
  get SUCCESS() { return this.GREEN; },
  get INFO() { return this.CYAN; },
  get DEBUG() { return this.BRIGHT_MAGENTA; },
  get HEADER() { return this.BRIGHT_CYAN; },
  get EMPHASIS() { return this.BRIGHT_YELLOW; },
};

export interface LogOptions {
  indentationTabs?: number;
  newlineBefore?: number;
  newlineAfter?: number;
  color?: string | null;
  content?: string;
  colorMode?: boolean | null;
}

export function log(
  indentationTabs: number = 0,
  newlineBefore: number = 0,
  newlineAfter: number = 0,
  color: string | null = null,
  content: string = "",
  colorMode: boolean | null = null
): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;

  if (newlineBefore > 0) {
    process.stdout.write('\n'.repeat(newlineBefore - 1));
  }

  const indentation = '\t'.repeat(indentationTabs);
  let message = "";

  if (color && useColor) {
    message = `${indentation}${color}${content}${Colors.RESET}`;
  } else {
    message = `${indentation}${content}`;
  }

  process.stdout.write(message);

  if (newlineAfter > 0) {
    process.stdout.write('\n'.repeat(newlineAfter));
  } else {
    process.stdout.write('\n');
  }
}

export function logNewline(count: number = 1): void {
  if (count > 1) {
    process.stdout.write('\n'.repeat(count - 1));
  }
  process.stdout.write('\n');
}

export function logApplicationTitle(title: string, width: number = 60, colorMode: boolean | null = null): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;

  const titleLength = title.length;
  if (titleLength + 2 > width - 2) {
    width = titleLength + 4;
  }

  const padding = Math.floor((width - 2 - titleLength) / 2);
  const paddedTitle = " ".repeat(padding) + title + " ".repeat(width - 2 - titleLength - padding);

  let topBorder = "";
  let middleLine = "";
  let bottomBorder = "";
  let color: string | null = null;

  if (useColor) {
    topBorder = "╔" + "═".repeat(width - 2) + "╗";
    middleLine = "║" + paddedTitle + "║";
    bottomBorder = "╚" + "═".repeat(width - 2) + "╝";
    color = Colors.BRIGHT_MAGENTA + Colors.BOLD;
  } else {
    topBorder = "+" + "-".repeat(width - 2) + "+";
    middleLine = "|" + paddedTitle + "|";
    bottomBorder = "+" + "-".repeat(width - 2) + "+";
    color = null;
  }

  logNewline(2);
  log(0, 1, 0, color, topBorder, useColor);
  log(0, 0, 0, color, middleLine, useColor);
  log(0, 0, 1, color, bottomBorder, useColor);
  logNewline(2);
}

export function logSectionHeader(title: string, indentationTabs: number = 0, colorMode: boolean | null = null): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const color = useColor ? Colors.HEADER + Colors.BOLD : null;
  const separator = "=".repeat(60);

  log(indentationTabs, 1, 0, color, separator, useColor);
  log(indentationTabs, 0, 0, color, title, useColor);
  log(indentationTabs, 0, 1, color, separator, useColor);
  logNewline();
}

export function logSubsection(title: string, indentationTabs: number = 0, colorMode: boolean | null = null): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const color = useColor ? Colors.BRIGHT_CYAN : null;
  const separator = "-".repeat(40);

  log(indentationTabs, 1, 0, color, separator, useColor);
  log(indentationTabs, 0, 0, color, title, useColor);
  log(indentationTabs, 0, 0, color, separator, useColor);
  logNewline();
}

export function logError(
  message: string,
  indentationTabs: number = 0,
  newlineBefore: number = 0,
  newlineAfter: number = 0,
  colorMode: boolean | null = null
): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const prefix = useColor ? "ERROR:" : "[ERROR]";
  const color = useColor ? Colors.ERROR + Colors.BOLD : null;
  log(indentationTabs, newlineBefore, newlineAfter, color, `${prefix} ${message}`, useColor);
}

export function logWarning(
  message: string,
  indentationTabs: number = 0,
  newlineBefore: number = 0,
  newlineAfter: number = 0,
  colorMode: boolean | null = null
): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const prefix = useColor ? "WARNING:" : "[WARNING]";
  const color = useColor ? Colors.WARNING + Colors.BOLD : null;
  log(indentationTabs, newlineBefore, newlineAfter, color, `${prefix} ${message}`, useColor);
}

export function logSuccess(
  message: string,
  indentationTabs: number = 0,
  newlineBefore: number = 0,
  newlineAfter: number = 0,
  colorMode: boolean | null = null
): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const prefix = useColor ? "SUCCESS:" : "[OK]";
  const color = useColor ? Colors.SUCCESS + Colors.BOLD : null;
  log(indentationTabs, newlineBefore, newlineAfter, color, `${prefix} ${message}`, useColor);
}

export function logInfo(
  message: string,
  indentationTabs: number = 0,
  newlineBefore: number = 0,
  newlineAfter: number = 0,
  colorMode: boolean | null = null
): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const prefix = useColor ? "INFO:" : "[INFO]";
  const color = useColor ? Colors.INFO : null;
  log(indentationTabs, newlineBefore, newlineAfter, color, `${prefix} ${message}`, useColor);
}

export function logDebug(
  message: string,
  indentationTabs: number = 2,
  newlineBefore: number = 0,
  newlineAfter: number = 0,
  colorMode: boolean | null = null
): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const prefix = useColor ? "DEBUG:" : "[DEBUG]";
  const color = useColor ? Colors.DEBUG + Colors.BOLD : null;
  log(indentationTabs, newlineBefore, newlineAfter, color, `${prefix} ${message}`, useColor);
}

export function logStep(
  stepNumber: number,
  totalSteps: number,
  description: string,
  indentationTabs: number = 0,
  colorMode: boolean | null = null
): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const color = useColor ? Colors.BRIGHT_BLUE + Colors.BOLD : null;
  logNewline();
  log(indentationTabs, 1, 0, color, `[Step ${stepNumber}/${totalSteps}] ${description}`, useColor);
  logNewline();
}

export function logFileSaved(
  filepath: string,
  indentationTabs: number = 1,
  colorMode: boolean | null = null
): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const prefix = "Saved:";
  const color = useColor ? Colors.SUCCESS : null;
  log(indentationTabs, 0, 0, color, `${prefix} ${filepath}`, useColor);
}

export function logFinalResult(
  success: boolean,
  message: string,
  width: number = 60,
  colorMode: boolean | null = null
): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const color = useColor ? (success ? Colors.SUCCESS + Colors.BOLD : Colors.ERROR + Colors.BOLD) : null;
  const separator = "=".repeat(width);

  logNewline(2);
  log(0, 1, 0, color, separator, useColor);
  if (success) {
    logSuccess(message, 0, 0, 1, useColor);
  } else {
    logError(message, 0, 0, 1, useColor);
  }
  log(0, 0, 1, color, separator, useColor);
  logNewline(2);
}

// Tree Structured Logger

export function logBanner(title: string, width: number = 54, colorMode: boolean | null = null): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const minWidth = title.length + 6;
  if (width < minWidth) {
    width = minWidth;
  }

  const lineDashes = "-".repeat(width - 2);
  const padded = `| [${title.toUpperCase()}]`.padEnd(width - 1);

  if (useColor) {
    const c = Colors.HEADER + Colors.BOLD;
    const r = Colors.RESET;
    const top = `${c}+${lineDashes}+${r}`;
    const mid = `${c}${padded}|${r}`;
    const bot = `${c}+${lineDashes}+${r}`;
    process.stdout.write(`\n${top}\n${mid}\n${bot}\n\n`);
  } else {
    const top = `+${lineDashes}+`;
    const mid = `${padded}|`;
    const bot = `+${lineDashes}+`;
    process.stdout.write(`\n${top}\n${mid}\n${bot}\n\n`);
  }
}

export function logSection(category: string, indentLevel: number = 0, colorMode: boolean | null = null): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const indent = "  ".repeat(indentLevel);
  const catStr = category.endsWith(":") ? category : `${category}:`;

  if (useColor) {
    const cTree = Colors.BRIGHT_CYAN;
    const cCat = Colors.BRIGHT_CYAN + Colors.BOLD;
    const r = Colors.RESET;
    process.stdout.write(`\n${indent}  ${cTree}|--${r} ${cCat}${catStr}${r}\n`);
  } else {
    process.stdout.write(`\n${indent}  |-- ${catStr}\n`);
  }
}

export function logDetail(label: any, value: any, indentLevel: number = 0, colorMode: boolean | null = null): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const indent = "  ".repeat(indentLevel + 1);
  const formattedLabel = String(label).padEnd(22);

  if (useColor) {
    const cTree = Colors.BRIGHT_CYAN;
    const cLabel = Colors.CYAN + Colors.BOLD;
    const cVal = Colors.BRIGHT_WHITE + Colors.BOLD;
    const r = Colors.RESET;
    process.stdout.write(`${indent}${cTree}+--${r} ${cLabel}${formattedLabel}${r} : ${cVal}${value}${r}\n`);
  } else {
    process.stdout.write(`${indent}+-- ${formattedLabel} : ${value}\n`);
  }
}

export function logDecision(action: string, detail: string | null = null, indentLevel: number = 0, colorMode: boolean | null = null): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const indent = "  ".repeat(indentLevel);

  if (useColor) {
    const cArrow = Colors.BRIGHT_YELLOW + Colors.BOLD;
    const cAction = Colors.BRIGHT_GREEN + Colors.BOLD;
    const cDetail = Colors.BRIGHT_WHITE;
    const r = Colors.RESET;

    if (detail !== null && detail !== undefined && String(detail).trim() !== "") {
      process.stdout.write(`\n${indent}  ${cArrow}+--> DECISION:${r} ${cAction}${action}${r} -> ${cDetail}${detail}${r}\n\n`);
    } else {
      process.stdout.write(`\n${indent}  ${cArrow}+--> DECISION:${r} ${cAction}${action}${r}\n\n`);
    }
  } else {
    if (detail !== null && detail !== undefined && String(detail).trim() !== "") {
      process.stdout.write(`\n${indent}  +--> DECISION: ${action} -> ${detail}\n\n`);
    } else {
      process.stdout.write(`\n${indent}  +--> DECISION: ${action}\n\n`);
    }
  }
}

export function logMessage(message: string, indentLevel: number = 0, colorMode: boolean | null = null): void {
  const useColor = colorMode === null || colorMode === undefined ? _colorMode : colorMode;
  const indent = "  ".repeat(indentLevel);

  if (useColor) {
    const cTree = Colors.BRIGHT_CYAN;
    const cMsg = Colors.BRIGHT_WHITE;
    const r = Colors.RESET;
    process.stdout.write(`${indent}${cTree}|--${r} ${cMsg}${message}${r}\n`);
  } else {
    process.stdout.write(`${indent}|-- ${message}\n`);
  }
}

export class StructuredLogger {
  static logBanner = logBanner;
  static logSection = logSection;
  static logDetail = logDetail;
  static logDecision = logDecision;
  static logMessage = logMessage;

  // Snake_case compatibility
  static log_banner = logBanner;
  static log_section = logSection;
  static log_detail = logDetail;
  static log_decision = logDecision;
  static log_message = logMessage;
}

export const AsciiLogger = StructuredLogger;
export const KeeperLogger = StructuredLogger;
