# 🔄 Live-Umschaltung Guide

**Sichere Umschaltung zwischen DRY_RUN und LIVE Trading Modi**

---

## 📋 Übersicht

Das `automation/live_switch.py` Modul bietet eine sichere, geprüfte Methode zum Wechseln zwischen DRY_RUN (Test) und LIVE (Production) Modi.

**Sicherheits-Features:**
- ✅ Validiert API-Keys und Secrets
- ✅ Prüft Umgebungs-Voraussetzungen
- ✅ Fordert explizite Bestätigung
- ✅ Führt Preflight-Checks aus
- ✅ Blockiert bei aktivem KILL_SWITCH

---

## 🚀 Schnellstart

### CLI Verwendung (Windows PowerShell)

**Aktuellen Status prüfen:**
```powershell
.\venv\Scripts\python.exe -m automation.live_switch --status
```

**Zu DRY_RUN wechseln (sicher):**
```powershell
.\venv\Scripts\python.exe -m automation.live_switch --dry-run
```

**Zu LIVE wechseln (mit Bestätigung):**
```powershell
.\venv\Scripts\python.exe -m automation.live_switch --live
```

**Zu LIVE wechseln (erzwungen, nur für Tests!):**
```powershell
.\venv\Scripts\python.exe -m automation.live_switch --live --force --skip-preflight
```

---

## 📚 Python API Verwendung

### Beispiel 1: Einfache Umschaltung

```python
from automation.live_switch import switch_to_live, switch_to_dry_run

# Zu DRY_RUN wechseln
result = switch_to_dry_run()
print(f"Modus: {result['mode']}")

# Zu LIVE wechseln (mit Bestätigung)
try:
    result = switch_to_live()
    if result['success']:
        print("✅ Live-Trading aktiviert!")
    else:
        print(f"❌ Fehler: {result['reason']}")
except Exception as e:
    print(f"❌ Exception: {e}")
```

### Beispiel 2: Validierung vor Umschaltung

```python
from automation.live_switch import check_api_key, check_environment_ready, switch_to_live

# Prüfe API-Keys
api_valid, api_msg = check_api_key()
if not api_valid:
    raise Exception(f"API-Key fehlt oder ungültig: {api_msg}")

# Prüfe Umgebung
env_valid, env_msg = check_environment_ready()
if not env_valid:
    raise Exception(f"Umgebung nicht bereit: {env_msg}")

# Jetzt sicher zu LIVE wechseln
result = switch_to_live()
```

### Beispiel 3: Status abfragen

```python
from automation.live_switch import get_current_mode

status = get_current_mode()
print(f"Aktueller Modus: {status['mode']}")
print(f"DRY_RUN: {status['dry_run']}")
print(f"LIVE_TRADING: {status['live_trading']}")
print(f"KILL_SWITCH: {status['kill_switch']}")
print(f"Sicherer Modus: {status['is_safe_mode']}")
```

### Beispiel 4: Integration in Trading-Bot

```python
import os
from automation.live_switch import switch_to_live, check_api_key, get_current_mode

def start_trading_bot():
    """Startet Trading-Bot mit Modus-Prüfung."""
    
    # Prüfe API-Keys
    if not check_api_key()[0]:
        print("❌ API-Keys fehlen oder sind ungültig")
        return
    
    # Frage Benutzer nach Modus
    status = get_current_mode()
    print(f"\n📊 Aktueller Modus: {status['mode']}")
    
    if status['mode'] == 'DRY_RUN':
        choice = input("\n⚠️  Zu LIVE-Trading wechseln? (ja/nein): ")
        if choice.lower() == 'ja':
            try:
                result = switch_to_live()
                if not result['success']:
                    print(f"❌ Umschaltung fehlgeschlagen: {result.get('reason')}")
                    return
            except Exception as e:
                print(f"❌ Fehler bei Umschaltung: {e}")
                return
    
    # Starte Bot
    print("\n🚀 Starte Trading-Bot...")
    run_bot()

def run_bot():
    """Bot-Logik hier."""
    current_mode = get_current_mode()
    if current_mode['is_safe_mode']:
        print("ℹ️  Bot läuft im sicheren Modus (DRY_RUN oder KILL_SWITCH)")
    else:
        print("⚠️  Bot läuft im LIVE-Modus - echte Trades!")
```

---

## 🔍 Funktionen im Detail

### `check_api_key() -> Tuple[bool, str]`

Prüft ob API-Key und Secret vorhanden und gültig sind.

**Returns:**
- `(True, "API-Keys vorhanden und gültig")` bei Erfolg
- `(False, "BINANCE_API_KEY fehlt")` bei Fehler

**Beispiel:**
```python
success, message = check_api_key()
if not success:
    print(f"❌ {message}")
```

---

### `check_environment_ready() -> Tuple[bool, str]`

Prüft ob die Umgebung für Live-Trading bereit ist.

**Prüfungen:**
- ✅ API-Keys vorhanden
- ✅ Production-Endpoint konfiguriert
- ✅ KILL_SWITCH nicht aktiv

**Returns:**
- `(True, "Umgebung bereit für Live-Trading")` bei Erfolg
- `(False, "Fehler-Beschreibung")` bei Fehler

**Beispiel:**
```python
success, message = check_environment_ready()
if not success:
    print(f"❌ {message}")
```

---

### `switch_to_live(force=False, skip_preflight=False) -> Dict`

Wechselt zu Live-Trading Modus.

**Args:**
- `force`: Wenn True, keine Bestätigung erforderlich (GEFÄHRLICH!)
- `skip_preflight`: Wenn True, Preflight-Checks überspringen (NICHT EMPFOHLEN!)

**Returns:**
```python
{
    "success": True,
    "mode": "LIVE",
    "dry_run": False,
    "live_trading": True,
    "base_url": "https://api.binance.com"
}
```

**Ablauf:**
1. ✅ Validiert API-Keys
2. ✅ Prüft Umgebung
3. ✅ Fordert Bestätigung (Text: "LIVE_TRADING_BESTÄTIGT")
4. ✅ Führt Preflight-Checks aus
5. ✅ Setzt Environment-Variablen

**Raises:**
- `Exception`: Bei fehlenden/ungültigen API-Keys oder Umgebungs-Fehlern

**Beispiel:**
```python
try:
    result = switch_to_live()
    print(f"✅ Umschaltung erfolgreich: {result['mode']}")
except Exception as e:
    print(f"❌ Fehler: {e}")
```

---

### `switch_to_dry_run() -> Dict`

Wechselt zu DRY_RUN Modus (sicherer Modus).

**Returns:**
```python
{
    "success": True,
    "mode": "DRY_RUN",
    "dry_run": True,
    "live_trading": False,
    "base_url": "https://testnet.binance.vision"
}
```

**Beispiel:**
```python
result = switch_to_dry_run()
print(f"✅ Sicherer Modus aktiviert: {result['mode']}")
```

---

### `get_current_mode() -> Dict`

Gibt den aktuellen Trading-Modus zurück.

**Returns:**
```python
{
    "mode": "LIVE" | "DRY_RUN",
    "dry_run": bool,
    "live_trading": bool,
    "base_url": str,
    "kill_switch": bool,
    "live_ack": str,
    "is_safe_mode": bool  # True wenn DRY_RUN oder KILL_SWITCH
}
```

**Beispiel:**
```python
status = get_current_mode()
if status['is_safe_mode']:
    print("✓  Sicherer Modus aktiv")
else:
    print("⚠️  LIVE-Modus aktiv!")
```

---

## 🛡️ Sicherheits-Checks

### Umschaltung zu LIVE wird blockiert wenn:

1. ❌ **API-Key fehlt oder ungültig**
   ```
   Exception: API-Key fehlt oder ungültig: BINANCE_API_KEY fehlt
   ```

2. ❌ **KILL_SWITCH ist aktiv**
   ```
   Exception: Umgebung nicht bereit: KILL_SWITCH ist aktiv - Live-Trading blockiert
   ```

3. ❌ **Falscher Base-URL**
   ```
   Exception: BINANCE_BASE_URL muss Production-Endpoint sein
   ```

4. ❌ **Bestätigung verweigert**
   ```
   {"success": False, "reason": "Bestätigung verweigert"}
   ```

5. ❌ **Preflight-Checks fehlgeschlagen**
   ```
   Exception: Preflight-Checks fehlgeschlagen: Time Sync failed
   ```

---

## ⚙️ Environment-Variablen

### Gesetzte Variablen bei LIVE-Modus:
```bash
DRY_RUN=false
LIVE_TRADING=true
BINANCE_BASE_URL=https://api.binance.com
```

### Gesetzte Variablen bei DRY_RUN-Modus:
```bash
DRY_RUN=true
LIVE_TRADING=false
BINANCE_BASE_URL=https://testnet.binance.vision
```

---

## 📝 Bestätigungs-Dialog

Bei Umschaltung zu LIVE wird folgende Bestätigung angefordert:

```
============================================================
⚠️  WARNUNG: Live-Trading Aktivierung
============================================================

Du bist dabei, zu LIVE-TRADING zu wechseln!

⚠️  RISIKEN:
  • Trading mit ECHTEM Geld
  • Echte Verluste sind möglich
  • Keine Rücknahme von Transaktionen

✓  VORAUSSETZUNGEN:
  • API-Keys sind korrekt konfiguriert
  • Risk-Limits sind gesetzt
  • Monitoring ist aktiv
  • Du verstehst die Strategie

Gib 'LIVE_TRADING_BESTÄTIGT' ein um fortzufahren:
(Jede andere Eingabe bricht ab)

> _
```

**Korrekte Eingabe:** `LIVE_TRADING_BESTÄTIGT`
**Abbruch:** Jede andere Eingabe oder Ctrl+C

---

## 🧪 Testing

**Teste mit Mock-Daten:**
```python
import os
os.environ["BINANCE_API_KEY"] = "test_key_1234567890"
os.environ["BINANCE_API_SECRET"] = "test_secret_1234567890"

from automation.live_switch import check_api_key
success, message = check_api_key()
print(f"Test: {message}")
```

**Führe Unit-Tests aus:**
```bash
python test_live_switch.py
```

**Führe Demo aus:**
```bash
python demo_live_switch.py
```

---

## 🔗 Verwandte Dateien

- **Quellcode:** `automation/live_switch.py`
- **Tests:** `test_live_switch.py` (21 Tests)
- **Demo:** `demo_live_switch.py`
- **Preflight:** `scripts/live_preflight.py`
- **Setup:** `scripts/setup_live.ps1`
- **Runner:** `scripts/start_live_prod.ps1`

---

## ⚠️ Best Practices

### ✅ DO:
- ✅ Verwende `--dry-run` für Tests
- ✅ Prüfe Status vor Umschaltung
- ✅ Validiere API-Keys explizit
- ✅ Führe Preflight-Checks aus
- ✅ Überwache nach Umschaltung

### ❌ DON'T:
- ❌ Verwende NICHT `--force` in Production
- ❌ Überspringe NICHT Preflight-Checks
- ❌ Teile NIEMALS API-Keys
- ❌ Wechsle NICHT ohne Monitoring
- ❌ Ignoriere NICHT Fehler-Meldungen

---

## 🆘 Troubleshooting

### Problem: API-Keys fehlen
```
Exception: API-Key fehlt oder ungültig: BINANCE_API_KEY fehlt
```

**Lösung:**
1. Führe Setup-Wizard aus: `.\scripts\setup_live.ps1`
2. Oder setze Environment-Variablen manuell

---

### Problem: KILL_SWITCH blockiert
```
Exception: KILL_SWITCH ist aktiv - Live-Trading blockiert
```

**Lösung:**
```powershell
$env:KILL_SWITCH = "false"
# Oder entfernen:
Remove-Item Env:KILL_SWITCH
```

---

### Problem: Falscher Base-URL
```
Exception: BINANCE_BASE_URL muss Production-Endpoint sein
```

**Lösung:**
```powershell
$env:BINANCE_BASE_URL = "https://api.binance.com"
```

---

### Problem: Preflight-Checks fehlgeschlagen
```
Exception: Preflight-Checks fehlgeschlagen: Time Sync failed
```

**Lösung:**
1. Prüfe System-Zeit: `Get-Date`
2. Synchronisiere Zeit: `w32tm /resync`
3. Prüfe Netzwerk-Verbindung zu Binance

---

## 📞 Support

**Dokumentation:**
- README.md - Hauptdokumentation
- LIVE_TRADING_SETUP_GUIDE.md - Setup-Guide
- LIVE_TRADING_MANUAL_TEST_GUIDE.md - Test-Guide

**Tests:**
- Führe `python test_live_switch.py` aus
- Führe `python demo_live_switch.py` aus

---

**Made for Windows ⭐ | PowerShell-First | Sichere Live-Umschaltung**
