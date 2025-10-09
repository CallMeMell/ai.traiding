# 📊 Trading Bot Dashboard - Benutzerhandbuch

## Übersicht

Das **Trading Bot Dashboard** ist eine professionelle Web-Oberfläche zur Visualisierung und Überwachung deines Trading Bots in Echtzeit.

### ✨ Features

- **📈 Live-Metriken**: Echtzeit-Anzeige von Performance-Kennzahlen
- **📊 Interaktive Charts**: Equity Curve, P&L Distribution, Strategy Performance
- **📋 Trade History**: Übersicht aller ausgeführten Trades
- **⚙️ Bot Configuration**: Aktuelle Bot-Einstellungen auf einen Blick
- **🔄 Auto-Refresh**: Automatische Datenaktualisierung alle 30 Sekunden
- **📱 Responsive Design**: Funktioniert auf Desktop, Tablet und Mobile

---

## 🚀 Schnellstart

### 1. Installation

```bash
# Flask installieren (falls noch nicht vorhanden)
pip install Flask

# Oder alle Dependencies installieren
pip install -r requirements.txt
```

### 2. Dashboard starten

**Windows:**
```cmd
start_dashboard.bat
```

**Linux/Mac:**
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

**Oder manuell:**
```bash
python dashboard.py
```

### 3. Dashboard öffnen

Öffne deinen Browser und navigiere zu:
```
http://localhost:5000
```

---

## 📊 Dashboard-Komponenten

### Performance-Metriken (Oben)

Das Dashboard zeigt 6 Haupt-Metriken in Karten-Form:

1. **Total P&L** 💰
   - Gesamtgewinn/-verlust seit Start
   - Grün = Profit, Rot = Verlust

2. **Current Capital** 💼
   - Aktuelles Gesamtkapital
   - Zeigt Kapitalentwicklung

3. **Total Trades** 🔄
   - Anzahl der ausgeführten Trades
   - Misst Bot-Aktivität

4. **Win Rate** 📈
   - Prozentsatz erfolgreicher Trades
   - Grün wenn ≥50%, sonst Rot

5. **Best Trade** 🏆
   - Höchster einzelner Gewinn
   - Zeigt Maximalpotential

6. **Worst Trade** ⚠️
   - Größter einzelner Verlust
   - Zeigt Risiko-Exposure

### Interaktive Charts

#### 1. Equity Curve (Kapitalverlauf)
- **Typ**: Liniendiagramm
- **Zeigt**: Entwicklung des Gesamtkapitals über Zeit
- **Nutzen**: Visualisiert Gesamtperformance und Trends

#### 2. P&L Distribution (Gewinn/Verlust-Verteilung)
- **Typ**: Balkendiagramm
- **Zeigt**: Einzelne Trade-Ergebnisse
- **Farben**: Grün = Gewinn, Rot = Verlust
- **Nutzen**: Identifiziert konsistente Performance

#### 3. Strategy Performance (Strategie-Performance)
- **Typ**: Donut-Chart
- **Zeigt**: P&L-Beitrag jeder Strategie
- **Nutzen**: Vergleicht Strategie-Effektivität

### Recent Trades (Trade-Historie)

Zeigt die letzten 20 Trades in Tabellenform:

| Spalte | Beschreibung |
|--------|-------------|
| **Timestamp** | Zeitpunkt des Trades |
| **Type** | BUY (grün) oder SELL (rot) |
| **Price** | Ausführungspreis |
| **Quantity** | Gehandelte Menge |
| **Strategies** | Auslösende Strategien |
| **P&L** | Gewinn/Verlust des Trades |
| **Capital** | Kapital nach Trade |

### Bot Configuration (Konfiguration)

Zeigt aktuelle Bot-Einstellungen:

- **Trading Symbol**: Z.B. BTC/USDT
- **Timeframe**: Z.B. 15m, 1h
- **Initial Capital**: Startkapital
- **Trade Size**: Größe pro Trade
- **Active Strategies**: Aktive Strategien
- **Cooperation Logic**: AND/OR Logic

---

## 🔄 Auto-Refresh

Das Dashboard aktualisiert sich automatisch alle **30 Sekunden**.

**Manuelle Aktualisierung:**
- Klicke auf den **blauen Refresh-Button** unten rechts
- Oder drücke **F5** im Browser

---

## 💡 Verwendungstipps

### Workflow 1: Performance überwachen

1. Starte den Trading Bot mit `python main.py`
2. Starte das Dashboard mit `python dashboard.py`
3. Öffne http://localhost:5000 im Browser
4. Beobachte Live-Metriken und Charts
5. Analysiere Trade-History für Optimierungen

### Workflow 2: Backtesting-Ergebnisse anzeigen

1. Führe Backtest aus mit `python backtester.py`
2. Starte das Dashboard
3. Dashboard zeigt Backtest-Ergebnisse automatisch
4. Analysiere Equity Curve und Strategy Performance

### Workflow 3: Multi-Monitor Setup

1. Bot läuft auf Monitor 1 (Terminal)
2. Dashboard auf Monitor 2 (Browser)
3. Echtzeit-Überwachung ohne Task-Switching

---

## 🎨 Customization

### Theme ändern

Passe die Farben in `templates/dashboard.html` an:

```css
/* Haupt-Gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Primärfarbe */
color: #667eea;
```

### Charts anpassen

Ändere Chart-Typen in der `loadCharts()` Funktion:

```javascript
// Von 'line' zu 'bar' ändern
type: 'bar'  // statt 'line'
```

### Refresh-Intervall ändern

```javascript
// Standard: 30 Sekunden
const AUTO_REFRESH_INTERVAL = 30000;

// Auf 60 Sekunden ändern
const AUTO_REFRESH_INTERVAL = 60000;
```

---

## 🐛 Troubleshooting

### Problem: Dashboard lädt nicht

**Lösung 1: Port bereits belegt**
```bash
# Anderen Port verwenden
# In dashboard.py ändern:
app.run(host='0.0.0.0', port=5001)  # statt 5000
```

**Lösung 2: Flask nicht installiert**
```bash
pip install Flask
```

### Problem: Keine Daten angezeigt

**Ursache**: Keine Trades vorhanden

**Lösung**:
1. Führe zuerst einen Backtest oder Live-Trading aus
2. Trades werden in `data/trades.csv` gespeichert
3. Refresh Dashboard

### Problem: Charts werden nicht angezeigt

**Ursache**: Chart.js nicht geladen

**Lösung**:
1. Prüfe Internet-Verbindung (CDN benötigt)
2. Alternativ: Chart.js lokal hosten

---

## 📱 Mobile Nutzung

Das Dashboard ist voll responsive:

- **Tablet**: Optimierte Layout-Darstellung
- **Smartphone**: Vertikale Card-Anordnung
- **Touch**: Alle Interaktionen touch-optimiert

---

## 🔒 Sicherheit

### Produktion-Deployment

⚠️ **Wichtig für Production:**

1. **Secret Key ändern**:
```python
# In dashboard.py
app.config['SECRET_KEY'] = 'dein-sicherer-random-key-hier'
```

2. **Debug Mode deaktivieren**:
```python
# In dashboard.py
app.run(host='0.0.0.0', port=5000, debug=False)
```

3. **Reverse Proxy nutzen**:
```bash
# Mit nginx oder Apache
# Nicht direkt Port 5000 nach außen öffnen
```

4. **Authentication hinzufügen**:
```python
# Flask-Login oder Flask-HTTPAuth verwenden
```

---

## 🚀 Erweiterte Features (Zukünftig)

Geplante Erweiterungen:

- [ ] **WebSocket-Integration** für Echtzeit-Updates ohne Refresh
- [ ] **User Authentication** für sicheren Zugriff
- [ ] **Multi-Symbol Dashboard** für mehrere Trading-Paare
- [ ] **Alert System** bei bestimmten Events
- [ ] **Export-Funktion** für Reports (PDF, Excel)
- [ ] **Dark Mode** Toggle
- [ ] **Custom Indicators** hinzufügen
- [ ] **Backtesting direkt im Dashboard**

---

## 📊 API Endpoints

Das Dashboard bietet folgende REST API Endpoints:

```
GET /api/metrics         - Performance-Metriken
GET /api/charts          - Chart-Daten
GET /api/trades          - Recent Trades (limit: 20)
GET /api/config          - Bot-Konfiguration
GET /api/status          - Bot-Status
```

**Beispiel-Aufruf:**
```bash
curl http://localhost:5000/api/metrics
```

---

## 📝 Beispiel-Screenshots

### Desktop-Ansicht
```
┌────────────────────────────────────────────────┐
│  🚀 Trading Bot Dashboard      ● Running       │
├────────────────────────────────────────────────┤
│  💰 Total P&L    💼 Capital    🔄 Trades       │
│  $2,450          $12,450       45              │
│                                                 │
│  📈 Win Rate     🏆 Best       ⚠️ Worst        │
│  62.22%          $450          -$220           │
├────────────────────────────────────────────────┤
│  📈 Equity Curve         📊 P&L Distribution   │
│  [Line Chart]            [Bar Chart]           │
│                                                 │
│  📊 Strategy Performance                        │
│  [Donut Chart]                                 │
├────────────────────────────────────────────────┤
│  📋 Recent Trades                              │
│  [Trade Table]                                 │
├────────────────────────────────────────────────┤
│  ⚙️ Bot Configuration                          │
│  [Config Cards]                                │
└────────────────────────────────────────────────┘
```

---

## 🤝 Support

Bei Fragen oder Problemen:

1. Prüfe diese Dokumentation
2. Schaue in `logs/trading_bot.log`
3. Teste mit `python test_system.py`
4. Öffne ein Issue auf GitHub

---

## 📄 Lizenz

MIT License - Nutze frei für deine Trading-Projekte

---

**Happy Trading! 🚀📈**

Dashboard-Version: 1.0
Letzte Aktualisierung: Oktober 2024
