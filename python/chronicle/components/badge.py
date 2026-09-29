from typing import List, Dict
from chronicle.core.geometry import Size, Segment, VisualMeter
from chronicle.layout.base import Renderable, RenderContext
from chronicle.logger import Colors

class Badge:
    STYLES: Dict[str, str] = {
        "RUNNING": Colors.BRIGHT_BLUE,
        "PASS": Colors.BRIGHT_GREEN,
        "ERROR": Colors.BRIGHT_RED,
        "WARN": Colors.BRIGHT_YELLOW,
        "DEFAULT": Colors.BRIGHT_WHITE,
    }

    def __init__(self, text: str, status: str = "DEFAULT"):
        self.text = text
        self.status = status.upper()

    def measure(self, ctx: RenderContext) -> Size:
        return Size(width=VisualMeter.measure(self.text) + 2, height=1)

    def render(self, bounds: Size, ctx: RenderContext) -> List[List[Segment]]:
        if bounds.width <= 0 or bounds.height <= 0:
            return []

        style = self.STYLES.get(self.status, self.STYLES["DEFAULT"]) if ctx.color_mode else ""
        text = f" {self.text} "

        # Truncate
        if VisualMeter.measure(text) > bounds.width:
            text = text[:bounds.width]

        pad = bounds.width - VisualMeter.measure(text)

        row = []
        if style:
            # We add bold + background
            bg_style = style.replace('3', '4', 1) if '3' in style else style # rough approximation, best is to use specific bg colors
            # Better to just use bold color for badge
            row.append(Segment(text, style + Colors.BOLD))
        else:
            row.append(Segment(f"[{self.text}]"))

        if pad > 0:
             row.append(Segment(" " * pad))

        return [row]
