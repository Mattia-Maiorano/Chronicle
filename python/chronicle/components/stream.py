from typing import List
from chronicle.core.geometry import Size, Segment, VisualMeter
from chronicle.layout.base import Renderable, RenderContext

class RollingLogStream:
    def __init__(self, max_lines: int = 100):
        self.max_lines = max_lines
        self.buffer: List[str] = []
        self.dirty = True

    def append(self, text: str):
        self.buffer.append(text)
        if len(self.buffer) > self.max_lines:
            self.buffer.pop(0)
        self.dirty = True

    def measure(self, ctx: RenderContext) -> Size:
        return Size(width=ctx.bounds.width, height=min(len(self.buffer), ctx.bounds.height))

    def render(self, bounds: Size, ctx: RenderContext) -> List[List[Segment]]:
        self.dirty = False
        if bounds.width <= 0 or bounds.height <= 0:
            return []

        lines = []
        start_idx = max(0, len(self.buffer) - bounds.height)
        display_lines = self.buffer[start_idx:]

        for line in display_lines:
            # Handle wrapping or truncation. For simplicity: truncate.
            if VisualMeter.measure(line) > bounds.width:
                # Strip and slice if it exceeds (simple logic, robust ANSI stripping is hard inline)
                clean = VisualMeter.strip_ansi(line)
                display_line = clean[:bounds.width]
                lines.append([Segment(display_line, None)]) # Assuming log already has ANSI embedded, but if we stripped it, we lose it.
                # Actually, better to just let canvas clip it if it's too long.
                # Here we just wrap it in a Segment.
                # But since we're generating segments, we can just pass the raw line.
                # The LiveEngine Canvas renderer blit method will handle clipping.
            else:
                pass

            # Keep the raw line, the canvas handles blitting correctly with clipping.
            lines.append([Segment(line)])

        # Fill remaining height with empty
        for _ in range(bounds.height - len(lines)):
            lines.append([Segment(" " * bounds.width)])

        return lines
