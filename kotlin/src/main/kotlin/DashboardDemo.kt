import chronicle.*

fun main() {
    setColorMode(true)

    val stream = RollingLogStream(50)

    val table = LiveTable(
        listOf(
            Column("Task", minWidth = 15, flex = 2),
            Column("Status", minWidth = 10, align = "center"),
            Column("Progress", flex = 3)
        )
    )

    val p1 = ProgressBar(total = 100, completed = 0, label = "Build")
    val p2 = ProgressBar(total = 100, completed = 0, label = "Test")

    table.addRow("task1", listOf("Frontend", Badge("RUNNING", Badge.RUNNING), p1))
    table.addRow("task2", listOf("Backend", Badge("PENDING", Badge.WARN), p2))

    val mainLayout = Layout(FlexSplitter.VERTICAL)

    val headerPanel = Panel(
        Text("LIVE PIPELINE STATUS", style = Colors.BRIGHT_MAGENTA, align = Text.CENTER),
        borderStyle = Panel.ROUNDED
    )
    mainLayout.add(headerPanel, Fixed(3))

    val tablePanel = Panel(table, title = "Active Tasks", borderStyle = Panel.DOUBLE)
    mainLayout.add(tablePanel, Flex(1))

    val logPanel = Panel(stream, title = "Timeline Event Stream", borderStyle = Panel.CHRONICLE_TREE)
    mainLayout.add(logPanel, Flex(1))

    val engine = LiveEngine(mainLayout, mode = LiveEngine.ALTERNATE_SCREEN, refreshRateHz = 10.0)
    engine.start()

    stream.append("INFO: Pipeline started.")

    for (i in 1..50) {
        Thread.sleep(100)
        p1.update(i * 2)

        if (i == 25) {
            table.updateCell("task1", 1, Badge("PASS", Badge.PASS))
            table.updateCell("task2", 1, Badge("RUNNING", Badge.RUNNING))
            stream.append("  +--> DECISION: Frontend Build -> Complete, advancing backend")
        }

        if (i > 25) {
            p2.update((i - 25) * 4)
        }

        if (i % 10 == 0) {
            stream.append("INFO: Processed batch $i")
        }
    }

    table.updateCell("task2", 1, Badge("PASS", Badge.PASS))
    stream.append("  +--> DECISION: Pipeline -> All tasks completed successfully")
    Thread.sleep(1000)

    engine.stop()
}
