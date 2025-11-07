#!/usr/bin/env python3


"""
verify-deps.py
- Vergleicht requirements.txt mit installierten Distributions im aktiven Interpreter/venv
- Option --install ermöglicht automatisches Nachinstallieren via pip
Usage:
  python scripts/verify-deps.py [--install]
"""
import sys
import subprocess
import argparse
import pkg_resources
from pathlib import Path

REQ_FILE = Path("requirements.txt")

def parse_requirements():
    if not REQ_FILE.exists():
        print("[WARN] requirements.txt not found.")
        return []
    lines = [l.strip() for l in REQ_FILE.read_text().splitlines() if l.strip() and not l.strip().startswith("#")]
    pkgs = []
    for l in lines:
        token = l.split(";",1)[0].strip()
        name = token.split("==")[0].split(">=")[0].split("<=")[0].split("><")[0].split("<")[0].strip()
        if name:
            pkgs.append(name)
    return pkgs

def installed_packages():
    dists = {d.project_name.lower() for d in pkg_resources.working_set}
    return dists

def install_missing(pkgs):
    missing = [p for p in pkgs if p.lower() not in installed_packages()]
    if not missing:
        print("[OK] All packages from requirements.txt are installed.")
        return 0
    print("[MISSING] The following packages are not installed:")
    for m in missing:
        print(f"  - {m}")
    cmd = [sys.executable, "-m", "pip", "install"] + missing
    print("\nSuggested command to install missing packages:")
    print(" ".join(cmd))
    return 1

def auto_install(missing):
    cmd = [sys.executable, "-m", "pip", "install"] + missing
    print("[INFO] Running:", " ".join(cmd))
    res = subprocess.run(cmd)
    return res.returncode

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install missing packages automatically")
    args = parser.parse_args()
    pkgs = parse_requirements()
    if not pkgs:
        print("[INFO] No packages listed in requirements.txt.")
        return 0
    dists = installed_packages()
    missing = [p for p in pkgs if p.lower() not in dists]
    if not missing:
        print("[OK] All requirements satisfied.")
        return 0
    print("[MISSING] Packages:", missing)
    if args.install:
        rc = auto_install(missing)
        return rc
    else:
        print("Run with --install to install the missing packages into the active environment.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
