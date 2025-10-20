# 🔐 Windows PowerShell ExecutionPolicy - Anleitung

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2025-10-20

## 📋 Übersicht

Diese Anleitung erklärt, wie man PowerShell ExecutionPolicy-Probleme behebt, die beim ersten Start von Skripten auftreten können. Die ExecutionPolicy ist ein Sicherheitsfeature von PowerShell, das die Ausführung von Skripten kontrolliert.

---

## 🚨 Typisches Problem

Wenn Sie versuchen, ein PowerShell-Skript auszuführen, kann folgende Fehlermeldung erscheinen:

```
.\scripts\start_live.ps1 : Die Datei "...\start_live.ps1" kann nicht geladen werden, 
da die Ausführung von Skripts auf diesem System deaktiviert ist. 
Weitere Informationen finden Sie unter "about_Execution_Policies".
```

**Ursache:** Die aktuelle ExecutionPolicy verhindert die Ausführung von Skripten.

---

## ⚡ Schnelllösung: Temporäre Freigabe (Empfohlen)

### 🎯 Für die aktuelle PowerShell-Session

**Dies ist die sicherste Methode** - Die Änderung gilt nur für die aktuell geöffnete PowerShell-Sitzung und wird nach dem Schließen automatisch zurückgesetzt.

```powershell
# Temporär Bypass für die aktuelle Session setzen
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Jetzt können Sie Ihr Skript ausführen
.\scripts\start_live.ps1
```

**Vorteile:**
- ✅ Keine permanenten Änderungen am System
- ✅ Automatischer Rollback beim Schließen von PowerShell
- ✅ Ideal für Entwicklung und Testing
- ✅ Keine Administratorrechte erforderlich

---

## 🔧 Permanente Änderung (Für fortgeschrittene Benutzer)

### Option 1: RemoteSigned (Empfohlen)

**RemoteSigned** erlaubt die Ausführung lokaler Skripte und signierter Skripte aus dem Internet. Dies ist ein guter Kompromiss zwischen Sicherheit und Funktionalität.

```powershell
# Für den aktuellen Benutzer (keine Admin-Rechte nötig)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Optional: Für alle Benutzer (Admin-Rechte erforderlich)
Set-ExecutionPolicy -Scope LocalMachine -ExecutionPolicy RemoteSigned
```

**Eigenschaften:**
- ✅ Lokale Skripte werden ausgeführt
- ✅ Heruntergeladene Skripte müssen signiert sein
- ✅ Gute Balance zwischen Sicherheit und Funktionalität
- ⚠️ Permanente Änderung

### Option 2: Unrestricted (Weniger sicher)

**Unrestricted** erlaubt alle Skripte, warnt aber bei heruntergeladenen Skripten.

```powershell
# Für den aktuellen Benutzer
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted
```

**Eigenschaften:**
- ✅ Alle lokalen Skripte werden ausgeführt
- ⚠️ Warnung bei heruntergeladenen Skripten
- ⚠️ Weniger sicher als RemoteSigned

### Option 3: Bypass (Nicht empfohlen für permanente Nutzung)

**⚠️ WARNUNG:** Bypass deaktiviert alle Sicherheitsprüfungen komplett!

```powershell
# NUR für Testzwecke oder Automatisierung
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass
```

**Eigenschaften:**
- ⚠️ Keine Sicherheitsprüfungen
- ⚠️ Alle Skripte werden ohne Warnung ausgeführt
- ❌ Nicht für Produktivsysteme empfohlen
- ⚠️ Verwenden Sie dies nur temporär (Scope Process)

---

## 🔍 Aktuelle Policy prüfen

Um die aktuelle ExecutionPolicy zu überprüfen:

```powershell
# Alle Policies anzeigen
Get-ExecutionPolicy -List

# Ausgabe-Beispiel:
#         Scope ExecutionPolicy
#         ----- ---------------
# MachinePolicy       Undefined
#    UserPolicy       Undefined
#       Process       Undefined
#   CurrentUser    RemoteSigned
#  LocalMachine       Undefined
```

Die effektive Policy ist die restriktivste Policy aus allen Scopes.

```powershell
# Effektive Policy anzeigen
Get-ExecutionPolicy

# Ausgabe: z.B. "RemoteSigned"
```

---

## 🔄 Policy zurücksetzen

### Temporäre Policy zurücksetzen

Einfach die PowerShell-Session schließen - die temporäre Policy (Scope Process) wird automatisch zurückgesetzt.

### Permanente Policy zurücksetzen

```powershell
# CurrentUser-Policy auf Standard zurücksetzen
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Undefined

# LocalMachine-Policy zurücksetzen (Admin-Rechte erforderlich)
Set-ExecutionPolicy -Scope LocalMachine -ExecutionPolicy Undefined
```

---

## 🛡️ Sicherheitshinweise

### ⚠️ Wichtige Warnungen

1. **Bypass ist gefährlich:**
   - Bypass deaktiviert ALLE Sicherheitsprüfungen
   - Verwenden Sie Bypass NUR temporär (Scope Process)
   - Niemals Bypass als permanente Policy für CurrentUser/LocalMachine

2. **Signierte Skripte:**
   - RemoteSigned schützt vor schädlichen heruntergeladenen Skripten
   - Lokale Skripte werden trotzdem ausgeführt
   - Guter Kompromiss für Entwickler

3. **Administrator-Rechte:**
   - Scope LocalMachine benötigt Admin-Rechte
   - Scope CurrentUser funktioniert ohne Admin-Rechte
   - Scope Process benötigt keine besonderen Rechte

4. **Permanente Änderungen:**
   - Überlegen Sie zweimal, bevor Sie permanente Änderungen vornehmen
   - Dokumentieren Sie Ihre Änderungen
   - Testen Sie mit temporären Policies zuerst

### ✅ Best Practices

1. **Entwicklung:**
   ```powershell
   # Verwenden Sie temporäre Bypass-Policy
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\scripts\start_live.ps1
   ```

2. **Produktivsystem:**
   ```powershell
   # Verwenden Sie RemoteSigned als permanente Policy
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```

3. **CI/CD Pipelines:**
   ```powershell
   # Setzen Sie Policy temporär im Build-Skript
   pwsh -ExecutionPolicy Bypass -File .\scripts\build.ps1
   ```

---

## 📖 Scope-Hierarchie

PowerShell verwendet folgende Scope-Hierarchie (von höchster zu niedrigster Priorität):

1. **MachinePolicy** - Durch Gruppenrichtlinien (GPO) gesetzt
2. **UserPolicy** - Durch Benutzer-Gruppenrichtlinien gesetzt
3. **Process** - Nur für aktuelle PowerShell-Session
4. **CurrentUser** - Für den aktuellen Benutzer
5. **LocalMachine** - Für alle Benutzer auf dem System

Die **restriktivste** Policy aus allen Scopes wird angewendet.

---

## 🎯 Empfehlungen für ai.traiding Repository

### Für Entwickler (Erstnutzer)

1. **Temporäre Freigabe** für erste Tests:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\scripts\start_live.ps1
   ```

2. **Permanente Lösung** nach erfolgreichen Tests:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```

### Für VS Code Tasks

Die VS Code Tasks nutzen direkt `pwsh` oder `powershell` mit dem Skript-Pfad, was in den meisten Fällen funktioniert, wenn CurrentUser auf RemoteSigned gesetzt ist.

### Für Automatisierung

```powershell
# In automatisierten Workflows
pwsh -ExecutionPolicy Bypass -File .\scripts\auto_select_strategy.ps1
```

---

## 📚 Weitere Ressourcen

### Microsoft-Dokumentation

- [About Execution Policies](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies)
- [Set-ExecutionPolicy Cmdlet](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy)
- [Get-ExecutionPolicy Cmdlet](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-executionpolicy)

### Repository-Dokumentation

- [README.md](../README.md) - Hauptdokumentation mit Quickstart
- [POWERSHELL_DEVELOPMENT.md](../POWERSHELL_DEVELOPMENT.md) - PowerShell-Entwicklungsrichtlinien
- [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Allgemeine Problemlösungen

---

## 💡 Häufig gestellte Fragen (FAQ)

### Q: Warum brauche ich ExecutionPolicy-Änderungen?

**A:** PowerShell blockiert standardmäßig die Ausführung von Skripten als Sicherheitsmaßnahme. Da dieses Repository PowerShell-Skripte verwendet, müssen Sie die Policy anpassen.

### Q: Ist Bypass gefährlich?

**A:** Ja, wenn permanent gesetzt. Für temporäre Nutzung (Scope Process) ist es sicher, da die Änderung nur für die aktuelle Session gilt.

### Q: Was ist der Unterschied zwischen RemoteSigned und Unrestricted?

**A:** RemoteSigned erlaubt lokale Skripte und signierte Downloads. Unrestricted erlaubt alle Skripte, warnt aber bei Downloads. RemoteSigned ist sicherer.

### Q: Muss ich Admin sein?

**A:** Nein, für Scope Process und CurrentUser sind keine Admin-Rechte nötig. Nur LocalMachine benötigt Admin-Rechte.

### Q: Gilt die Änderung für alle PowerShell-Versionen?

**A:** Ja, ExecutionPolicy gilt für PowerShell 5.1, PowerShell Core 7+ und alle anderen PowerShell-Versionen.

### Q: Was passiert wenn ich mehrere Policies setze?

**A:** Die restriktivste Policy aus allen Scopes wird angewendet. Process hat die höchste Priorität (nach GPO).

---

## ✅ Zusammenfassung

| Methode | Sicherheit | Permanenz | Admin | Empfehlung |
|---------|------------|-----------|-------|------------|
| `Process + Bypass` | ⚠️ Niedrig | ✅ Temporär | ❌ Nein | ✅ **Ideal für Dev** |
| `CurrentUser + RemoteSigned` | ✅ Hoch | ⚠️ Permanent | ❌ Nein | ✅ **Empfohlen** |
| `CurrentUser + Unrestricted` | ⚠️ Mittel | ⚠️ Permanent | ❌ Nein | ⚠️ Akzeptabel |
| `CurrentUser + Bypass` | ❌ Keine | ⚠️ Permanent | ❌ Nein | ❌ **Nicht empfohlen** |
| `LocalMachine + *` | Variiert | ⚠️ Permanent | ✅ Ja | ⚠️ Nur wenn nötig |

---

**Made for Windows ⭐ | PowerShell-First | Sicherheit durch Best Practices**
