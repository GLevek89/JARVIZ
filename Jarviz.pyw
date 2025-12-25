# JARVIZ launcher (no console)
# Double-click friendly entrypoint with crash logging + visible error dialogs.
import os
import sys
import traceback

# Ensure project root is on sys.path (this file lives in ./jarviz/)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _write_crash_log(exc: BaseException, extra_text: str = "") -> str:
    """Write crash/install output to %APPDATA%\\JARVIZ\\logs and return the log path."""
    try:
        base = os.environ.get("APPDATA") or ROOT
        log_dir = os.path.join(base, "JARVIZ", "logs")
        os.makedirs(log_dir, exist_ok=True)

        ts = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(log_dir, f"crash_{ts}.log")

        with open(log_path, "w", encoding="utf-8") as f:
            f.write("JARVIZ crash log\n\n")
            if extra_text:
                f.write(extra_text.strip() + "\n\n")
            f.write(repr(exc) + "\n\n")
            f.write(traceback.format_exc())

        return log_path
    except Exception:
        return ""


def _show_error(title: str, msg: str) -> None:
    """Prefer a Qt dialog if PySide6 is importable; fallback to Tk messagebox."""
    # Qt popup (preferred)
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox  # type: ignore

        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        QMessageBox.critical(None, title, msg)
        return
    except Exception:
        pass

    # Tk fallback popup
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, msg)
        try:
            root.destroy()
        except Exception:
            pass
    except Exception:
        pass


def _pip_install_requirements() -> tuple[bool, str]:
    """Attempt to install runtime requirements using the current Python interpreter."""
    import subprocess

    req_file = os.path.join(ROOT, "requirements.txt")
    if not os.path.exists(req_file):
        return False, f"requirements.txt not found at:\n{req_file}"

    cmd = [sys.executable, "-m", "pip", "install", "-r", req_file, "--upgrade"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True)
        out = ((p.stdout or "") + "\n" + (p.stderr or "")).strip()
        return (p.returncode == 0), out
    except Exception as e:
        return False, f"Failed to run pip:\n{e}"


def _ensure_deps_or_exit() -> None:
    """If GUI deps are missing, offer to install requirements.txt then exit."""
    missing: list[str] = []

    try:
        import PySide6  # noqa: F401
    except ModuleNotFoundError:
        missing.append("PySide6")

    # Needed for capture-only live preview (OCR Preview tab)
    try:
        import mss  # noqa: F401
    except ModuleNotFoundError:
        missing.append("mss")

    if not missing:
        return

    msg = (
        "Missing dependency(s): " + ", ".join(missing) + "\n\n"
        "Jarviz can attempt to install required dependencies now.\n"
        "After it finishes, relaunch Jarviz.\n\n"
        "If auto-install fails, run this in a terminal from the Jarviz folder:\n"
        f"  {sys.executable} -m pip install -r requirements.txt --upgrade"
    )

    _show_error("JARVIZ Dependencies Missing", msg)

    ok, out = _pip_install_requirements()
    if ok:
        _show_error("JARVIZ", "Dependencies installed successfully.\n\nPlease relaunch Jarviz.")
        sys.exit(0)

    # Save the pip output to a log so it doesn't get lost
    log_path = _write_crash_log(RuntimeError("pip install failed"), extra_text=out)
    extra = f"\n\nInstall log saved to:\n{log_path}" if log_path else ""
    _show_error(
        "JARVIZ Dependency Install Failed",
        "Dependency install failed.\n\n" + (out[:1600] if out else "(no output)") + extra,
    )
    sys.exit(1)


def _run() -> None:
    _ensure_deps_or_exit()
    from main import main  # import after deps are present
    main()


if __name__ == "__main__":
    try:
        _run()
    except Exception as e:
        log_path = _write_crash_log(e)
        extra = f"\n\nCrash log saved to:\n{log_path}" if log_path else ""
        _show_error("JARVIZ crashed on startup", f"{e}{extra}")
        sys.exit(1)
