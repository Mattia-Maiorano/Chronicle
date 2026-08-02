package main

import (
	"fmt"

	"github.com/Mattia-Maiorano/Chronicle/go"
)

func runDemoPipeline(modeName string) {
	chronicle.LogApplicationTitle(fmt.Sprintf("CHRONICLE DEMO (%s)", modeName), 54)

	chronicle.LogSectionHeader("PROCESSING PIPELINE")
	chronicle.LogInfo(fmt.Sprintf("Starting pipeline execution in %s...", modeName))

	steps := []string{"Initialization", "Data Processing", "Evaluation"}
	for i, stepName := range steps {
		stepNum := i + 1
		chronicle.LogStep(stepNum, 3, stepName)
		chronicle.LogDebug(fmt.Sprintf("Running internal task for %s", stepName))

		if stepNum == 1 {
			chronicle.LogSuccess("Initialization complete")
		} else if stepNum == 2 {
			chronicle.LogWarning("Low memory detected — continuing")
		} else {
			chronicle.LogSuccess("All steps finished")
		}
	}

	chronicle.LogSubsection("File Operations")
	chronicle.LogFileSaved("output/data_model.bin")
	chronicle.LogFileSaved("output/metrics.json")

	chronicle.LogBanner("DATA PROCESSING ENGINE", 54)
	chronicle.LogSection("Execution Phase")
	chronicle.LogDetail("Batch size", 64, 0)
	chronicle.LogDetail("Execution latency", "14.2ms", 0)
	chronicle.LogDecision("PASS", "Quality score 0.96 >= 0.85 threshold")
	chronicle.LogMessage("Pipeline ready for next batch", 1)

	chronicle.LogFinalResult(true, fmt.Sprintf("Demo completed successfully (%s)", modeName))
}

func main() {
	// 1. Color Mode
	chronicle.SetColorMode(true)
	runDemoPipeline("Color Mode")

	// 2. Colorless Mode
	chronicle.SetColorMode(false)
	runDemoPipeline("Colorless Mode")

	// Reset to default
	chronicle.SetColorMode(true)
}
