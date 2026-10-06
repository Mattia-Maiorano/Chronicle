import { Size, Segment, VisualMeter } from "../core/geometry";
import { Renderable, RenderContext } from "./base";

export class Rule implements Renderable {
    constructor(
        public title: string | null = null,
        public style: string = "",
        public character: string = "─"
    ) {}

    measure(ctx: RenderContext): Size {
        return new Size(ctx.bounds.width, 1);
    }

    render(bounds: Size, ctx: RenderContext): Segment[][] {
        if (bounds.width <= 0 || bounds.height <= 0) return [];

        const char = (ctx.colorMode && !ctx.asciiMode) ? this.character : "-";
        const style = ctx.colorMode ? this.style : null;

        if (!this.title) {
            return [[new Segment(char.repeat(bounds.width), style)]];
        }

        const titleText = ` ${this.title} `;
        const titleLen = VisualMeter.measure(titleText);

        if (titleLen >= bounds.width) {
            return [[new Segment(titleText.substring(0, bounds.width), style)]];
        }

        const leftDashLen = Math.floor((bounds.width - titleLen) / 2);
        const rightDashLen = bounds.width - titleLen - leftDashLen;

        const row: Segment[] = [];
        if (leftDashLen > 0) row.push(new Segment(char.repeat(leftDashLen), style));
        row.push(new Segment(titleText, style));
        if (rightDashLen > 0) row.push(new Segment(char.repeat(rightDashLen), style));

        return [row];
    }
}
