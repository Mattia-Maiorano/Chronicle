from typing import Tuple
from typing import List, Union
from chronicle.core.geometry import Size, Segment, VisualMeter
from chronicle.layout.base import Renderable, RenderContext

class Fixed:
    def __init__(self, size: int):
        self.size = size

class Flex:
    def __init__(self, weight: int = 1):
        self.weight = weight

class Ratio:
    def __init__(self, percentage: float):
        self.percentage = percentage

Policy = Union[Fixed, Flex, Ratio]


class FlexSplitter:
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

    def __init__(self, direction: str = HORIZONTAL):
        self.direction = direction
        self.children: List[Tuple[Renderable, Policy]] = []

    def add(self, child: Renderable, policy: Policy = Flex(1)):
        self.children.append((child, policy))

    def measure(self, ctx: RenderContext) -> Size:
        # In a real dynamic layout, measure is complex.
        # For simplicity, returning full bounds available, as it expands to fill.
        return ctx.bounds

    def render(self, bounds: Size, ctx: RenderContext) -> List[List[Segment]]:
        if not self.children:
            return []

        total_size = bounds.width if self.direction == self.HORIZONTAL else bounds.height

        # Calculate sizes based on policies
        sizes = [0] * len(self.children)
        remaining_size = total_size

        # 1. Fixed and Ratio
        for i, (_, policy) in enumerate(self.children):
            if isinstance(policy, Fixed):
                sizes[i] = policy.size
                remaining_size -= sizes[i]
            elif isinstance(policy, Ratio):
                sizes[i] = int(total_size * policy.percentage)
                remaining_size -= sizes[i]

        # 2. Flex
        flex_sum = sum(policy.weight for _, policy in self.children if isinstance(policy, Flex))
        if flex_sum > 0 and remaining_size > 0:
            flex_unit = remaining_size / flex_sum
            for i, (_, policy) in enumerate(self.children):
                if isinstance(policy, Flex):
                    alloc = int(policy.weight * flex_unit)
                    sizes[i] = alloc
                    remaining_size -= alloc

            # Distribute remaining pixel(s) to the first flex
            for i, (_, policy) in enumerate(self.children):
                if isinstance(policy, Flex) and remaining_size > 0:
                    sizes[i] += remaining_size
                    remaining_size = 0
                    break

        # Render children
        rendered_children = []
        for i, (child, _) in enumerate(self.children):
            if self.direction == self.HORIZONTAL:
                c_bounds = Size(sizes[i], bounds.height)
            else:
                c_bounds = Size(bounds.width, sizes[i])

            c_ctx = RenderContext(c_bounds, ctx.color_mode, ctx.ascii_mode)
            c_lines = child.render(c_bounds, c_ctx)
            rendered_children.append((c_bounds, c_lines))

        # Assemble
        lines = []
        if self.direction == self.HORIZONTAL:
            for y in range(bounds.height):
                row = []
                for (c_bounds, c_lines) in rendered_children:
                    if y < len(c_lines):
                        row.extend(c_lines[y])
                        c_len = sum(VisualMeter.measure(seg.text) for seg in c_lines[y])
                        pad = c_bounds.width - c_len
                        if pad > 0:
                            row.append(Segment(" " * pad))
                    else:
                        row.append(Segment(" " * c_bounds.width))
                lines.append(row)
        else:
            for (c_bounds, c_lines) in rendered_children:
                for y in range(c_bounds.height):
                    if y < len(c_lines):
                        lines.append(c_lines[y])
                    else:
                        lines.append([Segment(" " * bounds.width)])

        return lines

# Alias Layout to FlexSplitter as per spec step 2
Layout = FlexSplitter
