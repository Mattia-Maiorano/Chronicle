import { Size, Segment, VisualMeter } from "../core/geometry";
import { Renderable, RenderContext } from "../layout/base";

export class RollingLogStream implements Renderable {
    public buffer: string[] = [];
    public dirty = true;

    constructor(public maxLines: number = 100) {}

    append(text: string) {
        this.buffer.push(text);
        if (this.buffer.length > this.maxLines) {
            this.buffer.shift();
        }
        this.dirty = true;
    }

    measure(ctx: RenderContext): Size {
        return new Size(ctx.bounds.width, Math.min(this.buffer.length, ctx.bounds.height));
    }

    render(bounds: Size, ctx: RenderContext): Segment[][] {
        this.dirty = false;
        if (bounds.width <= 0 || bounds.height <= 0) return [];

        const lines: Segment[][] = [];
        const startIdx = Math.max(0, this.buffer.length - bounds.height);
        const displayLines = this.buffer.slice(startIdx);

        for (const line of displayLines) {
            if (VisualMeter.measure(line) > bounds.width) {
                const clean = VisualMeter.stripAnsi(line);
                lines.push([new Segment(clean.substring(0, bounds.width))]);
            } else {
                lines.push([new Segment(line)]);
            }
        }

        for (let i = 0; i < bounds.height - displayLines.length; i++) {
            lines.push([new Segment(" ".repeat(bounds.width))]);
        }

        return lines;
    }
}
