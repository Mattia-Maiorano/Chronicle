import { Size, Segment, VisualMeter } from "../core/geometry";
import { Renderable, RenderContext } from "./base";

interface BorderDef {
    tl: string; t: string; tr: string;
    l: string; r: string;
    bl: string; b: string; br: string;
}

const BORDERS: Record<string, BorderDef> = {
    ROUNDED: { tl: '╭', t: '─', tr: '╮', l: '│', r: '│', bl: '╰', b: '─', br: '╯' },
    DOUBLE: { tl: '╔', t: '═', tr: '╗', l: '║', r: '║', bl: '╚', b: '═', br: '╝' },
    SQUARE: { tl: '┌', t: '─', tr: '┐', l: '│', r: '│', bl: '└', b: '─', br: '┘' },
    CHRONICLE_TREE: { tl: '+', t: '-', tr: '+', l: '|', r: '|', bl: '+', b: '-', br: '+' },
    ASCII: { tl: '+', t: '-', tr: '+', l: '|', r: '|', bl: '+', b: '-', br: '+' },
};

export class Panel implements Renderable {
    static ROUNDED = "ROUNDED";
    static DOUBLE = "DOUBLE";
    static SQUARE = "SQUARE";
    static CHRONICLE_TREE = "CHRONICLE_TREE";

    constructor(
        public renderable: Renderable,
        public title: string | null = null,
        public subtitle: string | null = null,
        public borderStyle: string = Panel.SQUARE,
        public style: string = ""
    ) {}

    measure(ctx: RenderContext): Size {
        const innerCtx = new RenderContext(
            new Size(Math.max(0, ctx.bounds.width - 2), Math.max(0, ctx.bounds.height - 2)),
            ctx.colorMode,
            ctx.asciiMode
        );
        const innerSize = this.renderable.measure(innerCtx);
        return new Size(innerSize.width + 2, innerSize.height + 2);
    }

    render(bounds: Size, ctx: RenderContext): Segment[][] {
        if (bounds.width < 2 || bounds.height < 2) return [];

        let border = BORDERS[this.borderStyle] || BORDERS.ASCII;
        if (ctx.asciiMode || !ctx.colorMode) {
            border = BORDERS.ASCII;
        }

        const style = ctx.colorMode ? this.style : null;
        const lines: Segment[][] = [];

        // Top
        const topRow: Segment[] = [new Segment(border.tl, style)];
        const topSpace = bounds.width - 2;

        if (this.title && topSpace > 0) {
            let titleText = ctx.asciiMode ? ` [${this.title}] ` : ` ${this.title} `;
            let titleLen = VisualMeter.measure(titleText);
            if (titleLen > topSpace) {
                titleText = titleText.substring(0, topSpace);
                titleLen = topSpace;
            }

            let dashBefore = 1;
            let dashAfter = topSpace - titleLen - dashBefore;
            if (dashAfter < 0) {
                dashBefore += dashAfter;
                dashAfter = 0;
            }

            if (dashBefore > 0) topRow.push(new Segment(border.t.repeat(dashBefore), style));
            topRow.push(new Segment(titleText, style));
            if (dashAfter > 0) topRow.push(new Segment(border.t.repeat(dashAfter), style));
        } else {
            topRow.push(new Segment(border.t.repeat(topSpace), style));
        }
        topRow.push(new Segment(border.tr, style));
        lines.push(topRow);

        // Mid
        const innerBounds = new Size(bounds.width - 2, bounds.height - 2);
        const innerCtx = new RenderContext(innerBounds, ctx.colorMode, ctx.asciiMode);
        const contentLines = this.renderable.render(innerBounds, innerCtx);

        for (let i = 0; i < innerBounds.height; i++) {
            const midRow: Segment[] = [new Segment(border.l, style)];
            if (i < contentLines.length) {
                const cLine = contentLines[i];
                let cLen = 0;
                for (const seg of cLine) cLen += VisualMeter.measure(seg.text);
                midRow.push(...cLine);
                const pad = innerBounds.width - cLen;
                if (pad > 0) midRow.push(new Segment(" ".repeat(pad)));
            } else {
                midRow.push(new Segment(" ".repeat(innerBounds.width)));
            }
            midRow.push(new Segment(border.r, style));
            lines.push(midRow);
        }

        // Bottom
        const botRow: Segment[] = [new Segment(border.bl, style)];
        const botSpace = bounds.width - 2;

        if (this.subtitle && botSpace > 0) {
            let subText = ` ${this.subtitle} `;
            let subLen = VisualMeter.measure(subText);
            if (subLen > botSpace) {
                subText = subText.substring(0, botSpace);
                subLen = botSpace;
            }

            let dashAfter = 1;
            let dashBefore = botSpace - subLen - dashAfter;
            if (dashBefore < 0) {
                dashAfter += dashBefore;
                dashBefore = 0;
            }

            if (dashBefore > 0) botRow.push(new Segment(border.b.repeat(dashBefore), style));
            botRow.push(new Segment(subText, style));
            if (dashAfter > 0) botRow.push(new Segment(border.b.repeat(dashAfter), style));
        } else {
            botRow.push(new Segment(border.b.repeat(botSpace), style));
        }
        botRow.push(new Segment(border.br, style));
        lines.push(botRow);

        return lines;
    }
}
