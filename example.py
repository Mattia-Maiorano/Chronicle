"""example.py
Runnable demonstration of Chronicle's public API.

This script demonstrates identical logging hierarchies in both modes:
1. Color Mode (Full ANSI colors, bright styles, and tree formatting)
2. Colorless Mode (Clean plain text without ANSI escape sequences)

Run it with:
    python example.py
"""

from time import sleep

from chronicle import (
    Colors,
    log,
    log_application_title,
    log_section_header,
    log_subsection,
    log_step,
    log_file_saved,
    log_error,
    log_warning,
    log_success,
    log_info,
    log_debug,
    log_final_result,
    set_color_mode,
    StructuredLogger,
)


def run_demo_pipeline(mode_name: str) -> None:
    """Run the complete logging hierarchy for a given modality."""
    # Application Title
    log_application_title(f"CHRONICLE DEMO ({mode_name.upper()})", width=54)

    # 1. High-level Pipeline Section & Steps
    log_section_header("PROCESSING PIPELINE")
    log_info(f"Starting pipeline execution in {mode_name}...")

    for i, step_name in enumerate(("Initialization", "Data Processing", "Evaluation"), start=1):
        log_step(i, 3, step_name)
        log_debug(f"Running internal task for {step_name}")
        sleep(0.05)

        if i == 1:
            log_success("Initialization complete")
        elif i == 2:
            log_warning("Low memory detected — continuing")
        else:
            log_success("All steps finished")

    # 2. File Operations
    log_subsection("File Operations")
    log_file_saved("output/data_model.bin")
    log_file_saved("output/metrics.json")

    # 3. Structured Tree Logger
    StructuredLogger.log_banner("DATA PROCESSING ENGINE", width=54)
    StructuredLogger.log_section("Execution Phase")
    StructuredLogger.log_detail("Batch size", "64", indent_level=0)
    StructuredLogger.log_detail("Execution latency", "14.2ms", indent_level=0)
    StructuredLogger.log_decision("PASS", "Quality score 0.96 >= 0.85 threshold")
    StructuredLogger.log_message("Pipeline ready for next batch", indent_level=1)

    # 4. Final Result Box
    log_final_result(True, f"Demo completed successfully ({mode_name})")


def main() -> None:
    # --- 1. Run Pipeline in Color Mode ---
    set_color_mode(True)
    run_demo_pipeline("Color Mode")

    # --- 2. Run Identical Pipeline in Colorless Mode ---
    set_color_mode(False)
    run_demo_pipeline("Colorless Mode")

    # Reset back to default (Color Mode)
    set_color_mode(True)


if __name__ == "__main__":
    main()
