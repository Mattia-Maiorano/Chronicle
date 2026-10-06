import { LiveEngine, Layout, Panel, Text, LiveTable, RollingLogStream, ProgressBar, Badge, Fixed, Flex } from "../src";

const stream = new RollingLogStream(50);

const table = new LiveTable([
    { header: "Task", minWidth: 15, flex: 2 },
    { header: "Status", minWidth: 10, align: "center" },
    { header: "Progress", flex: 3 }
]);

const p1 = new ProgressBar(100, 0, "Build");
const p2 = new ProgressBar(100, 0, "Test");

table.addRow("task1", ["Frontend", new Badge("RUNNING", "RUNNING"), p1]);
table.addRow("task2", ["Backend", new Badge("PENDING", "WARN"), p2]);

const mainLayout = new Layout(Layout.VERTICAL);

const headerPanel = new Panel(new Text("LIVE PIPELINE STATUS", "\x1b[95m", Text.CENTER), null, null, Panel.ROUNDED);
mainLayout.add(headerPanel, new Fixed(3)); // Fixed

const tablePanel = new Panel(table, "Active Tasks", null, Panel.DOUBLE);
mainLayout.add(tablePanel, new Flex(1)); // Flex

const logPanel = new Panel(stream, "Timeline Event Stream", null, Panel.CHRONICLE_TREE);
mainLayout.add(logPanel, new Flex(1)); // Flex

const engine = new LiveEngine(mainLayout, LiveEngine.ALTERNATE_SCREEN, 10);
engine.start();

stream.append("INFO: Pipeline started.");

let i = 0;
const interval = setInterval(() => {
    i++;
    p1.update(i * 2);

    if (i === 25) {
        table.updateCell("task1", 1, new Badge("PASS", "PASS"));
        table.updateCell("task2", 1, new Badge("RUNNING", "RUNNING"));
        stream.append("  +--> DECISION: Frontend Build -> Complete, advancing backend");
    }

    if (i > 25) {
        p2.update((i - 25) * 4);
    }

    if (i % 10 === 0) {
        stream.append(`INFO: Processed batch ${i}`);
    }

    if (i >= 50) {
        clearInterval(interval);
        table.updateCell("task2", 1, new Badge("PASS", "PASS"));
        stream.append("  +--> DECISION: Pipeline -> All tasks completed successfully");

        setTimeout(() => {
            engine.stop();
        }, 1000);
    }
}, 100);
