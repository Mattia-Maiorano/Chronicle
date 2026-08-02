import 'package:chronicle/chronicle.dart';

void runDemoPipeline(String modeName) {
  logApplicationTitle("CHRONICLE DEMO (${modeName.toUpperCase()})", width: 54);

  logSectionHeader("PROCESSING PIPELINE");
  logInfo("Starting pipeline execution in $modeName...");

  final steps = ["Initialization", "Data Processing", "Evaluation"];
  for (var i = 0; i < steps.length; i++) {
    final stepNum = i + 1;
    final stepName = steps[i];
    logStep(stepNum, 3, stepName);
    logDebug("Running internal task for $stepName");

    if (stepNum == 1) {
      logSuccess("Initialization complete");
    } else if (stepNum == 2) {
      logWarning("Low memory detected — continuing");
    } else {
      logSuccess("All steps finished");
    }
  }

  logSubsection("File Operations");
  logFileSaved("output/data_model.bin");
  logFileSaved("output/metrics.json");

  StructuredLogger.logBanner("DATA PROCESSING ENGINE", width: 54);
  StructuredLogger.logSection("Execution Phase");
  StructuredLogger.logDetail("Batch size", 64);
  StructuredLogger.logDetail("Execution latency", "14.2ms");
  StructuredLogger.logDecision("PASS", detail: "Quality score 0.96 >= 0.85 threshold");
  StructuredLogger.logMessage("Pipeline ready for next batch", indentLevel: 1);

  logFinalResult(true, "Demo completed successfully ($modeName)");
}

void main() {
  // 1. Color Mode
  setColorMode(true);
  runDemoPipeline("Color Mode");

  // 2. Colorless Mode
  setColorMode(false);
  runDemoPipeline("Colorless Mode");

  // Reset back to default
  setColorMode(true);
}
