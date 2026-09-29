export class Size {
    constructor(public width: number, public height: number) {}
}

export class Point {
    constructor(public x: number, public y: number) {}
}

export class Segment {
    constructor(public text: string, public style?: string | null) {}
}

export class VisualMeter {
    // Regex to match ANSI SGR escape sequences
    private static _ANSI_RE = /\x1b\[[0-9;]*[mK]/g;

    /**
     * Removes all ANSI escape sequences from a string.
     */
    static stripAnsi(text: string): string {
        return text.replace(this._ANSI_RE, '');
    }

    /**
     * Returns the visual length of a string, ignoring ANSI escape sequences.
     */
    static measure(text: string): number {
        return this.stripAnsi(text).length;
    }
}

export class TerminalMetrics {
    /**
     * Returns the current terminal size.
     */
    static getSize(fallbackWidth = 80, fallbackHeight = 24): Size {
        if (process && process.stdout) {
            return new Size(
                process.stdout.columns || fallbackWidth,
                process.stdout.rows || fallbackHeight
            );
        }
        return new Size(fallbackWidth, fallbackHeight);
    }
}
