import { Size, Segment, VisualMeter } from "../core/geometry";
import { Renderable, RenderContext } from "./base";

export class Fixed {
    constructor(public size: number) {}
}

export class Flex {
    constructor(public weight: number = 1) {}
}

export class Ratio {
    constructor(public percentage: number) {}
}

export type Policy = Fixed | Flex | Ratio;

export class FlexSplitter implements Renderable {
    static HORIZONTAL = "horizontal";
    static VERTICAL = "vertical";

    public children: Array<{ child: Renderable, policy: Policy }> = [];

    constructor(public direction: string = FlexSplitter.HORIZONTAL) {}

    add(child: Renderable, policy: Policy = new Flex(1)) {
        this.children.push({ child, policy });
    }

    measure(ctx: RenderContext): Size {
        return ctx.bounds;
    }

    render(bounds: Size, ctx: RenderContext): Segment[][] {
        if (this.children.length === 0) return [];

        const totalSize = this.direction === FlexSplitter.HORIZONTAL ? bounds.width : bounds.height;
        const sizes = new Array(this.children.length).fill(0);
        let remainingSize = totalSize;

        // Fixed and Ratio
        this.children.forEach((item, i) => {
            if (item.policy instanceof Fixed) {
                sizes[i] = item.policy.size;
                remainingSize -= sizes[i];
            } else if (item.policy instanceof Ratio) {
                sizes[i] = Math.floor(totalSize * item.policy.percentage);
                remainingSize -= sizes[i];
            }
        });

        // Flex
        let flexSum = 0;
        this.children.forEach(item => {
            if (item.policy instanceof Flex) flexSum += item.policy.weight;
        });

        if (flexSum > 0 && remainingSize > 0) {
            const flexUnit = remainingSize / flexSum;
            this.children.forEach((item, i) => {
                if (item.policy instanceof Flex) {
                    const alloc = Math.floor(item.policy.weight * flexUnit);
                    sizes[i] = alloc;
                    remainingSize -= alloc;
                }
            });

            for (let i = 0; i < this.children.length; i++) {
                if (this.children[i].policy instanceof Flex && remainingSize > 0) {
                    sizes[i] += remainingSize;
                    remainingSize = 0;
                    break;
                }
            }
        }

        const renderedChildren: Array<{ cBounds: Size, cLines: Segment[][] }> = [];
        this.children.forEach((item, i) => {
            const cBounds = this.direction === FlexSplitter.HORIZONTAL
                ? new Size(sizes[i], bounds.height)
                : new Size(bounds.width, sizes[i]);

            const cCtx = new RenderContext(cBounds, ctx.colorMode, ctx.asciiMode);
            const cLines = item.child.render(cBounds, cCtx);
            renderedChildren.push({ cBounds, cLines });
        });

        const lines: Segment[][] = [];
        if (this.direction === FlexSplitter.HORIZONTAL) {
            for (let y = 0; y < bounds.height; y++) {
                const row: Segment[] = [];
                for (const rc of renderedChildren) {
                    if (y < rc.cLines.length) {
                        row.push(...rc.cLines[y]);
                        let cLen = 0;
                        for (const seg of rc.cLines[y]) cLen += VisualMeter.measure(seg.text);
                        const pad = rc.cBounds.width - cLen;
                        if (pad > 0) row.push(new Segment(" ".repeat(pad)));
                    } else {
                        row.push(new Segment(" ".repeat(rc.cBounds.width)));
                    }
                }
                lines.push(row);
            }
        } else {
            for (const rc of renderedChildren) {
                for (let y = 0; y < rc.cBounds.height; y++) {
                    if (y < rc.cLines.length) {
                        lines.push(rc.cLines[y]);
                    } else {
                        lines.push([new Segment(" ".repeat(bounds.width))]);
                    }
                }
            }
        }

        return lines;
    }
}

export const Layout = FlexSplitter;
