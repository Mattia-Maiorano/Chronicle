import time
from typing import List
from chronicle.core.geometry import Size, Segment, VisualMeter
from chronicle.layout.base import Renderable, RenderContext
from chronicle.logger import Colors

class ProgressBar:
    SPINNERS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, total: float = 100.0, current: float = 0.0, label: str = ""):
        self.total = total
        self.current = current
        self.label = label
        self.dirty = True

    def update(self, current: float):
        self.current = current
        self.dirty = True

    def measure(self, ctx: RenderContext) -> Size:
        return Size(width=ctx.bounds.width, height=1)

    def render(self, bounds: Size, ctx: RenderContext) -> List[List[Segment]]:
        self.dirty = False
        if bounds.width <= 0 or bounds.height <= 0:
            return []

        progress = min(1.0, max(0.0, self.current / self.total if self.total > 0 else 0))
        percent_str = f"{int(progress * 100)}%"

        spinner_idx = int(time.time() * 10) % len(self.SPINNERS)
        spinner = self.SPINNERS[spinner_idx] if ctx.color_mode and not ctx.ascii_mode else ""

        label_part = f"{spinner} {self.label}".strip() if spinner else self.label

        # Format: [Label] [======>   ] [100%]

        meta_len = VisualMeter.measure(label_part) + 1 + len(percent_str) + 4 # spaces and brackets
        bar_width = max(0, bounds.width - meta_len)

        filled_len = int(bar_width * progress)
        empty_len = bar_width - filled_len

        bar_char = "█" if ctx.color_mode and not ctx.ascii_mode else "="
        empty_char = "░" if ctx.color_mode and not ctx.ascii_mode else " "

        bar = (bar_char * filled_len) + (empty_char * empty_len)

        row = []
        if label_part:
            row.append(Segment(f"{label_part} "))

        row.append(Segment("[", Colors.BRIGHT_BLACK if ctx.color_mode else None))
        row.append(Segment(bar, Colors.BRIGHT_GREEN if ctx.color_mode else None))
        row.append(Segment("] ", Colors.BRIGHT_BLACK if ctx.color_mode else None))

        row.append(Segment(f"{percent_str:>4}", Colors.BRIGHT_WHITE if ctx.color_mode else None))

        # pad
        c_len = sum(VisualMeter.measure(s.text) for s in row)
        pad = bounds.width - c_len
        if pad > 0:
            row.append(Segment(" " * pad))

        return [row]
