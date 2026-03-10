#!/usr/bin/env python3
"""
SubtitleFinder – DaVinci Resolve Installer
Works on both DaVinci Resolve (free) and DaVinci Resolve Studio (paid).

The script installs subtitle-search.py into the correct Fusion/Scripts/Edit
folder so it appears under  Workspace > Scripts  inside Resolve.

macOS / Linux:  python3 install.py
Windows:        python install.py          (no admin rights needed)

To uninstall:   python3 install.py --uninstall
"""

import os
import sys
import shutil
import platform

SCRIPT_NAME = "SubtitleFinder.py"   # Name that appears in the Scripts menu

# ── Resolve's script drop-in folder (works on free AND paid) ──────────────────
# Scripts placed here appear under  Workspace > Scripts > Edit  in every page.
# Source: Blackmagic DaVinci Resolve Scripting README (v20)
INSTALL_DIRS = {
    "Darwin": os.path.expanduser(
        "~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Edit"
    ),
    "Windows": os.path.join(
        os.environ.get("APPDATA", ""),
        r"Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Edit",
    ),
    "Linux": os.path.expanduser(
        "~/.local/share/DaVinciResolve/Fusion/Scripts/Edit"
    ),
}

# Fallback system-wide Linux path
LINUX_SYSTEM_PATH = "/opt/resolve/Fusion/Scripts/Edit"


def get_install_dir():
    system = platform.system()
    path = INSTALL_DIRS.get(system)
    if system == "Linux" and path and not os.path.exists(os.path.dirname(path)):
        # Some installations use the system-wide path
        path = LINUX_SYSTEM_PATH
    return path, system


def install():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_py  = os.path.join(script_dir, "SubtitleFinder", "subtitle-search.py")

    if not os.path.isfile(source_py):
        print(f"[ERROR] Cannot find  SubtitleFinder/subtitle-search.py  next to this installer.")
        print(f"        Expected: {source_py}")
        return False

    install_dir, system = get_install_dir()
    if not install_dir:
        print(f"[ERROR] Unsupported OS: {system}")
        return False

    dest = os.path.join(install_dir, SCRIPT_NAME)

    print(f"Installing SubtitleFinder…")
    print(f"  Source : {source_py}")
    print(f"  Target : {dest}")

    try:
        os.makedirs(install_dir, exist_ok=True)
        shutil.copy2(source_py, dest)

        print()
        print("=" * 56)
        print("  SUCCESS – SubtitleFinder installed!")
        print("=" * 56)
        print()
        print("How to run it:")
        print("  1. Open (or restart) DaVinci Resolve.")
        print("  2. Go to  Workspace > Scripts > Edit > SubtitleFinder")
        print("     (or just  Workspace > Scripts  on some versions)")
        print()
        print("NOTE – Free version users: if the script shows an error")
        print("  about the Resolve object being None, see the README for")
        print("  the one-time Preferences change you need to make.")
        print()
        return True

    except PermissionError:
        print()
        print("[ERROR] Permission denied writing to:")
        print(f"        {install_dir}")
        if system != "Windows":
            print("        Try:  sudo python3 install.py")
        return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def uninstall():
    install_dir, system = get_install_dir()
    if not install_dir:
        print(f"[ERROR] Unsupported OS: {system}")
        return

    dest = os.path.join(install_dir, SCRIPT_NAME)
    if not os.path.isfile(dest):
        print("SubtitleFinder does not appear to be installed.")
        return

    try:
        os.remove(dest)
        print(f"Removed: {dest}")
        print("SubtitleFinder uninstalled.")
    except PermissionError:
        print("[ERROR] Permission denied. Try sudo python3 install.py --uninstall")
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        uninstall()
    else:
        install()
