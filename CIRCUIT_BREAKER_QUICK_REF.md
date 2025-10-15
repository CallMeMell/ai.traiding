# 🚨 Circuit Breaker Quick Reference

**Schnellreferenz für die erweiterte Circuit Breaker Logik**

---

## 🚀 Quick Start

### 1. Aktivieren

```python
# In config.py
use_advanced_circuit_breaker: bool = True
```

### 2. Basis-Usage

```python
from circuit_breaker import CircuitBreakerManager, CircuitBreakerActions

# Erstellen
manager = CircuitBreakerManager()

# Konfigurieren
manager.add_threshold(
    level=10.0,  # 10% Drawdown
    actions=[CircuitBreakerActions.create_log_action("10%!", "warning")],
    description="Warning Level"
)

# Prüfen
triggered = manager.check(current_equity=8500, is_dry_run=False)
```

---

## 📊 Standard-Konfiguration

```python
circuit_breaker_thresholds = {
    "warning": {
        "level": 10.0,
        "actions": ["log", "alert"],
        "description": "Warning Level"
    },
    "critical": {
        "level": 20.0,
        "actions": ["log", "alert", "pause_trading"],
        "description": "Critical Level"
    },
    "emergency": {
        "level": 30.0,
        "actions": ["log", "alert", "shutdown", "rebalance"],
        "description": "Emergency Level"
    }
}
```

---

## 🔧 Verfügbare Actions

| Action | Beschreibung | Verwendung |
|--------|--------------|------------|
| `log` | Logge Nachricht | `CircuitBreakerActions.create_log_action("msg", "critical")` |
| `alert` | Sende Alert (Telegram/Email) | `CircuitBreakerActions.create_alert_action(alert_manager, ...)` |
| `pause_trading` | Pausiere Trading | `CircuitBreakerActions.create_pause_trading_action(bot)` |
| `shutdown` | Fahre Bot herunter | `CircuitBreakerActions.create_shutdown_action(bot)` |
| `rebalance` | Rebalanciere Portfolio | `CircuitBreakerActions.create_rebalance_action(portfolio_mgr)` |
| `custom` | Custom Action | `CircuitBreakerActions.create_custom_action(func, "desc")` |

---

## 📋 API Kurzreferenz

### CircuitBreakerManager

```python
# Erstellen
manager = CircuitBreakerManager(enabled=True, only_production=True)

# Schwellenwert hinzufügen
manager.add_threshold(level=10.0, actions=[...], description="...")

# Aus Dict konfigurieren
manager.configure_from_dict({10.0: {...}, 20.0: {...}})

# Prüfen
triggered = manager.check(current_equity=9000, is_dry_run=False)

# Status abrufen
status = manager.get_status()

# Reset
manager.reset()
manager.reset_equity_curve()
```

---

## 🎯 Empfohlene Schwellenwerte

### Konservativ (neue Strategien)
- **5%**: Warning + Log
- **10%**: Alert + Log
- **15%**: Critical + Pause
- **20%**: Emergency + Shutdown

### Standard (erprobte Strategien)
- **10%**: Warning + Log
- **15%**: Alert + Log
- **20%**: Critical + Pause
- **30%**: Emergency + Shutdown

### Aggressiv (profitabel & robust)
- **15%**: Alert + Log
- **25%**: Critical + Pause
- **35%**: Emergency + Shutdown

---

## 🧪 Testing

```bash
# Unit Tests
python -m pytest test_circuit_breaker_advanced.py -v

# Demo
python demo_advanced_circuit_breaker.py

# Schnelltest
python circuit_breaker.py
```

---

## 🐛 Troubleshooting

### CB triggert nicht
```python
# Prüfe Status
status = manager.get_status()
print(f"Enabled: {status['enabled']}")
print(f"Equity points: {len(manager.equity_curve)}")
print(f"Current DD: {manager.calculate_current_drawdown():.2f}%")
```

### Actions schlagen fehl
```python
# Prüfe Logs für Action-Fehler
# Actions sollten robust implementiert sein
def safe_action():
    try:
        # logic
    except Exception as e:
        logger.error(f"Action failed: {e}")
```

### DRY_RUN vs Production
```python
# CB nur aktiv wenn:
manager.enabled = True
manager.only_production = True
is_dry_run = False
```

---

## 📚 Weitere Informationen

- **Vollständige Dokumentation**: `ADVANCED_CIRCUIT_BREAKER_GUIDE.md`
- **Implementierung**: `circuit_breaker.py`
- **Tests**: `test_circuit_breaker_advanced.py`
- **Demo**: `demo_advanced_circuit_breaker.py`
- **Config**: `config.py` und `config/circuit_breaker_config.example.yaml`

---

## 💡 Best Practices

1. **Immer in DRY_RUN testen** vor Production
2. **Progressive Eskalation** verwenden (10%, 15%, 20%, 30%)
3. **Alerts kombinieren** mit Actions (log + alert + pause)
4. **Status überwachen** mit `get_status()`
5. **Equity Curve limitieren** bei langen Sessions (>10k Punkte)

---

**Version**: 2.0.0 | **Datum**: 2025-10-15
