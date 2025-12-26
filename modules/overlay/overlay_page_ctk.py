from __future__ import annotations

from typing import Optional

def install_overlay_page(app) -> bool:
    """
    Best-effort injection:
    - If app has a CTkTabview at app.tabs or app.tabview, add an "OVERLAY" tab.
    - If already exists, do nothing.
    Returns True if installed successfully.
    """
    try:
        import customtkinter as ctk
    except Exception:
        return False

    tabview = getattr(app, "tabs", None) or getattr(app, "tabview", None)
    if tabview is None:
        return False

    # Try to detect existing tabs API
    try:
        existing = tabview._tab_dict.keys()  # internal but stable in CTkTabview
        if "OVERLAY" in existing:
            tab = tabview.tab("OVERLAY")
        else:
            tab = tabview.add("OVERLAY")
    except Exception:
        # Fallback: maybe different API
        try:
            tab = tabview.add("OVERLAY")
        except Exception:
            return False

    # Lazy import to avoid hard dependency if not used
    from modules.overlay.overlay_controller import OverlayController

    if not hasattr(app, "overlay_controller") or getattr(app, "overlay_controller") is None:
        # Prefer root attribute if present, else app itself for Tk master
        root = getattr(app, "root", None) or getattr(app, "master", None) or getattr(app, "window", None) or app
        app.overlay_controller = OverlayController(root)

    controller = app.overlay_controller

    # Build UI
    for child in tab.winfo_children():
        child.destroy()

    tab.grid_columnconfigure(0, weight=1)

    title = ctk.CTkLabel(tab, text="OVERLAY", font=("Segoe UI", 18, "bold"))
    title.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 6))

    sub = ctk.CTkLabel(
        tab,
        text="Overlay tools you can enable in-game. This page will grow over time.",
        font=("Segoe UI", 12),
        justify="left",
    )
    sub.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

    card = ctk.CTkFrame(tab, corner_radius=12)
    card.grid(row=2, column=0, sticky="ew", padx=16, pady=10)
    card.grid_columnconfigure(0, weight=1)

    card_title = ctk.CTkLabel(card, text="Event Timers", font=("Segoe UI", 14, "bold"))
    card_title.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

    card_desc = ctk.CTkLabel(
        card,
        text="Helltide, Legion, World Boss countdown overlay.\nDrag the overlay to reposition.",
        font=("Segoe UI", 12),
        justify="left",
    )
    card_desc.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))

    status_var = ctk.StringVar(value="Status: OFF")
    status = ctk.CTkLabel(card, textvariable=status_var, font=("Segoe UI", 12))
    status.grid(row=2, column=0, sticky="w", padx=14, pady=(0, 12))

    def _refresh_status():
        status_var.set("Status: ON" if controller.timers_enabled() else "Status: OFF")

    def _toggle():
        try:
            controller.toggle_timers(x=30, y=30)
        except Exception as ex:
            status_var.set(f"Status: ERROR - {ex}")
            return
        _refresh_status()

    btn = ctk.CTkButton(card, text="Toggle Timers Overlay", command=_toggle)
    btn.grid(row=3, column=0, sticky="w", padx=14, pady=(0, 14))

    _refresh_status()
    return True
