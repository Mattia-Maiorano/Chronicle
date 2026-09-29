import { Size, TerminalMetrics } from "../core/geometry";
import { Renderable, RenderContext } from "../layout/base";
import { Canvas } from "./canvas";

export class LiveEngine {
    static INLINE = "inline";
    static ALTERNATE_SCREEN = "alternate_screen";

    public running = false;
    private timer: NodeJS.Timeout | null = null;
    public canvas: Canvas | null = null;
    private renderedLines = 0;

    constructor(
        public renderable: Renderable,
        public mode: string = LiveEngine.INLINE,
        public refreshRateHz: number = 10.0,
        public colorMode: boolean = true,
        public asciiMode: boolean = false
    ) {}

    start() {
        if (this.running) return;
        this.running = true;

        if (this.colorMode) {
            process.stdout.write("\x1b[?25l"); // Hide cursor
        }
        if (this.mode === LiveEngine.ALTERNATE_SCREEN && this.colorMode) {
            process.stdout.write("\x1b[?1049h");
        }

        if (!this.colorMode) {
            this.refresh();
        }

        const handleResize = () => this.refresh();
        process.stdout.on('resize', handleResize);

        const handleExit = () => {
            this.stop();
            process.exit(0);
        };
        process.on('SIGINT', handleExit);
        process.on('SIGTERM', handleExit);

        const intervalMs = 1000 / this.refreshRateHz;

        if (this.colorMode) {
            this.timer = setInterval(() => this.refresh(), intervalMs);
        } else {
            this.timer = setInterval(() => this.refresh(), 5000);
        }
    }

    stop() {
        if (!this.running) return;
        this.running = false;

        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }

        if (this.colorMode) {
            if (this.mode === LiveEngine.ALTERNATE_SCREEN) {
                process.stdout.write("\x1b[?1049l");
            }
            process.stdout.write("\x1b[?25h"); // Show cursor
        }

        if (!this.colorMode) {
            this.refresh();
        }
    }

    refresh() {
        let size = TerminalMetrics.getSize();

        if (this.mode === LiveEngine.INLINE) {
            const ctx = new RenderContext(size, this.colorMode, this.asciiMode);
            const measuredSize = this.renderable.measure(ctx);
            const height = Math.min(measuredSize.height, size.height - 1);
            size = new Size(size.width, height);
        }

        if (!this.canvas || this.canvas.size.width !== size.width || this.canvas.size.height !== size.height) {
            this.canvas = new Canvas(size);
        }

        this.canvas.clear();

        const ctx = new RenderContext(size, this.colorMode, this.asciiMode);
        const lines = this.renderable.render(size, ctx);

        for (let y = 0; y < lines.length && y < size.height; y++) {
            this.canvas.blit(0, y, lines[y]);
        }

        const renderedStrings = this.canvas.renderToStrings();

        if (this.colorMode) {
            if (this.mode === LiveEngine.INLINE && this.renderedLines > 0) {
                process.stdout.write(`\x1b[${this.renderedLines}A`);
            }

            for (const rStr of renderedStrings) {
                process.stdout.write("\x1b[2K"); // Clear line
                process.stdout.write(rStr + "\n");
            }
            this.renderedLines = renderedStrings.length;
        } else {
            console.log("\n--- Live Snapshot ---");
            renderedStrings.forEach(s => console.log(s));
            console.log("---------------------\n");
        }
    }
}
