# 🎯 Automatische Strategie-Auswahl Guide

**Intelligente Auswahl der optimalen Trading-Strategie basierend auf Backtest-Analyse**

---

## 📋 Inhaltsverzeichnis

- [Überblick](#überblick)
- [Funktionsweise](#funktionsweise)
- [Bewertungskriterien](#bewertungskriterien)
- [Verwendung](#verwendung)
- [Integration in Setup-Wizard](#integration-in-setup-wizard)
- [Kommandozeilen-Nutzung](#kommandozeilen-nutzung)
- [Konfiguration](#konfiguration)
- [Beispiele](#beispiele)
- [FAQ](#faq)

---

## Überblick

Die automatische Strategie-Auswahl analysiert alle verfügbaren Trading-Strategien mittels Backtest und empfiehlt die beste Strategie basierend auf robusten Performance-Metriken.

### Key Features

- ✅ **Automatischer Backtest** für alle Strategien mit gleichen Daten
- ✅ **Multi-Kriterien-Bewertung** (ROI, Sharpe, Calmar, Drawdown, Win Rate)
- ✅ **Gewichtetes Scoring-System** für objektive Vergleichbarkeit
- ✅ **Robustheit-Filter** (Mindestanzahl Trades)
- ✅ **Detailliertes Ranking** mit Export-Funktion
- ✅ **Integration in Setup-Wizard** als optionaler Schritt

### Analysierte Strategien

Die Auswahl umfasst derzeit:

1. **Golden Cross (50/200)** - Langfristige Trendfolge
2. **MA Crossover (20/50)** - Mittelfristige Trendfolge
3. **MA Crossover (10/30)** - Kurzfristige Trendfolge
4. **RSI Mean Reversion** - Überkauft/Überverkauft-Strategie
5. **RSI Conservative** - Konservative RSI-Variante
6. **EMA Crossover (9/21)** - Schnelle EMA-Crossover
7. **EMA Crossover (12/26)** - MACD-ähnliche EMA-Crossover
8. **Bollinger Bands** - Volatilitäts-basierte Strategie
9. **Bollinger Bands Wide** - Konservative BB-Variante

---

## Funktionsweise

### 1. Daten-Setup

Für den Backtest werden historische OHLCV-Daten verwendet:
- **Simulierte Daten**: Generierte Marktdaten mit realistischen Preisbewegungen
- **CSV-Import**: Echte historische Daten von Börsen

### 2. Backtest-Durchführung

Für jede Strategie wird ein vollständiger Backtest durchgeführt:
- Gleiche Daten für faire Vergleichbarkeit
- Gleiche Kapital- und Positionsgrößen
- Realistische Trade-Ausführung mit Entry/Exit-Signalen

### 3. Metriken-Berechnung

Für jede Strategie werden folgende Kennzahlen ermittelt:

| Metrik | Beschreibung | Ziel |
|--------|--------------|------|
| **ROI** | Return on Investment (%) | Maximieren |
| **Sharpe Ratio** | Risk-adjusted Returns | Maximieren |
| **Calmar Ratio** | Return / Max Drawdown | Maximieren |
| **Max Drawdown** | Maximaler Verlust (%) | Minimieren |
| **Win Rate** | Erfolgreiche Trades (%) | Maximieren |
| **Total Trades** | Anzahl der Trades | ≥ Minimum |

### 4. Scoring-Algorithmus

Die Strategien werden anhand eines gewichteten Scores bewertet:

```
Score = (ROI × 30%) + 
        (Sharpe × 25%) + 
        (Calmar × 20%) + 
        (Win Rate × 15%) + 
        (Drawdown × 10%)
```

**Gewichtung (Standard)**:
- ROI: 30% - Wichtigste Metrik für Profitabilität
- Sharpe Ratio: 25% - Risk-adjusted Performance
- Calmar Ratio: 20% - Return im Verhältnis zum Risiko
- Win Rate: 15% - Zuverlässigkeit der Strategie
- Max Drawdown: 10% - Risikominimierung

### 5. Robustheit-Filter

Strategien müssen folgende Kriterien erfüllen:
- **Mindestanzahl Trades**: Default 10 (konfigurierbar)
- **Erfolgreicher Backtest**: Keine Fehler bei Signalgenerierung
- **Valide Metriken**: Alle Kennzahlen berechenbar

---

## Bewertungskriterien

### Score-Normalisierung

Jede Metrik wird auf eine 0-100 Skala normalisiert:

#### ROI Normalisierung
```
ROI Score = min(max(ROI%, -50), 100)
```
- -50% oder schlechter: 0 Punkte
- 100% oder besser: 100 Punkte

#### Sharpe Ratio Normalisierung
```
Sharpe Score = min((Sharpe / 3.0) × 100, 100)
```
- 0: 0 Punkte
- 3.0 oder höher: 100 Punkte (exzellent)

#### Calmar Ratio Normalisierung
```
Calmar Score = min((Calmar / 3.0) × 100, 100)
```
- 0: 0 Punkte
- 3.0 oder höher: 100 Punkte

#### Win Rate Normalisierung
```
Win Rate Score = Win Rate % (direkt)
```
- 0%: 0 Punkte
- 100%: 100 Punkte

#### Max Drawdown Normalisierung (invertiert)
```
Drawdown Score = max(100 - (|DD| / 50.0) × 100, 0)
```
- -50% oder schlechter: 0 Punkte
- 0% (kein Drawdown): 100 Punkte

### Beispiel-Berechnung

**Strategie A:**
- ROI: 45% → 45 Punkte
- Sharpe: 2.1 → 70 Punkte
- Calmar: 2.5 → 83.3 Punkte
- Win Rate: 62% → 62 Punkte
- Max DD: -12% → 76 Punkte

**Gewichteter Score:**
```
Score = (45 × 0.30) + (70 × 0.25) + (83.3 × 0.20) + (62 × 0.15) + (76 × 0.10)
      = 13.5 + 17.5 + 16.66 + 9.3 + 7.6
      = 64.56
```

---

## Verwendung

### Als Standalone-Tool

```bash
# Windows (PowerShell)
.\venv\Scripts\python.exe strategy_selector.py

# Linux/macOS
python strategy_selector.py
```

Das Tool führt interaktiv durch den Auswahlprozess:

1. Datenquelle wählen (simuliert oder CSV)
2. Kapital und Trade-Size eingeben
3. Mindestanzahl Trades festlegen
4. Backtest läuft automatisch
5. Ranking wird angezeigt
6. Optional: Export als CSV

### Programmgesteuert

```python
from strategy_selector import StrategySelector
from utils import generate_sample_data

# Daten laden oder generieren
data = generate_sample_data(n_bars=2000, start_price=30000)

# Selector erstellen
selector = StrategySelector(
    initial_capital=10000.0,
    trade_size=100.0,
    min_trades=10
)

# Auswahl durchführen
best_name, best_score = selector.run_selection(data)

print(f"Empfohlene Strategie: {best_name}")
print(f"Score: {best_score.score:.2f}/100")
print(f"ROI: {best_score.roi:+.2f}%")

# Ranking exportieren
selector.export_ranking("data/strategy_ranking.csv")
```

---

## Integration in Setup-Wizard

Die Strategie-Auswahl ist in den Live-Trading Setup-Wizard integriert:

```bash
# Windows
.\venv\Scripts\python.exe scripts\setup_live.py

# Linux/macOS
python scripts/setup_live.py
```

### Workflow im Setup-Wizard

1. **API-Keys eingeben** (sicher in Credential Manager gespeichert)
2. **Strategie-Auswahl** (optional)
   - Automatischer Backtest aller Strategien
   - Empfehlung der besten Strategie
   - User kann Empfehlung akzeptieren oder überschreiben
3. **Risk-Parameter konfigurieren**
4. **Config-Datei erstellen** (`config/live_risk.yaml`)

### Strategie-Auswahl überspringen

Der Schritt kann übersprungen werden:
- Bei Prompt "Strategie-Auswahl durchführen? (j/n)" mit "n" antworten
- Strategie wird dann manuell aus Liste gewählt
- Standard: "Golden Cross (50/200)"

---

## Kommandozeilen-Nutzung

### Mit simulierten Daten

```bash
# Kurze Simulation (1000 Bars)
.\venv\Scripts\python.exe strategy_selector.py
# Wähle [1] bei Prompt

# Lange Simulation (2000 Bars) - Empfohlen
.\venv\Scripts\python.exe strategy_selector.py
# Wähle [2] bei Prompt
```

### Mit echten historischen Daten

```bash
.\venv\Scripts\python.exe strategy_selector.py
# Wähle [3] bei Prompt
# Pfad zur CSV angeben (z.B. data/BTCUSDT_1h.csv)
```

### CSV-Format für Import

```csv
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,30000.0,30500.0,29800.0,30200.0,1000.0
2024-01-01 01:00:00,30200.0,30400.0,30000.0,30300.0,1200.0
...
```

---

## Konfiguration

### Custom Gewichtung

Eigene Gewichtung der Metriken festlegen:

```python
custom_weights = {
    'roi': 0.40,           # Mehr Fokus auf ROI
    'sharpe_ratio': 0.30,  # Mehr Fokus auf risk-adjusted returns
    'calmar_ratio': 0.15,
    'win_rate': 0.10,
    'max_drawdown': 0.05
}

selector = StrategySelector(weights=custom_weights)
```

### Mindestanzahl Trades anpassen

```python
# Strengeres Kriterium (mehr Trades erforderlich)
selector = StrategySelector(min_trades=20)

# Lockereres Kriterium (für kurze Zeiträume)
selector = StrategySelector(min_trades=5)
```

### Kapital und Trade-Size

```python
# Höheres Kapital und größere Positionen
selector = StrategySelector(
    initial_capital=50000.0,
    trade_size=500.0
)
```

---

## Beispiele

### Beispiel 1: Standard-Auswahl

```python
from strategy_selector import StrategySelector
from utils import generate_sample_data

# Daten generieren
data = generate_sample_data(n_bars=2000, start_price=30000)

# Standard-Selector
selector = StrategySelector()

# Auswahl durchführen
best_name, best_score = selector.run_selection(data)

# Ergebnisse
print(f"\n🏆 Beste Strategie: {best_name}")
print(f"Score: {best_score.score:.2f}/100")
print(f"ROI: {best_score.roi:+.2f}%")
print(f"Sharpe: {best_score.sharpe_ratio:.2f}")
print(f"Max DD: {best_score.max_drawdown:.2f}%")
print(f"Win Rate: {best_score.win_rate:.1f}%")
```

### Beispiel 2: Konservative Auswahl

```python
# Fokus auf niedrigen Drawdown und hohe Sharpe Ratio
conservative_weights = {
    'roi': 0.20,
    'sharpe_ratio': 0.35,
    'calmar_ratio': 0.25,
    'win_rate': 0.10,
    'max_drawdown': 0.10
}

selector = StrategySelector(
    weights=conservative_weights,
    min_trades=15  # Höhere Robustheit
)

best_name, best_score = selector.run_selection(data)
```

### Beispiel 3: Aggressive Auswahl

```python
# Fokus auf maximalen ROI
aggressive_weights = {
    'roi': 0.50,
    'sharpe_ratio': 0.20,
    'calmar_ratio': 0.15,
    'win_rate': 0.10,
    'max_drawdown': 0.05
}

selector = StrategySelector(
    weights=aggressive_weights,
    min_trades=8  # Niedrigere Robustheit
)

best_name, best_score = selector.run_selection(data)
```

---

## FAQ

### Wie lange dauert die Strategie-Auswahl?

**Antwort**: Bei simulierten Daten (2000 Bars) ca. 1-3 Minuten, abhängig von:
- Anzahl der Strategien
- Datenmenge
- Systemleistung

### Kann ich eigene Strategien hinzufügen?

**Ja!** In `strategy_selector.py` die Methode `setup_strategies()` erweitern:

```python
def setup_strategies(self) -> Dict[str, Any]:
    strategies = {
        # Bestehende Strategien...
        
        # Eigene Strategie hinzufügen
        'My Custom Strategy': MyCustomStrategy({
            'param1': value1,
            'param2': value2
        })
    }
    return strategies
```

### Wie zuverlässig ist die Empfehlung?

**Hinweis**: Die Empfehlung basiert auf historischen Daten (Backtest). 

**Wichtig**:
- ✅ Gute Indikation für relative Performance
- ✅ Objektivere Auswahl als manuelle Entscheidung
- ⚠️ Keine Garantie für zukünftige Performance
- ⚠️ Past performance is not indicative of future results

**Best Practice**:
- Strategie in Dry-Run/Testnet testen
- Mit minimalem Kapital starten
- Performance regelmäßig überprüfen

### Kann ich die Gewichtung ändern?

**Ja!** Die Gewichtung kann beim Erstellen des Selectors angepasst werden:

```python
my_weights = {
    'roi': 0.35,
    'sharpe_ratio': 0.30,
    'calmar_ratio': 0.20,
    'win_rate': 0.10,
    'max_drawdown': 0.05
}

selector = StrategySelector(weights=my_weights)
```

### Was passiert wenn keine Strategie genug Trades hat?

**Antwort**: Der Selector wirft einen `ValueError` mit der Meldung "Keine gültigen Strategien gefunden".

**Lösung**:
- Mehr historische Daten verwenden
- `min_trades` Parameter reduzieren
- Andere Strategien hinzufügen

### Werden die Ergebnisse gespeichert?

**Ja!** Mit der `export_ranking()` Methode:

```python
selector.export_ranking("data/strategy_ranking.csv")
```

Enthält:
- Strategy Name
- Score
- Alle Performance-Metriken
- Sortiert nach Score

### Kann ich echte Binance-Daten verwenden?

**Ja!** Historische Daten von Binance laden und als CSV importieren:

```python
# Alternativ mit Binance API (nicht im Selector enthalten)
from binance.client import Client

client = Client(api_key, api_secret)
klines = client.get_historical_klines(
    "BTCUSDT", 
    Client.KLINE_INTERVAL_1HOUR, 
    "1 Jan, 2024", 
    "1 Feb, 2024"
)

# Konvertiere zu DataFrame und speichere als CSV
# Dann mit strategy_selector.py laden
```

---

## Weiterführende Dokumentation

- [LIVE_TRADING_SETUP_GUIDE.md](LIVE_TRADING_SETUP_GUIDE.md) - Komplettes Live-Trading Setup
- [BACKTESTING_GUIDE.md](BACKTESTING_GUIDE.md) - Backtest-Grundlagen
- [PERFORMANCE_METRICS_GUIDE.md](PERFORMANCE_METRICS_GUIDE.md) - Detaillierte Metrik-Erklärungen
- [BATCH_BACKTESTING_README.md](BATCH_BACKTESTING_README.md) - Batch-Backtest Details

---

## Support

Bei Fragen oder Problemen:
1. Dokumentation durchlesen
2. Issue auf GitHub erstellen
3. Logs prüfen (`data/` Verzeichnis)

---

**Made for Windows ⭐ | Automatische Strategie-Auswahl | ROI-Optimiert**
