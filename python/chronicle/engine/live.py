import sys
import threading
import time
import signal
from typing import Optional, ContextManager
import chronicle.logger as chronicle_logger

from chronicle.core.geometry import Size, TerminalMetrics
from chronicle.layout.base import Renderable, RenderContext
from chronicle.engine.canvas import Canvas

class LiveEngine:
    INLINE = "inline"
    ALTERNATE_SCREEN = "alternate_screen"

    def __init__(self, renderable: Renderable, mode: str = INLINE, refresh_rate_hz: float = 10.0, redirect_stdout: bool = False, stream = None):
        self.renderable = renderable
        self.mode = mode
        self.refresh_rate = 1.0 / refresh_rate_hz
        self.redirect_stdout = redirect_stdout
        self.stream = stream # RollingLogStream instance if redirection needed

        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()

        self.canvas: Optional[Canvas] = None
        self.last_size: Optional[Size] = None
        self.rendered_lines = 0

        # Redirection backups
        self._original_log_funcs = {}

    def start(self):
        with self._lock:
            if self.running:
                return
            self.running = True

            # Setup signal handlers (best effort, signal only works in main thread)
            if threading.current_thread() == threading.main_thread():
                signal.signal(signal.SIGINT, self._sig_handler)
                signal.signal(signal.SIGTERM, self._sig_handler)
                if hasattr(signal, 'SIGWINCH'):
                    signal.signal(signal.SIGWINCH, self._resize_handler)

            # Cursor hide
            if chronicle_logger._COLOR_MODE:
                sys.stdout.write("\033[?25l")

            if self.mode == self.ALTERNATE_SCREEN and chronicle_logger._COLOR_MODE:
                sys.stdout.write("\033[?1049h")

            if self.redirect_stdout and self.stream:
                self._redirect_logs()

            # Initial snapshot for colorless
            if not chronicle_logger._COLOR_MODE:
                self.refresh()

            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            if not self.running:
                return
            self.running = False

        if self._thread:
            self._thread.join()

        # Restore logs
        if self.redirect_stdout and self.stream:
            self._restore_logs()

        # Cleanup display
        if chronicle_logger._COLOR_MODE:
            if self.mode == self.ALTERNATE_SCREEN:
                sys.stdout.write("\033[?1049l")
            sys.stdout.write("\033[?25h") # Cursor show

        # Final snapshot for colorless
        if not chronicle_logger._COLOR_MODE:
            self.refresh()

        sys.stdout.flush()

    def _run_loop(self):
        while self.running:
            if chronicle_logger._COLOR_MODE:
                # We need a way to check if dirty. For now we assume if running we redraw.
                # Real implementation would walk tree to check dirty flag.
                # Since we don't have a tree walker, we'll redraw.
                self.refresh()
                time.sleep(self.refresh_rate)
            else:
                # Colorless mode: Throttled snapshot cadence
                # E.g. every 5 seconds
                time.sleep(5.0)
                if self.running:
                    self.refresh()

    def refresh(self):
        with self._lock:
            size = TerminalMetrics.get_size()

            if self.mode == self.INLINE:
                # We might want to cap height for inline based on terminal or fixed size
                # Measure first
                ctx = RenderContext(size, chronicle_logger._COLOR_MODE, chronicle_logger.get_ascii_mode())
                measured_size = self.renderable.measure(ctx)
                height = min(measured_size.height, size.height - 1) # leave room for cursor
                size = Size(size.width, height)

            if not self.canvas or self.canvas.size != size:
                self.canvas = Canvas(size)

            self.canvas.clear()

            ctx = RenderContext(size, chronicle_logger._COLOR_MODE, chronicle_logger.get_ascii_mode())
            lines = self.renderable.render(size, ctx)

            for y, line_segments in enumerate(lines):
                if y >= size.height:
                    break
                self.canvas.blit(0, y, line_segments)

            rendered_strings = self.canvas.render_to_strings()

            if chronicle_logger._COLOR_MODE:
                # Move cursor up if inline and already rendered
                if self.mode == self.INLINE and self.rendered_lines > 0:
                    sys.stdout.write(f"\033[{self.rendered_lines}A")

                for r_str in rendered_strings:
                    sys.stdout.write("\033[2K") # Clear line
                    sys.stdout.write(r_str + "\n")

                self.rendered_lines = len(rendered_strings)
            else:
                # Colorless mode: print snapshot
                print("\n--- Live Snapshot ---")
                for r_str in rendered_strings:
                    print(r_str)
                print("---------------------\n")

            sys.stdout.flush()

    def _sig_handler(self, signum, frame):
        self.stop()
        sys.exit(0)

    def _resize_handler(self, signum, frame):
        self.refresh()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def _redirect_logs(self):
        # We hook into print and direct log_* functions if possible,
        # but since we want to capture Chronicle logs specifically,
        # we can patch the underlying chronicle_logger.log function.
        self._original_log = chronicle_logger.log

        def patched_log(indentation_tabs=0, newline_before=0, newline_after=0, color=None, content="", color_mode=None):
            # Format exactly as Chronicle would
            indentation = '\t' * indentation_tabs
            use_color = chronicle_logger._COLOR_MODE if color_mode is None else color_mode
            if color and use_color:
                message = f"{indentation}{color}{content}{chronicle_logger.Colors.RESET}"
            else:
                message = f"{indentation}{content}"

            self.stream.append(message)

        chronicle_logger.log = patched_log

        # Also patch print for generic StructuredLogger.log_* methods which use print
        self._original_print = __builtins__["print"]
        def patched_print(*args, **kwargs):
            sep = kwargs.get('sep', ' ')
            end = kwargs.get('end', '\n')
            message = sep.join(str(a) for a in args) + end
            # Remove trailing newlines for stream appending
            self.stream.append(message.rstrip('\n'))

        __builtins__["print"] = patched_print

    def _restore_logs(self):
        if hasattr(self, '_original_log'):
            chronicle_logger.log = self._original_log
        if hasattr(self, '_original_print'):
            __builtins__["print"] = self._original_print
