from typing import Protocol, List, Optional
from chronicle.core.geometry import Size, Segment


class RenderContext:
    def __init__(self, bounds: Size, color_mode: bool, ascii_mode: bool):
        self.bounds = bounds
        self.color_mode = color_mode
        self.ascii_mode = ascii_mode


class Renderable(Protocol):
    def measure(self, ctx: RenderContext) -> Size:
        """Measure the size needed by this component, given the context bounds."""
        ...

    def render(self, bounds: Size, ctx: RenderContext) -> List[List[Segment]]:
        """Render the component within the given bounds."""
        ...
