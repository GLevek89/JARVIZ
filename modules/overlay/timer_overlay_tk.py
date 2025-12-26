from __future__ import annotations

import tkinter as tk
from datetime import datetime

from modules.timers.d4_event_schedule import fetch_events, next_by_kind


def _fmt_countdown(target: datetime) -> str:
    now = datetime.now(tz=target.tzinfo)
    delta = target - now
    total = int(delta.total_seconds())
    if total <= 0:
        return "NOW"

    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60

    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


class TimerOverlay(tk.Toplevel):
    def __init__(self, master: tk.Tk, x: int = 30, y: int = 30):
        super().__init__(master)

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.85)
        self.configure(bg="#0b0f14")
        self.geometry(f"+{x}+{y}")

        self.label = tk.Label(
            self,
            text="Loading timers...",
            font=("Segoe UI", 12, "bold"),
            fg="#d7e3ff",
            bg="#0b0f14",
            justify="left",
        )
        self.label.pack(padx=10, pady=8)

        self._drag_data = None
        self.bind("<ButtonPress-1>", self._on_drag_start)
        self.bind("<B1-Motion>", self._on_drag_move)

    def _on_drag_start(self, e):
        self._drag_data = (e.x_root, e.y_root, self.winfo_x(), self.winfo_y())

    def _on_drag_move(self, e):
        if not self._drag_data:
            return
        x0, y0, wx, wy = self._drag_data
        dx = e.x_root - x0
        dy = e.y_root - y0
        self.geometry(f"+{wx + dx}+{wy + dy}")

    def start(self):
        self._tick()

    def _tick(self):
        try:
            events = fetch_events(limit=40)
            nxt = next_by_kind(events)

            lines = []

            if nxt.get("helltide"):
                lines.append(f"Helltide: {_fmt_countdown(nxt['helltide'].starts_at)}")
            if nxt.get("legion"):
                lines.append(f"Legion:   {_fmt_countdown(nxt['legion'].starts_at)}")
            if nxt.get("worldboss"):
                wb = nxt["worldboss"]
                boss = wb.label or "World Boss"
                lines.append(f"WB ({boss}): {_fmt_countdown(wb.starts_at)}")

            if not lines:
                lines = ["No upcoming events"]

            self.label.config(text="\n".join(lines))
        except Exception as ex:
            self.label.config(text=f"Timer error:\n{ex}")

        self.after(1000, self._tick)
