import { Size, Segment, VisualMeter } from "../core/geometry";

export class Canvas {
    public buffer: Array<Array<{ char: string; style: string }>>;

    constructor(public size: Size) {
        this.buffer = Array.from({ length: size.height }, () =>
            Array.from({ length: size.width }, () => ({ char: " ", style: "" }))
        );
    }

    clear() {
        for (let y = 0; y < this.size.height; y++) {
            for (let x = 0; x < this.size.width; x++) {
                this.buffer[y][x] = { char: " ", style: "" };
            }
        }
    }

    blit(x: number, y: number, segments: Segment[]) {
        if (y < 0 || y >= this.size.height) return;

        let cx = x;
        for (const seg of segments) {
            const cleanText = VisualMeter.stripAnsi(seg.text);
            for (const char of cleanText) {
                if (cx >= this.size.width) break;
                if (cx >= 0) {
                    this.buffer[y][cx] = { char, style: seg.style || "" };
                }
                cx++;
            }
        }
    }

    renderToStrings(): string[] {
        const lines: string[] = [];
        for (let y = 0; y < this.size.height; y++) {
            let line = "";
            let currentStyle = "";
            for (let x = 0; x < this.size.width; x++) {
                const { char, style } = this.buffer[y][x];
                if (style !== currentStyle) {
                    if (currentStyle) line += "\x1b[0m";
                    if (style) line += style;
                    currentStyle = style;
                }
                line += char;
            }
            if (currentStyle) line += "\x1b[0m";
            lines.push(line);
        }
        return lines;
    }
}
