from typing import List, Dict, Optional, Any, NamedTuple
from chronicle.core.geometry import Size, Segment, VisualMeter
from chronicle.layout.base import Renderable, RenderContext
from chronicle.logger import Colors


class Column(NamedTuple):
    header: str
    style: str = ""
    align: str = "left"
    min_width: int = 0
    max_width: Optional[int] = None
    flex: int = 1


class LiveTable:
    def __init__(self, columns: List[Column]):
        self.columns = columns
        self.rows: List[Dict[str, Any]] = []
        self._row_ids: List[str] = []
        self.dirty = True

    def add_row(self, row_id: str, cells: List[Any]):
        self.rows.append({"id": row_id, "cells": cells})
        self._row_ids.append(row_id)
        self.dirty = True

    def update_row(self, row_id: str, cells: List[Any]):
        if row_id in self._row_ids:
            idx = self._row_ids.index(row_id)
            self.rows[idx]["cells"] = cells
            self.dirty = True

    def update_cell(self, row_id: str, col_index: int, value: Any):
        if row_id in self._row_ids:
            idx = self._row_ids.index(row_id)
            if col_index < len(self.rows[idx]["cells"]):
                self.rows[idx]["cells"][col_index] = value
                self.dirty = True

    def measure(self, ctx: RenderContext) -> Size:
        # height = headers + separator + rows
        return Size(width=ctx.bounds.width, height=2 + len(self.rows))

    def render(self, bounds: Size, ctx: RenderContext) -> List[List[Segment]]:
        self.dirty = False
        if bounds.width <= 0 or bounds.height <= 0:
            return []

        col_count = len(self.columns)
        if col_count == 0:
            return []

        # 1. Distribute widths
        widths = [max(col.min_width, VisualMeter.measure(col.header) + 2) for col in self.columns]

        # Consider available width
        available = bounds.width - sum(widths)
        if available > 0:
            flex_sum = sum(col.flex for col in self.columns)
            if flex_sum > 0:
                unit = available / flex_sum
                for i, col in enumerate(self.columns):
                    add = int(col.flex * unit)
                    if col.max_width and widths[i] + add > col.max_width:
                        add = col.max_width - widths[i]
                    widths[i] += add
                    available -= add

                # Assign remainder to first flex
                if available > 0:
                    for i, col in enumerate(self.columns):
                        if col.flex > 0:
                            if not col.max_width or widths[i] + available <= col.max_width:
                                widths[i] += available
                                break

        lines = []

        def format_cell(text: str, width: int, align: str, style: str) -> Segment:
            text_len = VisualMeter.measure(text)
            if text_len > width:
                clean = VisualMeter.strip_ansi(text)
                text = clean[:max(0, width - 1)] + ("…" if width > 0 else "")
                text_len = width

            pad = width - text_len
            pad_left, pad_right = 0, 0

            if align == "center":
                pad_left = pad // 2
                pad_right = pad - pad_left
            elif align == "right":
                pad_left = pad
            else:
                pad_right = pad

            display = (" " * pad_left) + text + (" " * pad_right)
            return Segment(display, style if ctx.color_mode else None)

        # Header
        header_row = []
        for i, col in enumerate(self.columns):
            header_row.append(format_cell(col.header, widths[i], col.align, Colors.BRIGHT_CYAN + Colors.BOLD if ctx.color_mode else ""))
        lines.append(header_row)

        # Rule
        sep_char = "─" if ctx.color_mode and not ctx.ascii_mode else "-"
        sep_row = [Segment(sep_char * bounds.width, Colors.BRIGHT_CYAN if ctx.color_mode else None)]
        lines.append(sep_row)

        # Rows
        max_rows = bounds.height - 2
        for r_idx, row_data in enumerate(self.rows[:max_rows]):
            row_segments = []
            cells = row_data["cells"]
            for i, col in enumerate(self.columns):
                val = cells[i] if i < len(cells) else ""
                if hasattr(val, "render"):
                    # For simplicity in this mock, we just measure and grab text if it has a quick text prop, but proper layout engine would recurse.
                    # For Badge and Progress we can call render
                    c_ctx = RenderContext(Size(widths[i], 1), ctx.color_mode, ctx.ascii_mode)
                    res = val.render(Size(widths[i], 1), c_ctx)
                    if res and res[0]:
                        # combine segments into single string for our simple format_cell
                        val_str = ""
                        val_style = res[0][0].style if ctx.color_mode else ""
                        for s in res[0]:
                             val_str += s.text
                        row_segments.append(Segment(val_str, val_style))
                        continue
                val = str(val)
                row_segments.append(format_cell(val, widths[i], col.align, col.style if ctx.color_mode else ""))
            lines.append(row_segments)

        return lines
