from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

try:
    # Timer overlay is pure tkinter
    from modules.overlay.timer_overlay_tk import TimerOverlay
except Exception:
    TimerOverlay = None  # type: ignore


@dataclass
class OverlayState:
    timer_overlay: Optional[Any] = None  # TimerOverlay


class OverlayController:
    """
    Keeps overlay windows in one place so the OVERLAY page (and future overlay tools)
    can toggle them without duplicating logic.
    """
    def __init__(self, root):
        self.root = root
        self.state = OverlayState()

    def toggle_timers(self, x: int = 30, y: int = 30) -> bool:
        """
        Returns True if now enabled, False if disabled.
        """
        if TimerOverlay is None:
            raise RuntimeError("TimerOverlay module not available (modules/overlay/timer_overlay_tk.py).")

        w = self.state.timer_overlay
        if w is not None:
            try:
                if w.winfo_exists():
                    w.destroy()
            except Exception:
                pass
            self.state.timer_overlay = None
            return False

        self.state.timer_overlay = TimerOverlay(self.root, x=x, y=y)
        self.state.timer_overlay.start()
        return True

    def timers_enabled(self) -> bool:
        w = self.state.timer_overlay
        try:
            return bool(w is not None and w.winfo_exists())
        except Exception:
            return False
