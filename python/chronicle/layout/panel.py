from typing import List, Optional, Tuple, NamedTuple
from chronicle.core.geometry import Size, Segment, VisualMeter
from chronicle.layout.base import Renderable, RenderContext
from chronicle.logger import Colors

class Border(NamedTuple):
    top_left: str
    top: str
    top_right: str
    left: str
    right: str
    bottom_left: str
    bottom: str
    bottom_right: str

BORDERS = {
    "ROUNDED": Border('╭', '─', '╮', '│', '│', '╰', '─', '╯'),
    "DOUBLE": Border('╔', '═', '╗', '║', '║', '╚', '═', '╝'),
    "SQUARE": Border('┌', '─', '┐', '│', '│', '└', '─', '┘'),
    "CHRONICLE_TREE": Border('+', '-', '+', '|', '|', '+', '-', '+'),
    "ASCII": Border('+', '-', '+', '|', '|', '+', '-', '+'),
}

class Panel:
    ROUNDED = "ROUNDED"
    DOUBLE = "DOUBLE"
    SQUARE = "SQUARE"
    CHRONICLE_TREE = "CHRONICLE_TREE"

    def __init__(self, renderable: Renderable, title: Optional[str] = None, subtitle: Optional[str] = None, border_style: str = SQUARE, style: str = ""):
        self.renderable = renderable
        self.title = title
        self.subtitle = subtitle
        self.border_style = border_style
        self.style = style

    def measure(self, ctx: RenderContext) -> Size:
        # Subtract border size from bounds to measure inner
        inner_ctx = RenderContext(
            Size(max(0, ctx.bounds.width - 2), max(0, ctx.bounds.height - 2)),
            ctx.color_mode,
            ctx.ascii_mode
        )
        inner_size = self.renderable.measure(inner_ctx)
        return Size(inner_size.width + 2, inner_size.height + 2)

    def render(self, bounds: Size, ctx: RenderContext) -> List[List[Segment]]:
        if bounds.width < 2 or bounds.height < 2:
            return []

        border = BORDERS.get(self.border_style, BORDERS["ASCII"])
        if ctx.ascii_mode or not ctx.color_mode:
            border = BORDERS["ASCII"]

        style = self.style if ctx.color_mode else None

        lines: List[List[Segment]] = []

        # Top border
        top_row = []
        top_row.append(Segment(border.top_left, style))

        top_space = bounds.width - 2
        if self.title and top_space > 0:
            title_text = f" [{self.title}] " if ctx.ascii_mode else f" {self.title} "
            title_len = VisualMeter.measure(title_text)
            if title_len > top_space:
                title_text = title_text[:top_space]
                title_len = top_space

            # Left align title after 1 char
            dash_before = 1
            dash_after = top_space - title_len - dash_before
            if dash_after < 0:
                dash_before += dash_after
                dash_after = 0

            if dash_before > 0:
                top_row.append(Segment(border.top * dash_before, style))
            top_row.append(Segment(title_text, style))
            if dash_after > 0:
                top_row.append(Segment(border.top * dash_after, style))
        else:
            top_row.append(Segment(border.top * top_space, style))

        top_row.append(Segment(border.top_right, style))
        lines.append(top_row)

        # Middle Content
        inner_bounds = Size(bounds.width - 2, bounds.height - 2)
        inner_ctx = RenderContext(inner_bounds, ctx.color_mode, ctx.ascii_mode)

        content_lines = self.renderable.render(inner_bounds, inner_ctx)

        for i in range(inner_bounds.height):
            mid_row = [Segment(border.left, style)]
            if i < len(content_lines):
                # We need to pad the content line to inner_bounds.width
                c_line = content_lines[i]
                c_len = sum(VisualMeter.measure(seg.text) for seg in c_line)
                mid_row.extend(c_line)
                pad = inner_bounds.width - c_len
                if pad > 0:
                    mid_row.append(Segment(" " * pad))
            else:
                mid_row.append(Segment(" " * inner_bounds.width))
            mid_row.append(Segment(border.right, style))
            lines.append(mid_row)

        # Bottom border
        bot_row = []
        bot_row.append(Segment(border.bottom_left, style))

        bot_space = bounds.width - 2
        if self.subtitle and bot_space > 0:
            sub_text = f" {self.subtitle} "
            sub_len = VisualMeter.measure(sub_text)
            if sub_len > bot_space:
                sub_text = sub_text[:bot_space]
                sub_len = bot_space

            dash_after = 1
            dash_before = bot_space - sub_len - dash_after
            if dash_before < 0:
                dash_after += dash_before
                dash_before = 0

            if dash_before > 0:
                bot_row.append(Segment(border.bottom * dash_before, style))
            bot_row.append(Segment(sub_text, style))
            if dash_after > 0:
                bot_row.append(Segment(border.bottom * dash_after, style))
        else:
            bot_row.append(Segment(border.bottom * bot_space, style))

        bot_row.append(Segment(border.bottom_right, style))
        lines.append(bot_row)

        return lines
