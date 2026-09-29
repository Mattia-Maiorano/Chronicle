from typing import List
from chronicle.core.geometry import Size, Segment, VisualMeter
from chronicle.layout.base import Renderable, RenderContext
from chronicle.logger import Colors


class Text:
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"

    def __init__(self, text: str, style: str = "", align: str = LEFT, truncate_str: str = "..."):
        self.text = text
        self.style = style
        self.align = align
        self.truncate_str = truncate_str

    def measure(self, ctx: RenderContext) -> Size:
        width = VisualMeter.measure(self.text)
        return Size(width=width, height=1)

    def render(self, bounds: Size, ctx: RenderContext) -> List[List[Segment]]:
        if bounds.width <= 0 or bounds.height <= 0:
            return []

        text_len = VisualMeter.measure(self.text)

        # Truncation
        display_text = self.text
        if text_len > bounds.width:
            if bounds.width >= len(self.truncate_str):
                # Truncate visual chars (this might be tricky with inline ANSI, but for simple styling we assume text is plain or styled at the segment level)
                # For simplicity, if text has no inline ANSI, we just slice.
                # If it has inline ANSI, it's more complex. We'll strip ANSI to get clean text.
                clean_text = VisualMeter.strip_ansi(self.text)
                allowed_len = bounds.width - len(self.truncate_str)
                display_text = clean_text[:allowed_len] + self.truncate_str
                text_len = bounds.width
            else:
                display_text = ""
                text_len = 0

        pad_total = bounds.width - text_len
        pad_left = 0
        pad_right = 0

        if self.align == self.CENTER:
            pad_left = pad_total // 2
            pad_right = pad_total - pad_left
        elif self.align == self.RIGHT:
            pad_left = pad_total
        else:
            pad_right = pad_total

        styled_segment = Segment(display_text, self.style if ctx.color_mode else None)

        row: List[Segment] = []
        if pad_left > 0:
            row.append(Segment(" " * pad_left))
        row.append(styled_segment)
        if pad_right > 0:
            row.append(Segment(" " * pad_right))

        return [row]
