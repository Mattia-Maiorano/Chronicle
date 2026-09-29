import time
from chronicle import (
    LiveEngine, Layout, Panel, LiveTable, Column,
    RollingLogStream, Badge, ProgressBar, Text, Fixed, Flex,
    log_info, log_decision, Colors, set_color_mode
)

def run_demo():
    set_color_mode(True)

    # 1. Setup Data Components
    stream = RollingLogStream(max_lines=50)

    table = LiveTable([
        Column("Task", min_width=15, flex=2),
        Column("Status", min_width=10, align="center"),
        Column("Progress", flex=3)
    ])

    # Add initial rows
    p1 = ProgressBar(100, 0, "Build")
    p2 = ProgressBar(100, 0, "Test")

    table.add_row("task1", ["Frontend", Badge("RUNNING", "RUNNING"), p1])
    table.add_row("task2", ["Backend", Badge("PENDING", "WARN"), p2])

    # 2. Setup Layout
    main_layout = Layout(Layout.VERTICAL)

    # Header
    header_panel = Panel(Text("LIVE PIPELINE STATUS", style=Colors.BRIGHT_MAGENTA, align=Text.CENTER), border_style=Panel.ROUNDED)
    main_layout.add(header_panel, Fixed(3))

    # Table
    table_panel = Panel(table, title="Active Tasks", border_style=Panel.DOUBLE)
    main_layout.add(table_panel, Flex(1))

    # Logs
    log_panel = Panel(stream, title="Timeline Event Stream", border_style=Panel.CHRONICLE_TREE)
    main_layout.add(log_panel, Flex(1))

    # 3. Run Engine
    # Run for 5 seconds to simulate
    with LiveEngine(main_layout, mode=LiveEngine.ALTERNATE_SCREEN, refresh_rate_hz=10, redirect_stdout=True, stream=stream) as live:

        log_info("Pipeline started.")

        for i in range(1, 51):
            time.sleep(0.1)
            p1.update(i * 2)

            if i == 25:
                table.update_cell("task1", 1, Badge("PASS", "PASS"))
                table.update_cell("task2", 1, Badge("RUNNING", "RUNNING"))
                log_decision("Frontend Build", "Complete, advancing backend")

            if i > 25:
                p2.update((i - 25) * 4)

            if i % 10 == 0:
                log_info(f"Processed batch {i}")

        table.update_cell("task2", 1, Badge("PASS", "PASS"))
        log_decision("Pipeline", "All tasks completed successfully")
        time.sleep(1)

if __name__ == "__main__":
    run_demo()
