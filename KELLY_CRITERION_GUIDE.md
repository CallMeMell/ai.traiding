# 📊 Kelly Criterion Position Sizing Guide

## Übersicht

Das **Kelly Criterion** ist eine mathematische Formel zur Berechnung der optimalen Positionsgröße bei Trades. Es maximiert das geometrische Wachstum des Kapitals langfristig, basierend auf:
- **Gewinnwahrscheinlichkeit** (Win Rate)
- **Durchschnittlicher Gewinn** pro Trade
- **Durchschnittlicher Verlust** pro Trade

## Die Kelly-Formel

```
f* = (p × b - q) / b

wobei:
- f* = Optimaler Kapitalanteil für Trade (0.0 bis 1.0)
- p  = Gewinnwahrscheinlichkeit (Win Rate)
- q  = Verlustwahrscheinlichkeit (1 - Win Rate)
- b  = Win/Loss Ratio (Avg Win / Avg Loss)
```

## Beispiel-Berechnung

**Szenario:**
- Win Rate: 60% (p = 0.6)
- Avg Win: $150
- Avg Loss: $100
- Win/Loss Ratio: 1.5 (b = 150/100)

**Berechnung:**
```
f* = (0.6 × 1.5 - 0.4) / 1.5
f* = (0.9 - 0.4) / 1.5
f* = 0.5 / 1.5
f* = 0.333... = 33.33%
```

**Interpretation:** Full Kelly empfiehlt 33.33% des Kapitals pro Trade.

## Konfiguration

### In `config.py` / `.env`

```python
# Kelly Criterion Position Sizing
enable_kelly_criterion: bool = False      # Kelly aktivieren/deaktivieren
kelly_fraction: float = 0.5              # 0.5 = Half Kelly (konservativ)
kelly_max_position_pct: float = 0.25     # Max 25% des Kapitals
kelly_lookback_trades: int = 20          # Anzahl vergangener Trades für Berechnung
```

### Empfohlene Einstellungen

| Setting | Wert | Beschreibung |
|---------|------|--------------|
| `kelly_fraction` | 0.5 | **Half Kelly** - Konservativer Ansatz, reduziert Risiko |
| `kelly_max_position_pct` | 0.25 | **25% Maximum** - Verhindert zu große Einzelpositionen |
| `kelly_lookback_trades` | 20 | **Mindestens 20 Trades** - Statistisch aussagekräftig |

## Verwendung

### 1. Aktivierung in Config

```python
from config import TradingConfig

config = TradingConfig()
config.enable_kelly_criterion = True
config.kelly_fraction = 0.5  # Half Kelly
config.kelly_max_position_pct = 0.25  # Max 25%

# Validierung
is_valid, error = config.validate()
if is_valid:
    print("✓ Kelly Criterion aktiviert")
```

### 2. Verwendung in Strategie

```python
from lsob_strategy import LSOBStrategy

# Strategy mit Kelly
strategy = LSOBStrategy(params)

# Position Size mit Kelly berechnen
position_size = strategy.calculate_position_size(
    capital=10000,
    current_price=50000,
    atr=500,
    use_kelly=True,
    trade_history=past_trades  # Liste vergangener Trades
)
```

### 3. Standalone-Verwendung

```python
from utils import calculate_kelly_position_size

# Direkte Berechnung
position = calculate_kelly_position_size(
    capital=10000,
    win_rate=0.6,
    avg_win=150,
    avg_loss=100,
    kelly_fraction=0.5,
    max_position_pct=0.25
)

print(f"Position Size: ${position:.2f}")
```

## Verschiedene Kelly-Fraktionen

| Fraction | Name | Beschreibung | Risiko | Empfohlen für |
|----------|------|--------------|--------|---------------|
| 1.0 | Full Kelly | Maximum Growth | Hoch | Erfahrene Trader |
| 0.5 | Half Kelly | Konservativ | Mittel | **Die meisten Trader** ⭐ |
| 0.25 | Quarter Kelly | Sehr konservativ | Niedrig | Risiko-averse Trader |

## Trading-Szenarien

### ✅ Gute Szenarien für Kelly

**1. Konservative Strategie**
- Win Rate: 55%
- Win/Loss Ratio: 1.2
- Half Kelly: ~8.75% des Kapitals

**2. Aggressive Strategie**
- Win Rate: 40%
- Win/Loss Ratio: 3.0
- Half Kelly: ~10% des Kapitals

### ❌ Schlechte Szenarien (Kein Kelly)

**1. Breakeven Strategie**
- Win Rate: 50%
- Win/Loss Ratio: 1.0
- Kelly: 0% (Kein Edge)

**2. Verlust-Strategie**
- Win Rate: 40%
- Win/Loss Ratio: 0.83
- Kelly: 0% (Negativer Edge)

## Vor- und Nachteile

### ✅ Vorteile

- **Mathematisch optimal** für langfristiges Wachstum
- **Automatische Anpassung** basierend auf Performance
- **Verhindert Over-Trading** bei schlechter Performance
- **Maximiert Gewinnpotenzial** bei guter Performance

### ⚠️ Nachteile / Risiken

- **Aggressiv**: Full Kelly kann zu großen Drawdowns führen
- **Datenabhängig**: Benötigt mindestens 20 Trades für Genauigkeit
- **Annahmen**: Geht von unabhängigen Trades aus
- **Volatilität**: Kann zu starken Positionsgrößen-Schwankungen führen

## Best Practices

### ✅ DO's

1. **Starte mit Half Kelly** (kelly_fraction=0.5)
2. **Setze ein Maximum** (kelly_max_position_pct=0.25)
3. **Sammle Daten**: Mindestens 20 Trades vor Aktivierung
4. **Teste im DRY_RUN**: Immer erst simulieren
5. **Überwache Performance**: Passe kelly_fraction bei Bedarf an

### ❌ DON'Ts

1. **Nicht Full Kelly verwenden** ohne Erfahrung
2. **Nicht mit zu wenig Daten** (< 20 Trades)
3. **Nicht ohne Maximum** (setze immer kelly_max_position_pct)
4. **Nicht blind vertrauen**: Überprüfe Berechnungen manuell
5. **Nicht bei Live-Trading starten**: Erst Backtest!

## Tests & Demo

### Tests ausführen

```powershell
# Windows PowerShell
.\venv\Scripts\python.exe test_kelly_criterion.py

# Linux/Mac
python3 test_kelly_criterion.py
```

**Erwartete Ausgabe:**
- 16 Tests
- Alle bestehen ✅
- Test für verschiedene Szenarien

### Demo ausführen

```powershell
# Windows PowerShell
.\venv\Scripts\python.exe demo_kelly_criterion.py

# Linux/Mac
python3 demo_kelly_criterion.py
```

**Demo zeigt:**
1. Basic Kelly Criterion
2. Position Sizing
3. Verschiedene Szenarien
4. Schritt-für-Schritt Berechnung
5. Config Integration

## Integration Beispiel: LSOB Strategy

```python
# In lsob_strategy.py
def calculate_position_size(self, capital, current_price, atr, 
                           use_kelly=False, trade_history=None):
    if not use_kelly or len(trade_history) < 10:
        # Standard ATR-based sizing
        risk_amount = capital * 0.01
        position_size = risk_amount / (atr * self.stop_loss_atr_mult)
        return max(1, int(position_size))
    
    # Kelly-based sizing
    pnls = [float(t['pnl']) for t in trade_history[-20:]]
    wins = [p for p in pnls if p > 0]
    losses = [abs(p) for p in pnls if p < 0]
    
    win_rate = len(wins) / len(pnls)
    avg_win = sum(wins) / len(wins)
    avg_loss = sum(losses) / len(losses)
    
    kelly_position = calculate_kelly_position_size(
        capital, win_rate, avg_win, avg_loss,
        kelly_fraction=0.5, max_position_pct=0.25
    )
    
    return max(1, int(kelly_position / current_price))
```

## FAQ

### Q: Wann sollte ich Kelly Criterion verwenden?

**A:** Verwende Kelly, wenn:
- Du mindestens 20 vergangene Trades hast
- Deine Strategie einen **positiven Edge** hat (Win Rate × Win/Loss Ratio > 1)
- Du bereit bist, Positionsgrößen dynamisch anzupassen

### Q: Was ist der Unterschied zwischen Full und Half Kelly?

**A:** 
- **Full Kelly (1.0)**: Maximales Wachstum, aber hohe Volatilität
- **Half Kelly (0.5)**: 75% des Wachstums von Full Kelly, aber nur 50% der Volatilität
- **Empfehlung**: Starte mit Half Kelly oder weniger

### Q: Warum gibt Kelly manchmal 0% zurück?

**A:** Kelly gibt 0% zurück wenn:
- Die Strategie einen **negativen Edge** hat (mehr Verlust als Gewinn erwartet)
- Win Rate × Win/Loss Ratio ≤ 1
- **Bedeutung**: Kein Trade empfohlen - die Strategie ist nicht profitabel!

### Q: Kann Kelly mit Stop-Loss kombiniert werden?

**A:** Ja! Kelly berechnet die Positionsgröße, Stop-Loss schützt vor zu großen Verlusten:
```python
# Kelly für Position Size
position = calculate_kelly_position_size(...)

# Stop-Loss für Risk Management
stop_loss = entry_price * (1 - stop_loss_percent)
```

### Q: Was passiert bei zu wenig Daten?

**A:** Die Implementation fällt automatisch auf Standard-Sizing zurück:
```python
if len(trade_history) < 10:
    # Fall back to ATR-based sizing
    return standard_position_size()
```

## Weiterführende Ressourcen

- 📚 [Wikipedia: Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion)
- 📊 [ROADMAP.md - M3.6](ROADMAP.md) - Original Feature Request
- 🧪 [test_kelly_criterion.py](test_kelly_criterion.py) - Unit Tests
- 🎯 [demo_kelly_criterion.py](demo_kelly_criterion.py) - Demonstrations
- 🔧 [lsob_strategy.py](lsob_strategy.py) - Beispiel-Integration

## Warnung ⚠️

Kelly Criterion ist ein **mächtiges Werkzeug**, aber:

1. **Kein Heiliger Gral**: Kelly garantiert keine Gewinne
2. **Hohe Volatilität**: Full Kelly kann zu großen Swings führen
3. **Datenanforderungen**: Benötigt genaue Win Rate / Win-Loss Daten
4. **Annahmen**: Geht von unabhängigen Trades aus (nicht immer gegeben)

**IMMER im DRY_RUN Modus testen bevor du live gehst!**

---

**Made for Windows ⭐ | DRY_RUN Default | Kelly Criterion Integration Complete**
