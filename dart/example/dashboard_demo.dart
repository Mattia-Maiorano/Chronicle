import 'dart:async';
import 'package:chronicle/chronicle.dart';

void main() async {
  setColorMode(true);

  final stream = RollingLogStream(50);

  final table = LiveTable([
    const Column("Task", minWidth: 15, flex: 2),
    const Column("Status", minWidth: 10, align: "center"),
    const Column("Progress", flex: 3),
  ]);

  final p1 = ProgressBar(total: 100, completed: 0, label: "Build");
  final p2 = ProgressBar(total: 100, completed: 0, label: "Test");

  table.addRow("task1", ["Frontend", const Badge("RUNNING", badgeType: Badge.running), p1]);
  table.addRow("task2", ["Backend", const Badge("PENDING", badgeType: Badge.warn), p2]);

  final mainLayout = Layout(FlexSplitter.vertical);

  final headerPanel = Panel(
    const Text("LIVE PIPELINE STATUS", style: "\x1b[95m", align: Text.center),
    borderStyle: Panel.rounded,
  );
  mainLayout.add(headerPanel, const Fixed(3));

  final tablePanel = Panel(table, title: "Active Tasks", borderStyle: Panel.doubleBorder);
  mainLayout.add(tablePanel, const Flex(1));

  final logPanel = Panel(stream, title: "Timeline Event Stream", borderStyle: Panel.chronicleTree);
  mainLayout.add(logPanel, const Flex(1));

  final engine = LiveEngine(mainLayout, mode: LiveEngine.alternateScreen, refreshRateHz: 10);
  engine.start();

  stream.append("INFO: Pipeline started.");

  for (int i = 1; i <= 50; i++) {
    await Future.delayed(const Duration(milliseconds: 100));
    p1.update(i * 2);

    if (i == 25) {
      table.updateCell("task1", 1, const Badge("PASS", badgeType: Badge.pass));
      table.updateCell("task2", 1, const Badge("RUNNING", badgeType: Badge.running));
      stream.append("  +--> DECISION: Frontend Build -> Complete, advancing backend");
    }

    if (i > 25) {
      p2.update((i - 25) * 4);
    }

    if (i % 10 == 0) {
      stream.append("INFO: Processed batch $i");
    }
  }

  table.updateCell("task2", 1, const Badge("PASS", badgeType: Badge.pass));
  stream.append("  +--> DECISION: Pipeline -> All tasks completed successfully");
  await Future.delayed(const Duration(seconds: 1));

  engine.stop();
}
