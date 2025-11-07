#!/usr/bin/env python3
"""
env-check.py
- Prüft Python-Version, venv-Ordner, pip-Verfügbarkeit
- Gibt klare, plattform-spezifische Hinweise aus
Exit-Codes:
 0 = OK
 10 = Python nicht gefunden / falsche Version
 11 = venv fehlt
 12 = pip fehlt
"""
import sys
import os
import shutil
import subprocess

MIN_PY = (3, 8)

def check_python():
    if sys.version_info < MIN_PY:
        print(f"[ERROR] Python {MIN_PY[0]}.{MIN_PY[1]}+ required. Gefundene Version: {sys.version_info.major}.{sys.version_info.minor}")
        return 10
    print(f"[OK] Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return 0

def check_venv():
    venv_dirs = ["venv", ".venv"]
    for d in venv_dirs:
        if os.path.isdir(d):
            print(f"[OK] Virtualenv found: {d}")
            return 0
    print("[WARN] Virtual environment not found (common names: venv, .venv). Start-Skripte können es automatisch anlegen.")
    return 11

def check_pip():
    pip = shutil.which("pip") or shutil.which("pip3")
    if pip is None:
        print("[ERROR] pip not found in PATH.")
        return 12
    try:
        out = subprocess.check_output([pip, "--version"], stderr=subprocess.STDOUT, text=True)
        print(f"[OK] {out.strip()}")
        return 0
    except Exception:
        print("[ERROR] pip exists but --version failed.")
        return 12

def main():
    rc = 0
    rc = max(rc, check_python())
    rc = max(rc, check_venv())
    rc = max(rc, check_pip())
    if rc == 0:
        print("\nAll checks passed. To create venv: python -m venv venv && source venv/bin/activate (Linux/Mac) or venv\Scripts\activate (Windows)")
    else:
        if rc == 10:
            print("\nAction: Installiere Python 3.8+:
 - Windows: https://www.python.org/downloads/
 - macOS (Homebrew): brew install python
 - Ubuntu: sudo apt update && sudo apt install python3 python3-venv python3-pip")
        if rc == 11:
            print("\nAction: Erstelle virtuelles Environment:
 python -m venv venv
 Linux/macOS: source venv/bin/activate
 Windows (PowerShell): .\venv\Scripts\Activate.ps1")
        if rc == 12:
            print("\nAction: Stelle sicher, dass pip verfügbar ist. Bei venv: activate venv, dann python -m pip install -U pip")
    sys.exit(rc)

if __name__ == "__main__":
    main()