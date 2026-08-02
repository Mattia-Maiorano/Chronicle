import io
import sys
import unittest

from chronicle import (
    set_color_mode,
    get_color_mode,
    set_colorless_mode,
    set_ascii_mode,
    get_ascii_mode,
    StructuredLogger,
    AsciiLogger,
    log_banner,
    log_section,
    log_detail,
    log_decision,
    log_message,
    log_info,
    log_error,
    log_warning,
    log_success,
    log_debug,
    log_file_saved,
    log_application_title,
    log_section_header,
)


class TestColorAndColorlessModes(unittest.TestCase):
    def setUp(self):
        set_color_mode(True)
        self.held_output = io.StringIO()
        sys.stdout = self.held_output

    def tearDown(self):
        sys.stdout = sys.__stdout__
        set_color_mode(True)

    def test_color_mode_toggle(self):
        self.assertTrue(get_color_mode())
        set_color_mode(False)
        self.assertFalse(get_color_mode())
        set_colorless_mode(True)
        self.assertFalse(get_color_mode())
        set_ascii_mode(True)
        self.assertTrue(get_ascii_mode())

    def test_log_banner_colorless(self):
        set_color_mode(False)
        log_banner("ENGINE BANNER", width=54)
        output = self.held_output.getvalue()
        self.assertIn("+----------------------------------------------------+", output)
        self.assertIn("| [ENGINE BANNER]                                    |", output)
        self.assertNotIn("\033[", output)

    def test_log_section_colorless(self):
        set_color_mode(False)
        log_section("Data Processor")
        output = self.held_output.getvalue()
        self.assertEqual(output, "\n  |-- Data Processor:\n")

    def test_log_detail_colorless(self):
        set_color_mode(False)
        log_detail("Execution latency", "12.4ms", indent_level=0)
        output = self.held_output.getvalue()
        self.assertEqual(output, "  +-- Execution latency      : 12.4ms\n")

    def test_log_decision_colorless(self):
        set_color_mode(False)
        log_decision("PROCEED", "Score 0.98 >= 0.85 threshold")
        output = self.held_output.getvalue()
        self.assertEqual(output, "\n  +--> DECISION: PROCEED -> Score 0.98 >= 0.85 threshold\n\n")

    def test_log_decision_no_detail_colorless(self):
        set_color_mode(False)
        log_decision("SKIP")
        output = self.held_output.getvalue()
        self.assertEqual(output, "\n  +--> DECISION: SKIP\n\n")

    def test_log_message_colorless(self):
        set_color_mode(False)
        log_message("Model loaded into memory", indent_level=1)
        output = self.held_output.getvalue()
        self.assertEqual(output, "  |-- Model loaded into memory\n")

    def test_structured_logger_class_parity(self):
        set_color_mode(False)
        StructuredLogger.log_banner("TEST BANNER")
        StructuredLogger.log_section("Category")
        StructuredLogger.log_detail("Metric", 100)
        StructuredLogger.log_decision("ACTION", "DETAIL")
        StructuredLogger.log_message("RAW MESSAGE")

        output = self.held_output.getvalue()
        self.assertIn("[TEST BANNER]", output)
        self.assertIn("|-- Category:", output)
        self.assertIn("+-- Metric                 : 100", output)
        self.assertIn("+--> DECISION: ACTION -> DETAIL", output)
        self.assertIn("|-- RAW MESSAGE", output)

    def test_camel_case_aliases(self):
        set_color_mode(False)
        AsciiLogger.logBanner("CAMEL BANNER")
        AsciiLogger.logSection("Camel Section")
        AsciiLogger.logDetail("Camel Label", "val")
        AsciiLogger.logDecision("CAMEL_ACT", "CAMEL_DET")
        AsciiLogger.logMessage("Camel Msg")

        output = self.held_output.getvalue()
        self.assertIn("[CAMEL BANNER]", output)
        self.assertIn("|-- Camel Section:", output)
        self.assertIn("+-- Camel Label            : val", output)
        self.assertIn("+--> DECISION: CAMEL_ACT -> CAMEL_DET", output)
        self.assertIn("|-- Camel Msg", output)

    def test_semantic_loggers_colorless_mode(self):
        set_color_mode(False)
        log_info("Info message")
        log_error("Error message")
        log_warning("Warning message")
        log_success("Success message")
        log_debug("Debug message")
        log_file_saved("path/to/file.txt")

        output = self.held_output.getvalue()
        self.assertIn("[INFO] Info message", output)
        self.assertIn("[ERROR] Error message", output)
        self.assertIn("[WARNING] Warning message", output)
        self.assertIn("[OK] Success message", output)
        self.assertIn("\t\t[DEBUG] Debug message", output)
        self.assertIn("Saved: path/to/file.txt", output)
        # Ensure no ANSI colors in output
        self.assertNotIn("\033[", output)

    def test_application_title_colorless_mode(self):
        set_color_mode(False)
        log_application_title("TITLE", width=30)
        output = self.held_output.getvalue()
        self.assertIn("+----------------------------+", output)
        self.assertIn("|           TITLE            |", output)
        self.assertNotIn("╔", output)
        self.assertNotIn("\033[", output)


if __name__ == "__main__":
    unittest.main()
