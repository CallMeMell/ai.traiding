#!/bin/bash
# start_automated_workflow.sh - Quick Start für Automatisierten Workflow
# ========================================================================

echo "=============================================================================="
echo "🤖 AUTOMATISIERTER TRADING-BOT WORKFLOW"
echo "=============================================================================="
echo ""
echo "Dieses Skript startet den vollautomatischen Workflow zur Vorbereitung"
echo "des KI-Trading-Bots für den Echtgeld-Einsatz."
echo ""
echo "Workflow-Phasen:"
echo "  1. Datenanalyse und -kreierung"
echo "  2. Strategie-Optimierung"
echo "  3. API-Vorbereitung"
echo "  4. Live-View Session Integration"
echo "  5. Finale Validierung"
echo ""
echo "=============================================================================="
echo ""

# Prüfe ob Python verfügbar ist
if ! command -v python &> /dev/null; then
    echo "❌ Python nicht gefunden. Bitte installiere Python 3.9+."
    exit 1
fi

# Prüfe ob Virtual Environment aktiviert ist
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Keine Virtual Environment aktiviert."
    echo "Empfehlung: Aktiviere Virtual Environment vor dem Start."
    echo ""
    read -p "Fortfahren ohne Virtual Environment? (j/n): " response
    if [[ "$response" != "j" ]]; then
        echo "Abgebrochen."
        exit 0
    fi
fi

# Erstelle notwendige Verzeichnisse
mkdir -p data/workflow_sessions
mkdir -p logs

# Starte Workflow
echo ""
echo "🚀 Starte Automatisierten Workflow..."
echo ""

python demo_automated_workflow.py

echo ""
echo "=============================================================================="
echo "✅ Workflow-Skript beendet"
echo "=============================================================================="
echo ""
echo "📁 Session-Dateien: data/workflow_sessions/"
echo "📝 Log-Dateien: logs/trading_bot.log"
echo ""
echo "Weitere Informationen: AUTOMATED_WORKFLOW_GUIDE.md"
echo ""
