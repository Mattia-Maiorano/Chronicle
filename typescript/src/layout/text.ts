import { Size, Segment, VisualMeter } from "../core/geometry";
import { Renderable, RenderContext } from "./base";

export class Text implements Renderable {
    static LEFT = "left";
    static CENTER = "center";
    static RIGHT = "right";

    constructor(
        public text: string,
        public style: string = "",
        public align: string = Text.LEFT,
        public truncateStr: string = "..."
    ) {}

    measure(ctx: RenderContext): Size {
        return new Size(VisualMeter.measure(this.text), 1);
    }

    render(bounds: Size, ctx: RenderContext): Segment[][] {
        if (bounds.width <= 0 || bounds.height <= 0) return [];

        let textLen = VisualMeter.measure(this.text);
        let displayText = this.text;

        if (textLen > bounds.width) {
            if (bounds.width >= this.truncateStr.length) {
                const cleanText = VisualMeter.stripAnsi(this.text);
                const allowedLen = bounds.width - this.truncateStr.length;
                displayText = cleanText.substring(0, allowedLen) + this.truncateStr;
                textLen = bounds.width;
            } else {
                displayText = "";
                textLen = 0;
            }
        }

        const padTotal = bounds.width - textLen;
        let padLeft = 0, padRight = 0;

        if (this.align === Text.CENTER) {
            padLeft = Math.floor(padTotal / 2);
            padRight = padTotal - padLeft;
        } else if (this.align === Text.RIGHT) {
            padLeft = padTotal;
        } else {
            padRight = padTotal;
        }

        const styledSegment = new Segment(displayText, ctx.colorMode ? this.style : null);
        const row: Segment[] = [];

        if (padLeft > 0) row.push(new Segment(" ".repeat(padLeft)));
        row.push(styledSegment);
        if (padRight > 0) row.push(new Segment(" ".repeat(padRight)));

        return [row];
    }
}
