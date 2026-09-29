from typing import List, Tuple
from chronicle.core.geometry import Size, Segment, VisualMeter
from chronicle.logger import Colors


class Canvas:
    def __init__(self, size: Size):
        self.size = size
        # 2D array of (char, style)
        self.buffer: List[List[Tuple[str, str]]] = [
            [(" ", "") for _ in range(size.width)] for _ in range(size.height)
        ]

    def clear(self):
        for y in range(self.size.height):
            for x in range(self.size.width):
                self.buffer[y][x] = (" ", "")

    def blit(self, x: int, y: int, segments: List[Segment]):
        if y < 0 or y >= self.size.height:
            return

        cx = x
        for seg in segments:
            # Clean text may contain embedded ANSI, but VisualMeter strips it.
            # However, for a true virtual canvas, each cell needs only ONE visual char
            # and one style. If 'text' has embedded ANSI, this gets very complicated.
            # For this simplified model, we assume segments are plain text with a single style.
            # If there's embedded ANSI, we just dump it in the first cell, which breaks grid alignment.
            # Let's strip embedded ANSI for grid integrity and rely on seg.style.
            clean_text = VisualMeter.strip_ansi(seg.text)

            for char in clean_text:
                if cx >= self.size.width:
                    break
                if cx >= 0:
                    self.buffer[y][cx] = (char, seg.style or "")
                cx += 1

    def render_to_strings(self) -> List[str]:
        lines = []
        for y in range(self.size.height):
            line = ""
            current_style = ""
            for x in range(self.size.width):
                char, style = self.buffer[y][x]
                if style != current_style:
                    # Reset if switching styles, or just append new style
                    if current_style:
                        line += Colors.RESET
                    if style:
                        line += style
                    current_style = style
                line += char

            if current_style:
                line += Colors.RESET
            lines.append(line)
        return lines
