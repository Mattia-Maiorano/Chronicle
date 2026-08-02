import chronicle.*

fun runDemoPipeline(modeName: String) {
    logApplicationTitle("CHRONICLE DEMO (${modeName.uppercase()})", width = 54)

    logSectionHeader("PROCESSING PIPELINE")
    logInfo("Starting pipeline execution in $modeName...")

    val steps = listOf("Initialization", "Data Processing", "Evaluation")
    for ((index, stepName) in steps.withIndex()) {
        val stepNum = index + 1
        logStep(stepNum, 3, stepName)
        logDebug("Running internal task for $stepName")

        when (stepNum) {
            1 -> logSuccess("Initialization complete")
            2 -> logWarning("Low memory detected — continuing")
            else -> logSuccess("All steps finished")
        }
    }

    logSubsection("File Operations")
    logFileSaved("output/data_model.bin")
    logFileSaved("output/metrics.json")

    StructuredLogger.logBanner("DATA PROCESSING ENGINE", width = 54)
    StructuredLogger.logSection("Execution Phase")
    StructuredLogger.logDetail("Batch size", 64, indentLevel = 0)
    StructuredLogger.logDetail("Execution latency", "14.2ms", indentLevel = 0)
    StructuredLogger.logDecision("PASS", detail = "Quality score 0.96 >= 0.85 threshold")
    StructuredLogger.logMessage("Pipeline ready for next batch", indentLevel = 1)

    logFinalResult(true, "Demo completed successfully ($modeName)")
}

fun main() {
    // 1. Color Mode
    setColorMode(true)
    runDemoPipeline("Color Mode")

    // 2. Colorless Mode
    setColorMode(false)
    runDemoPipeline("Colorless Mode")

    // Reset back to default
    setColorMode(true)
}
