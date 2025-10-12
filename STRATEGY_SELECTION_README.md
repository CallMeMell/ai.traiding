# 🎯 Strategie-Auswahl - Quick Reference

**Automatische Auswahl der optimalen Trading-Strategie**

---

## 🚀 Schnellstart

### 1. Demo ausführen

```powershell
# Windows
.\venv\Scripts\python.exe demo_strategy_selection.py

# Linux/macOS  
python demo_strategy_selection.py
```

### 2. Standalone-Tool

```powershell
# Windows
.\venv\Scripts\python.exe strategy_selector.py

# Linux/macOS
python strategy_selector.py
```

### 3. In Setup-Wizard (Live-Trading)

```powershell
# Windows
.\scripts\setup_live.ps1

# Linux/macOS
./scripts/setup_live.sh
```

---

## 📊 Was macht es?

Die automatische Strategie-Auswahl:

1. ✅ **Testet alle Strategien** mit gleichen historischen Daten
2. ✅ **Berechnet Metriken** (ROI, Sharpe, Calmar, Drawdown, Win Rate)
3. ✅ **Erstellt Ranking** mit gewichtetem Scoring-System
4. ✅ **Empfiehlt beste Strategie** basierend auf robusten Kriterien
5. ✅ **Exportiert Ergebnisse** als CSV für weitere Analyse

---

## 🎲 Verfügbare Strategien

| Strategie | Typ | Timeframe |
|-----------|-----|-----------|
| **Golden Cross (50/200)** | Trend Following | Langfristig |
| **MA Crossover (20/50)** | Trend Following | Mittelfristig |
| **MA Crossover (10/30)** | Trend Following | Kurzfristig |
| **RSI Mean Reversion** | Mean Reversion | Mittelfristig |
| **RSI Conservative** | Mean Reversion | Mittelfristig |
| **EMA Crossover (9/21)** | Trend Following | Schnell |
| **EMA Crossover (12/26)** | Trend Following | MACD-ähnlich |
| **Bollinger Bands** | Volatility | Mittelfristig |
| **Bollinger Bands Wide** | Volatility | Konservativ |

---

## 📈 Bewertungs-Kriterien

### Gewichtung (Standard)

```
Score = (ROI × 30%) + (Sharpe × 25%) + (Calmar × 20%) + (Win Rate × 15%) + (Drawdown × 10%)
```

| Metrik | Gewicht | Beschreibung |
|--------|---------|--------------|
| **ROI** | 30% | Return on Investment |
| **Sharpe Ratio** | 25% | Risk-adjusted Returns |
| **Calmar Ratio** | 20% | Return / Max Drawdown |
| **Win Rate** | 15% | Erfolgsquote |
| **Max Drawdown** | 10% | Maximaler Verlust (invertiert) |

### Mindestanforderungen

- ✅ Mindestens 10 Trades (konfigurierbar)
- ✅ Erfolgreicher Backtest ohne Fehler
- ✅ Alle Metriken berechenbar

---

## 🔧 Programmgesteuerte Nutzung

```python
from strategy_selector import StrategySelector
from utils import generate_sample_data

# 1. Daten laden
data = generate_sample_data(n_bars=2000, start_price=30000)

# 2. Selector erstellen
selector = StrategySelector(
    initial_capital=10000.0,
    trade_size=100.0,
    min_trades=10
)

# 3. Auswahl durchführen
best_name, best_score = selector.run_selection(data)

# 4. Ergebnisse anzeigen
print(f"Beste Strategie: {best_name}")
print(f"Score: {best_score.score:.2f}/100")
print(f"ROI: {best_score.roi:+.2f}%")

# 5. Ranking exportieren
selector.export_ranking("data/strategy_ranking.csv")
```

---

## 🎨 Custom Gewichtung

```python
# Konservativ (niedriger Drawdown wichtiger)
conservative_weights = {
    'roi': 0.20,
    'sharpe_ratio': 0.35,
    'calmar_ratio': 0.25,
    'win_rate': 0.10,
    'max_drawdown': 0.10
}

selector = StrategySelector(weights=conservative_weights)

# Aggressiv (maximaler ROI wichtiger)
aggressive_weights = {
    'roi': 0.50,
    'sharpe_ratio': 0.20,
    'calmar_ratio': 0.15,
    'win_rate': 0.10,
    'max_drawdown': 0.05
}

selector = StrategySelector(weights=aggressive_weights)
```

---

## 📁 Output-Dateien

### Ranking CSV

`data/strategy_ranking.csv` enthält:

- Strategy Name
- Score (0-100)
- ROI (%)
- Sharpe Ratio
- Calmar Ratio
- Max Drawdown (%)
- Win Rate (%)
- Total Trades
- Avg Trade ($)
- Final Capital ($)

Sortiert nach Score (höchster zuerst).

---

## ⚙️ Konfiguration

### Parameter

```python
StrategySelector(
    initial_capital=10000.0,  # Startkapital für Backtest
    trade_size=100.0,         # Handelsgröße
    min_trades=10,            # Mindestanzahl Trades
    weights={...}             # Custom Gewichtung (optional)
)
```

### Robustheit-Filter

```python
# Strenger (mehr Trades erforderlich)
selector = StrategySelector(min_trades=20)

# Lockerer (für kurze Zeiträume)
selector = StrategySelector(min_trades=5)
```

---

## 💡 Best Practices

### ✅ Do's

- ✅ Verwende genug historische Daten (mind. 500-1000 Bars)
- ✅ Teste empfohlene Strategie im Dry-Run
- ✅ Überprüfe alle Top-3 Strategien
- ✅ Berücksichtige deine Risikotoleranz
- ✅ Exportiere und archiviere Ranking-Ergebnisse

### ❌ Don'ts

- ❌ Nicht blind der Empfehlung folgen ohne Testing
- ❌ Nicht mit zu wenig Daten (< 200 Bars)
- ❌ Nicht die Gewichtung zu extrem anpassen
- ❌ Nicht vergessen: Past performance ≠ Future results
- ❌ Nicht ohne Dry-Run direkt live gehen

---

## 🔍 Troubleshooting

### Problem: "Keine gültigen Strategien gefunden"

**Lösung:**
```python
# Option 1: Reduziere Mindestanzahl
selector = StrategySelector(min_trades=5)

# Option 2: Mehr Daten verwenden
data = generate_sample_data(n_bars=2000)
```

### Problem: Strategie-Import-Fehler

**Lösung:**
```powershell
# Stelle sicher dass alle Dependencies installiert sind
pip install -r requirements.txt

# Prüfe dass alle Strategie-Module vorhanden sind
python -c "from strategy import *; from golden_cross_strategy import *"
```

### Problem: Sehr lange Laufzeit

**Lösung:**
```python
# Reduziere Anzahl der Bars
data = generate_sample_data(n_bars=500)

# Oder reduziere min_trades
selector = StrategySelector(min_trades=5)
```

---

## 📚 Weiterführende Dokumentation

- [STRATEGY_SELECTION_GUIDE.md](STRATEGY_SELECTION_GUIDE.md) - Detaillierte Dokumentation
- [LIVE_TRADING_SETUP_GUIDE.md](LIVE_TRADING_SETUP_GUIDE.md) - Live-Trading Setup
- [BACKTESTING_GUIDE.md](BACKTESTING_GUIDE.md) - Backtest-Grundlagen
- [PERFORMANCE_METRICS_GUIDE.md](PERFORMANCE_METRICS_GUIDE.md) - Metriken-Details

---

## 📞 Support

Bei Fragen oder Problemen:

1. 📖 Lies die ausführliche Dokumentation
2. 🐛 Erstelle ein Issue auf GitHub
3. 📊 Prüfe die Logs im `logs/` Verzeichnis

---

**Made for Windows ⭐ | Automatische Strategie-Auswahl | ROI-Optimiert**
