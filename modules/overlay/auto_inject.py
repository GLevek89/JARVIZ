from __future__ import annotations

"""
Import this module once during app startup to auto-add an OVERLAY page (best effort).

It will only act if:
- customtkinter is installed AND
- the running app exposes a CTkTabview at app.tabs or app.tabview AND
- the app provides a global app instance via a known name.

This module is safe to import even if conditions are not met.
"""

def try_inject(app) -> bool:
    try:
        from modules.overlay.overlay_page_ctk import install_overlay_page
        return install_overlay_page(app)
    except Exception:
        return False
