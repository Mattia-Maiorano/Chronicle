import unittest
from chronicle.core.geometry import VisualMeter, Size, TerminalMetrics
from chronicle.layout import FlexSplitter, Fixed, Flex
from chronicle.components import LiveTable, Column
from chronicle.layout.base import RenderContext
from chronicle.logger import Colors

class TestLiveDashboard(unittest.TestCase):
    def test_visual_meter_strip_ansi(self):
        styled = f"{Colors.BRIGHT_CYAN}Hello{Colors.RESET}"
        clean = VisualMeter.strip_ansi(styled)
        self.assertEqual(clean, "Hello")

    def test_visual_meter_measure(self):
        styled = f"{Colors.BRIGHT_CYAN}Hello World{Colors.RESET}"
        self.assertEqual(VisualMeter.measure(styled), 11)

    def test_flex_splitter_measure(self):
        # Even without full render layout tree traversal, we can test component behavior
        ctx = RenderContext(Size(100, 24), True, False)
        layout = FlexSplitter()
        # Measure just returns bounds for layout
        size = layout.measure(ctx)
        self.assertEqual(size, Size(100, 24))

    def test_live_table_updates(self):
        table = LiveTable([
            Column("ID", min_width=5),
            Column("Status", flex=1)
        ])

        table.add_row("row1", ["1", "Pending"])
        self.assertEqual(len(table.rows), 1)

        table.update_cell("row1", 1, "Running")
        self.assertEqual(table.rows[0]["cells"][1], "Running")

        table.update_row("row1", ["1", "Complete"])
        self.assertEqual(table.rows[0]["cells"][1], "Complete")

if __name__ == "__main__":
    unittest.main()
