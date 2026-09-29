import { Size, Segment } from "../core/geometry";

export class RenderContext {
    constructor(
        public bounds: Size,
        public colorMode: boolean,
        public asciiMode: boolean
    ) {}
}

export interface Renderable {
    measure(ctx: RenderContext): Size;
    render(bounds: Size, ctx: RenderContext): Segment[][];
}
