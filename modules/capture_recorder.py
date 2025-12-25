from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Optional (Windows) foreground window checks.
try:
    import win32gui  # type: ignore
except Exception:  # pragma: no cover
    win32gui = None

# Input capture (cross-platform). On Windows this is what you want.
try:
    from pynput import mouse, keyboard  # type: ignore
except Exception:  # pragma: no cover
    mouse = None
    keyboard = None


@dataclass
class CaptureConfig:
    target_window_substring: str = "Diablo IV"
    mode: str = "event"  # "event" or "fixed"
    fixed_rate_ms: int = 25
    output_path: str = ""


class CaptureRecorder:
    """
    Safe-ish recorder:
      - Only records while user explicitly starts it
      - By default only records while the target window is the foreground window (Windows)
      - No playback, only event logging to JSONL
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._running = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._cfg = CaptureConfig()
        self._start_t = 0.0

        self._mouse_listener = None
        self._kbd_listener = None

        self._events_written = 0
        self._last_move_t = 0.0

        self._fh = None

    def available(self) -> bool:
        return mouse is not None and keyboard is not None

    def supports_foreground_gate(self) -> bool:
        return win32gui is not None

    def status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "running": self._running,
                "paused": self._paused,
                "events_written": self._events_written,
                "target_window_substring": self._cfg.target_window_substring,
                "mode": self._cfg.mode,
                "fixed_rate_ms": self._cfg.fixed_rate_ms,
                "output_path": self._cfg.output_path,
                "foreground_gate": self.supports_foreground_gate(),
            }

    def start(self, cfg: CaptureConfig) -> None:
        if not self.available():
            raise RuntimeError("pynput is not available. Install requirements first.")

        with self._lock:
            if self._running:
                return
            self._cfg = cfg
            os.makedirs(os.path.dirname(cfg.output_path), exist_ok=True)
            self._fh = open(cfg.output_path, "a", encoding="utf-8")
            self._events_written = 0
            self._start_t = time.perf_counter()
            self._last_move_t = 0.0
            self._running = True
            self._paused = False

        # Start listeners
        self._mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self._kbd_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )

        self._mouse_listener.start()
        self._kbd_listener.start()

        self._thread = threading.Thread(target=self._gate_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        with self._lock:
            if not self._running:
                return
            self._running = False

        try:
            if self._mouse_listener is not None:
                self._mouse_listener.stop()
        except Exception:
            pass

        try:
            if self._kbd_listener is not None:
                self._kbd_listener.stop()
        except Exception:
            pass

        with self._lock:
            try:
                if self._fh is not None:
                    self._fh.flush()
                    self._fh.close()
            except Exception:
                pass
            self._fh = None
            self._paused = False

    # --------------------
    # Foreground gating
    # --------------------
    def _is_target_foreground(self) -> bool:
        # If win32gui isn't available, we can't gate by foreground window.
        if win32gui is None:
            return True

        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd) or ""
            return (self._cfg.target_window_substring or "").lower() in title.lower()
        except Exception:
            return True

    def _gate_loop(self) -> None:
        # Poll foreground window; pause if target not focused.
        while True:
            with self._lock:
                if not self._running:
                    return
            ok = self._is_target_foreground()
            with self._lock:
                self._paused = not ok
            time.sleep(0.15)

    # --------------------
    # Event logging
    # --------------------
    def _rel_t(self) -> float:
        return time.perf_counter() - self._start_t

    def _write(self, payload: Dict[str, Any]) -> None:
        with self._lock:
            if not self._running or self._fh is None or self._paused:
                return
            self._fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
            self._events_written += 1

    def _on_move(self, x: int, y: int) -> None:
        # Throttle mouse move events in "fixed" mode.
        if self._cfg.mode == "fixed":
            now = time.perf_counter()
            if self._last_move_t and (now - self._last_move_t) * 1000.0 < max(1, self._cfg.fixed_rate_ms):
                return
            self._last_move_t = now

        self._write({"t": self._rel_t(), "type": "mouse_move", "x": x, "y": y})

    def _on_click(self, x: int, y: int, button, pressed: bool) -> None:
        self._write({
            "t": self._rel_t(),
            "type": "mouse_click",
            "x": x,
            "y": y,
            "button": str(button),
            "pressed": bool(pressed),
        })

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        self._write({
            "t": self._rel_t(),
            "type": "mouse_scroll",
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy,
        })

    def _on_key_press(self, key) -> None:
        self._write({"t": self._rel_t(), "type": "key_press", "key": str(key)})

    def _on_key_release(self, key) -> None:
        self._write({"t": self._rel_t(), "type": "key_release", "key": str(key)})
