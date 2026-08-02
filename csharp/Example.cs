using System;
using Chronicle;

namespace ChronicleDemo
{
    class Program
    {
        static void RunDemoPipeline(string modeName)
        {
            ChronicleLogger.LogApplicationTitle($"CHRONICLE DEMO ({modeName.ToUpper()})", 54);

            ChronicleLogger.LogSectionHeader("PROCESSING PIPELINE");
            ChronicleLogger.LogInfo($"Starting pipeline execution in {modeName}...");

            string[] steps = { "Initialization", "Data Processing", "Evaluation" };
            for (int i = 0; i < steps.Length; i++)
            {
                int stepNum = i + 1;
                string stepName = steps[i];
                ChronicleLogger.LogStep(stepNum, 3, stepName);
                ChronicleLogger.LogDebug($"Running internal task for {stepName}");

                if (stepNum == 1)
                {
                    ChronicleLogger.LogSuccess("Initialization complete");
                }
                else if (stepNum == 2)
                {
                    ChronicleLogger.LogWarning("Low memory detected — continuing");
                }
                else
                {
                    ChronicleLogger.LogSuccess("All steps finished");
                }
            }

            ChronicleLogger.LogSubsection("File Operations");
            ChronicleLogger.LogFileSaved("output/data_model.bin");
            ChronicleLogger.LogFileSaved("output/metrics.json");

            StructuredLogger.LogBanner("DATA PROCESSING ENGINE", 54);
            StructuredLogger.LogSection("Execution Phase");
            StructuredLogger.LogDetail("Batch size", 64, 0);
            StructuredLogger.LogDetail("Execution latency", "14.2ms", 0);
            StructuredLogger.LogDecision("PASS", "Quality score 0.96 >= 0.85 threshold");
            StructuredLogger.LogMessage("Pipeline ready for next batch", 1);

            ChronicleLogger.LogFinalResult(true, $"Demo completed successfully ({modeName})");
        }

        static void Main(string[] args)
        {
            // 1. Color Mode
            ChronicleLogger.SetColorMode(true);
            RunDemoPipeline("Color Mode");

            // 2. Colorless Mode
            ChronicleLogger.SetColorMode(false);
            RunDemoPipeline("Colorless Mode");

            // Reset back to default
            ChronicleLogger.SetColorMode(true);
        }
    }
}
