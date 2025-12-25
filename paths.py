import os
import sys

def app_dir() -> str:
    # Works for both source run and PyInstaller.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def data_dir() -> str:
    """User-writable data directory."""
    base = os.environ.get('APPDATA') or os.path.expanduser('~')
    d = os.path.join(base, 'JARVIZ')
    os.makedirs(d, exist_ok=True)
    return d
