import { Size, Segment, VisualMeter } from "../core/geometry";
import { Renderable, RenderContext } from "../layout/base";

export class Badge implements Renderable {
    static STYLES: Record<string, string> = {
        RUNNING: "\x1b[94m",
        PASS: "\x1b[92m",
        ERROR: "\x1b[91m",
        WARN: "\x1b[93m",
        DEFAULT: "\x1b[97m",
    };

    public status: string;

    constructor(public text: string, status: string = "DEFAULT") {
        this.status = status.toUpperCase();
    }

    measure(ctx: RenderContext): Size {
        return new Size(VisualMeter.measure(this.text) + 2, 1);
    }

    render(bounds: Size, ctx: RenderContext): Segment[][] {
        if (bounds.width <= 0 || bounds.height <= 0) return [];

        const style = ctx.colorMode ? (Badge.STYLES[this.status] || Badge.STYLES["DEFAULT"]) : "";
        let text = ` ${this.text} `;

        if (VisualMeter.measure(text) > bounds.width) {
            text = text.substring(0, bounds.width);
        }

        const pad = bounds.width - VisualMeter.measure(text);
        const row: Segment[] = [];

        if (style) {
            row.push(new Segment(text, style + "\x1b[1m"));
        } else {
            row.push(new Segment(`[${this.text}]`));
        }

        if (pad > 0) row.push(new Segment(" ".repeat(pad)));

        return [row];
    }
}
