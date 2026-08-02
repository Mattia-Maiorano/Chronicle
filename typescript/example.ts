import {
  setColorMode,
  logApplicationTitle,
  logSectionHeader,
  logSubsection,
  logInfo,
  logStep,
  logDebug,
  logSuccess,
  logWarning,
  logFileSaved,
  logFinalResult,
  StructuredLogger
} from "./src/logger";

function runDemoPipeline(modeName: string): void {
  logApplicationTitle(`CHRONICLE DEMO (${modeName.toUpperCase()})`, 54);

  logSectionHeader("PROCESSING PIPELINE");
  logInfo(`Starting pipeline execution in ${modeName}...`);

  const steps = ["Initialization", "Data Processing", "Evaluation"];
  steps.forEach((stepName, index) => {
    const stepNum = index + 1;
    logStep(stepNum, 3, stepName);
    logDebug(`Running internal task for ${stepName}`);

    if (stepNum === 1) {
      logSuccess("Initialization complete");
    } else if (stepNum === 2) {
      logWarning("Low memory detected — continuing");
    } else {
      logSuccess("All steps finished");
    }
  });

  logSubsection("File Operations");
  logFileSaved("output/data_model.bin");
  logFileSaved("output/metrics.json");

  StructuredLogger.logBanner("DATA PROCESSING ENGINE", 54);
  StructuredLogger.logSection("Execution Phase");
  StructuredLogger.logDetail("Batch size", "64", 0);
  StructuredLogger.logDetail("Execution latency", "14.2ms", 0);
  StructuredLogger.logDecision("PASS", "Quality score 0.96 >= 0.85 threshold");
  StructuredLogger.logMessage("Pipeline ready for next batch", 1);

  logFinalResult(true, `Demo completed successfully (${modeName})`);
}

function main(): void {
  // 1. Color Mode
  setColorMode(true);
  runDemoPipeline("Color Mode");

  // 2. Colorless Mode
  setColorMode(false);
  runDemoPipeline("Colorless Mode");

  // Reset back to default
  setColorMode(true);
}

main();
