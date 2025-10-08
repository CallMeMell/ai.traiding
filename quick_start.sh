#!/bin/bash

echo "========================================"
echo " Multi-Strategy Trading Bot"
echo " Quick Start Script"
echo "========================================"
echo

# Prüfe ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 ist nicht installiert!"
    echo "Bitte installiere Python 3.8+ mit: sudo apt install python3"
    exit 1
fi

echo "[1/4] Erstelle virtuelle Umgebung..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "     Virtual environment erstellt!"
else
    echo "     Virtual environment existiert bereits."
fi

echo
echo "[2/4] Aktiviere virtuelle Umgebung..."
source venv/bin/activate

echo
echo "[3/4] Installiere Dependencies..."
pip install -r requirements.txt --quiet

echo
echo "[4/4] Erstelle Verzeichnisse..."
mkdir -p data logs config

echo
echo "========================================"
echo " Setup abgeschlossen!"
echo "========================================"
echo
echo "Verfügbare Befehle:"
echo "  python main.py        - Starte Live-Trading"
echo "  python backtester.py  - Führe Backtest durch"
echo
echo "Hinweis: Virtual environment ist aktiv."
echo "Zum Deaktivieren: deactivate"
echo
