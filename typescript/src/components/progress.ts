import { Size, Segment, VisualMeter } from "../core/geometry";
import { Renderable, RenderContext } from "../layout/base";

export class ProgressBar implements Renderable {
    static SPINNERS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];
    public dirty = true;

    constructor(
        public total: number = 100.0,
        public current: number = 0.0,
        public label: string = ""
    ) {}

    update(current: number) {
        this.current = current;
        this.dirty = true;
    }

    measure(ctx: RenderContext): Size {
        return new Size(ctx.bounds.width, 1);
    }

    render(bounds: Size, ctx: RenderContext): Segment[][] {
        this.dirty = false;
        if (bounds.width <= 0 || bounds.height <= 0) return [];

        const progress = Math.min(1.0, Math.max(0.0, this.total > 0 ? this.current / this.total : 0));
        const percentStr = `${Math.floor(progress * 100)}%`;

        const spinnerIdx = Math.floor(Date.now() / 100) % ProgressBar.SPINNERS.length;
        const spinner = (ctx.colorMode && !ctx.asciiMode) ? ProgressBar.SPINNERS[spinnerIdx] : "";

        const labelPart = spinner ? `${spinner} ${this.label}`.trim() : this.label;

        const metaLen = VisualMeter.measure(labelPart) + 1 + percentStr.length + 4;
        const barWidth = Math.max(0, bounds.width - metaLen);

        const filledLen = Math.floor(barWidth * progress);
        const emptyLen = barWidth - filledLen;

        const barChar = (ctx.colorMode && !ctx.asciiMode) ? "█" : "=";
        const emptyChar = (ctx.colorMode && !ctx.asciiMode) ? "░" : " ";

        const bar = barChar.repeat(filledLen) + emptyChar.repeat(emptyLen);

        const row: Segment[] = [];
        if (labelPart) row.push(new Segment(`${labelPart} `));

        row.push(new Segment("[", ctx.colorMode ? "\x1b[90m" : null));
        row.push(new Segment(bar, ctx.colorMode ? "\x1b[92m" : null));
        row.push(new Segment("] ", ctx.colorMode ? "\x1b[90m" : null));

        row.push(new Segment(percentStr.padStart(4, ' '), ctx.colorMode ? "\x1b[97m" : null));

        let cLen = 0;
        for (const s of row) cLen += VisualMeter.measure(s.text);
        const pad = bounds.width - cLen;
        if (pad > 0) row.push(new Segment(" ".repeat(pad)));

        return [row];
    }
}
