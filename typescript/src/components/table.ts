import { Size, Segment, VisualMeter } from "../core/geometry";
import { Renderable, RenderContext } from "../layout/base";

export interface Column {
    header: string;
    style?: string;
    align?: "left" | "center" | "right";
    minWidth?: number;
    maxWidth?: number | null;
    flex?: number;
}

export class LiveTable implements Renderable {
    public columns: Required<Column>[];
    public rows: Array<{ id: string, cells: any[] }> = [];
    private rowIds: string[] = [];
    public dirty = true;

    constructor(columns: Column[]) {
        this.columns = columns.map(c => ({
            header: c.header,
            style: c.style || "",
            align: c.align || "left",
            minWidth: c.minWidth || 0,
            maxWidth: c.maxWidth || null,
            flex: c.flex !== undefined ? c.flex : 1
        }));
    }

    addRow(rowId: string, cells: any[]) {
        this.rows.push({ id: rowId, cells });
        this.rowIds.push(rowId);
        this.dirty = true;
    }

    updateRow(rowId: string, cells: any[]) {
        const idx = this.rowIds.indexOf(rowId);
        if (idx !== -1) {
            this.rows[idx].cells = cells;
            this.dirty = true;
        }
    }

    updateCell(rowId: string, colIndex: number, value: any) {
        const idx = this.rowIds.indexOf(rowId);
        if (idx !== -1 && colIndex < this.rows[idx].cells.length) {
            this.rows[idx].cells[colIndex] = value;
            this.dirty = true;
        }
    }

    measure(ctx: RenderContext): Size {
        return new Size(ctx.bounds.width, 2 + this.rows.length);
    }

    render(bounds: Size, ctx: RenderContext): Segment[][] {
        this.dirty = false;
        if (bounds.width <= 0 || bounds.height <= 0) return [];
        if (this.columns.length === 0) return [];

        const widths = this.columns.map(c => Math.max(c.minWidth, VisualMeter.measure(c.header) + 2));
        let available = bounds.width - widths.reduce((a, b) => a + b, 0);

        if (available > 0) {
            const flexSum = this.columns.reduce((sum, c) => sum + c.flex, 0);
            if (flexSum > 0) {
                const unit = available / flexSum;
                for (let i = 0; i < this.columns.length; i++) {
                    const col = this.columns[i];
                    let add = Math.floor(col.flex * unit);
                    if (col.maxWidth && widths[i] + add > col.maxWidth) {
                        add = col.maxWidth - widths[i];
                    }
                    widths[i] += add;
                    available -= add;
                }

                if (available > 0) {
                    for (let i = 0; i < this.columns.length; i++) {
                        const col = this.columns[i];
                        if (col.flex > 0 && (!col.maxWidth || widths[i] + available <= col.maxWidth)) {
                            widths[i] += available;
                            break;
                        }
                    }
                }
            }
        }

        const lines: Segment[][] = [];

        const formatCell = (text: string, width: number, align: string, style: string): Segment => {
            let textLen = VisualMeter.measure(text);
            if (textLen > width) {
                const clean = VisualMeter.stripAnsi(text);
                text = clean.substring(0, Math.max(0, width - 1)) + (width > 0 ? "…" : "");
                textLen = width;
            }

            const pad = width - textLen;
            let padLeft = 0, padRight = 0;

            if (align === "center") {
                padLeft = Math.floor(pad / 2);
                padRight = pad - padLeft;
            } else if (align === "right") {
                padLeft = pad;
            } else {
                padRight = pad;
            }

            const display = " ".repeat(padLeft) + text + " ".repeat(padRight);
            return new Segment(display, ctx.colorMode ? style : null);
        };

        // Header
        const headerRow: Segment[] = [];
        this.columns.forEach((col, i) => {
            headerRow.push(formatCell(col.header, widths[i], col.align, ctx.colorMode ? "\x1b[96m\x1b[1m" : ""));
        });
        lines.push(headerRow);

        // Sep
        const sepChar = (ctx.colorMode && !ctx.asciiMode) ? "─" : "-";
        lines.push([new Segment(sepChar.repeat(bounds.width), ctx.colorMode ? "\x1b[96m" : null)]);

        // Rows
        const maxRows = bounds.height - 2;
        for (let rIdx = 0; rIdx < Math.min(this.rows.length, maxRows); rIdx++) {
            const rowData = this.rows[rIdx];
            const rowSegments: Segment[] = [];
            const cells = rowData.cells;

            this.columns.forEach((col, i) => {
                let val = i < cells.length ? cells[i] : "";

                if (val && typeof val.render === "function") {
                    const cCtx = new RenderContext(new Size(widths[i], 1), ctx.colorMode, ctx.asciiMode);
                    const res = val.render(new Size(widths[i], 1), cCtx);
                    if (res && res[0]) {
                        let valStr = "";
                        let valStyle = ctx.colorMode ? res[0][0].style : null;
                        for (const s of res[0]) valStr += s.text;
                        rowSegments.push(new Segment(valStr, valStyle));
                        return;
                    }
                }

                rowSegments.push(formatCell(String(val), widths[i], col.align, ctx.colorMode ? col.style : ""));
            });
            lines.push(rowSegments);
        }

        return lines;
    }
}
