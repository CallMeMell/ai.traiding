# 📊 Trading Bot Dashboard

## Übersicht

Das Dashboard bietet eine visuelle Benutzeroberfläche zur Überwachung der Trading-Bot-Performance in Echtzeit.

![Dashboard Screenshot](https://github.com/user-attachments/assets/d3588768-e7f6-439c-b701-b75f270ab7b2)

## Features

### 📈 Interaktive Visualisierungen
- **Gewinn/Verlust Diagramm**: Zeigt P&L für jeden Trade als Balkendiagramm
- **Kapital Entwicklung**: Liniendiagramm der Kapitalentwicklung über Zeit
- **Letzte Trades**: Übersichtliche Liste der jüngsten Trades

### 📊 Statistiken
- **Total P&L**: Gesamtgewinn/-verlust
- **ROI**: Return on Investment in Prozent
- **Anzahl Trades**: Gesamtzahl ausgeführter Trades
- **Erfolgsquote**: Win Rate (prozentual profitable Trades)
- **Aktuelles Kapital**: Verfügbares Kapital
- **Durchschnittlicher P&L**: Durchschnittlicher Gewinn/Verlust pro Trade

### 🎨 Design
- Modernes, responsives Design
- Farbcodierung (Grün = Gewinn, Rot = Verlust)
- Hover-Effekte und Animationen
- Auto-Refresh alle 10 Sekunden
- Manueller Refresh-Button

## Verwendung

### 1. Bot starten
Starten Sie zunächst den Trading-Bot, um Trades zu generieren:

```bash
python main.py
```

Der Bot erstellt automatisch die Datei `data/trades.csv` mit allen Trades.

### 2. Dashboard öffnen

#### Option A: Direktes Öffnen
Öffnen Sie einfach die Datei `dashboard.html` in Ihrem Browser:
```bash
# Windows
start dashboard.html

# Mac
open dashboard.html

# Linux
xdg-open dashboard.html
```

#### Option B: Mit lokalem Server
Für eine bessere Performance können Sie einen lokalen Server starten:

```bash
# Python 3
python -m http.server 8000

# Dann öffnen Sie im Browser:
# http://localhost:8000/dashboard.html
```

#### Option C: Mit Node.js
```bash
npx serve

# Oder mit einem anderen Server wie live-server:
npx live-server
```

### 3. Dashboard nutzen
- Das Dashboard lädt automatisch die Daten aus `data/trades.csv`
- Daten werden alle 10 Sekunden automatisch aktualisiert
- Klicken Sie auf den 🔄 Button für manuellen Refresh
- Hovern Sie über Diagramme für Details

## Technische Details

### Keine externen Abhängigkeiten
Das Dashboard verwendet:
- **Vanilla JavaScript** - Keine Frameworks erforderlich
- **CSS3** für Animationen und Styling
- **SVG** für Liniendiagramme
- **CSS Flexbox/Grid** für Balkendiagramme

Dadurch funktioniert das Dashboard **ohne Internet-Verbindung** und ohne zusätzliche Installation.

### Datenquelle
Das Dashboard liest die Datei `data/trades.csv`, die automatisch vom Trading-Bot erstellt wird:

```csv
timestamp,symbol,order_type,price,quantity,triggering_strategies,capital,pnl
2024-10-09T12:30:45,BTC/USDT,BUY,30000.50,0.1,"rsi, ma_crossover",10000.00,0.00
2024-10-09T12:31:50,BTC/USDT,SELL,31500.75,0.1,rsi,10150.00,150.00
```

### Browser-Kompatibilität
- ✅ Chrome/Edge (empfohlen)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

Mindestens: Moderne Browser mit ES6-Support

## Fehlerbehebung

### "Keine Trades gefunden"
**Problem**: Dashboard zeigt "Keine Trades gefunden"

**Lösung**: 
1. Starten Sie den Bot mit `python main.py`
2. Warten Sie, bis mindestens ein Trade ausgeführt wurde
3. Aktualisieren Sie das Dashboard

### "Fehler beim Laden der Daten"
**Problem**: Dashboard kann `data/trades.csv` nicht laden

**Lösung**:
1. Stellen Sie sicher, dass die Datei existiert: `ls data/trades.csv`
2. Verwenden Sie einen lokalen Server (siehe Option B oben)
3. Überprüfen Sie Browser-Konsole (F12) für Details

### Diagramme werden nicht angezeigt
**Problem**: Statistiken werden angezeigt, aber keine Diagramme

**Lösung**:
1. Stellen Sie sicher, dass mindestens 2 SELL-Trades vorhanden sind
2. Aktualisieren Sie die Seite (F5)
3. Leeren Sie den Browser-Cache (Strg+Shift+Delete)

## Anpassungen

### Auto-Refresh-Intervall ändern
Bearbeiten Sie `dashboard.html` und ändern Sie:

```javascript
// Standard: 10 Sekunden
setInterval(loadData, 10000);

// Ändern auf 5 Sekunden:
setInterval(loadData, 5000);
```

### Anzahl angezeigter Trades
Bearbeiten Sie die Funktion `updateTradeList()`:

```javascript
// Standard: 10 Trades
const recentTrades = trades.slice(-10).reverse();

// Ändern auf 20 Trades:
const recentTrades = trades.slice(-20).reverse();
```

### Farben anpassen
Bearbeiten Sie den `<style>` Bereich in `dashboard.html`:

```css
/* Beispiel: Hintergrund-Gradient ändern */
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

## Nächste Schritte

Wie in der Feature-Beschreibung erwähnt, sind folgende Erweiterungen geplant:

### 📡 Echtzeitdaten
- WebSocket-Verbindung zum Trading-Bot
- Live-Updates ohne Polling
- Push-Benachrichtigungen für Trades

### 📊 Zusätzliche Metriken
- **Drawdown**: Maximaler Kapitalrückgang
- **Sharpe Ratio**: Risiko-adjustierte Performance
- **Risikoanalyse**: Volatilität, Value at Risk
- **Trade-Dauer**: Durchschnittliche Haltedauer
- **Strategie-Performance**: Erfolg einzelner Strategien

### 🔧 Erweiterte Features
- Export zu PDF/Excel
- Historische Vergleiche
- Multi-Symbol-Unterstützung
- Konfigurierbare Alerts
- Dark Mode Toggle

## Mitwirkung

Verbesserungsvorschläge und Feedback sind willkommen! Bitte erstellen Sie ein Issue oder Pull Request.

## Lizenz

Teil des ai.traiding Projekts - siehe Hauptprojekt für Lizenzdetails.
