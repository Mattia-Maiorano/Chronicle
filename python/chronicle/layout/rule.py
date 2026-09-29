from typing import List, Optional
from chronicle.core.geometry import Size, Segment, VisualMeter
from chronicle.layout.base import Renderable, RenderContext
from chronicle.logger import Colors


class Rule:
    def __init__(self, title: Optional[str] = None, style: str = "", character: str = "─"):
        self.title = title
        self.style = style
        self.character = character

    def measure(self, ctx: RenderContext) -> Size:
        return Size(width=ctx.bounds.width, height=1)

    def render(self, bounds: Size, ctx: RenderContext) -> List[List[Segment]]:
        if bounds.width <= 0 or bounds.height <= 0:
            return []

        char = self.character if ctx.color_mode and not ctx.ascii_mode else "-"
        style = self.style if ctx.color_mode else None

        if not self.title:
            return [[Segment(char * bounds.width, style)]]

        # Inject title
        title_text = f" {self.title} "
        title_len = VisualMeter.measure(title_text)

        if title_len >= bounds.width:
            # Title is too wide, truncate it or just draw title
            return [[Segment(title_text[:bounds.width], style)]]

        left_dash_len = (bounds.width - title_len) // 2
        right_dash_len = bounds.width - title_len - left_dash_len

        row = []
        if left_dash_len > 0:
            row.append(Segment(char * left_dash_len, style))
        row.append(Segment(title_text, style))
        if right_dash_len > 0:
            row.append(Segment(char * right_dash_len, style))

        return [row]
