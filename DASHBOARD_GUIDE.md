# 📊 Visual Dashboard Guide

## Übersicht

Das Enhanced Visual Dashboard ist eine leistungsstarke Erweiterung für den Trading-Bot, die es ermöglicht, Metriken und Diagramme zu verwalten und zu visualisieren.

---

## ✨ Features

### 🎯 Hauptfunktionen

- **Modal-Fenster**: Verwalten Sie Metriken und Diagramme über ein modales Interface
- **Mehrere Diagrammtypen**: Unterstützung für Linien-, Balken- und Kreisdiagramme
- **Echtzeitdaten**: Integration von Live-Daten aus dem Trading-Bot
- **Persistente Konfiguration**: Speicherung der Einstellungen im Browser-Cache oder Datenbank
- **Interaktive Charts**: Verwendung von Plotly für interaktive Visualisierungen
- **Export-Funktionen**: HTML-Export für einfaches Teilen

### 📈 Unterstützte Metriken

1. **Total P&L**: Gesamter Gewinn/Verlust
2. **Win Rate**: Gewinnrate in Prozent
3. **Total Trades**: Anzahl der ausgeführten Trades
4. **Best Trade**: Bester Trade
5. **Worst Trade**: Schlechtester Trade
6. **Average P&L**: Durchschnittlicher Gewinn/Verlust

### 📊 Unterstützte Diagrammtypen

1. **Liniendiagramm**: Zeigt P&L über Zeit
2. **Balkendiagramm**: Trades pro Strategie
3. **Kreisdiagramm**: Win/Loss Verteilung

---

## 🚀 Schnellstart

### Installation

Installieren Sie die erforderlichen Pakete:

```bash
pip install -r requirements.txt
```

Die neuen Abhängigkeiten umfassen:
- `matplotlib>=3.7.0` - Für statische Diagramme
- `plotly>=5.18.0` - Für interaktive Diagramme

### Erste Schritte

#### 1. Dashboard erstellen

```python
from dashboard import create_dashboard

# Dashboard initialisieren
dashboard = create_dashboard()
```

#### 2. Metriken anzeigen

```python
# In der Konsole anzeigen
dashboard.display_metrics_console()

# Programmatisch abrufen
metrics = dashboard.get_metrics()
print(metrics)
```

#### 3. HTML-Dashboard exportieren

```python
# Dashboard als HTML exportieren
dashboard.export_dashboard_html('data/dashboard.html')
```

#### 4. Diagramme generieren

```python
# Interaktive Plotly-Diagramme
charts = dashboard.generate_all_charts(use_plotly=True)

# Statische Matplotlib-Diagramme
charts = dashboard.generate_all_charts(use_plotly=False)
```

---

## 🔧 Modal-Fenster verwenden

### Modal öffnen und schließen

```python
from dashboard import DashboardModal

# Modal erstellen
modal = DashboardModal(dashboard)

# Modal öffnen
modal.open()

# Modal schließen
modal.close()
```

### Metriken hinzufügen/entfernen

```python
# Metrik hinzufügen
modal.open()
modal.add_metric('custom_metric')

# Metrik entfernen
modal.remove_metric('custom_metric')
modal.close()
```

### Diagramme hinzufügen/entfernen

```python
# Diagramm hinzufügen
modal.open()
modal.add_chart(
    chart_type='line',
    title='Custom Chart',
    data_source='pnl_history'
)

# Diagramm entfernen
modal.remove_chart('Custom Chart')
modal.close()
```

### Verfügbare Optionen abrufen

```python
# Verfügbare Metriken
metrics = modal.get_available_metrics()

# Verfügbare Diagrammtypen
chart_types = modal.get_available_chart_types()

# Verfügbare Datenquellen
data_sources = modal.get_available_data_sources()
```

---

## 💻 Demo-Anwendung

Eine interaktive Demo-Anwendung ist verfügbar:

```bash
python dashboard_demo.py
```

Die Demo bietet:
- Metriken-Anzeige
- Modal-Verwaltung
- Diagramm-Generierung
- HTML-Export

---

## 🎨 Konfiguration

### Dashboard-Konfiguration anpassen

Die Konfiguration wird in `data/dashboard_config.json` gespeichert:

```json
{
  "metrics": [
    "total_pnl",
    "win_rate",
    "total_trades"
  ],
  "charts": [
    {
      "type": "line",
      "title": "P&L Over Time",
      "data_source": "pnl_history"
    }
  ]
}
```

### Programmgesteuerte Konfiguration

```python
from dashboard import DashboardConfig

# Konfiguration laden
config = DashboardConfig('data/dashboard_config.json')

# Metriken anpassen
config.add_metric('new_metric')
config.remove_metric('old_metric')

# Diagramme anpassen
config.add_chart('bar', 'New Chart', 'strategy_stats')
config.remove_chart('Old Chart')

# Speichern
config.save_config()
```

---

## 📊 Datenquellen

### P&L History (`pnl_history`)

Zeigt die kumulative P&L über alle Trades:

```python
data = dashboard.get_chart_data('pnl_history')
# Returns: {'timestamps': [...], 'pnl': [...]}
```

### Strategy Statistics (`strategy_stats`)

Zeigt die Anzahl der Trades pro Strategie:

```python
data = dashboard.get_chart_data('strategy_stats')
# Returns: {'strategies': [...], 'counts': [...]}
```

### Win/Loss Distribution (`win_loss`)

Zeigt die Verteilung von gewinnenden vs. verlierenden Trades:

```python
data = dashboard.get_chart_data('win_loss')
# Returns: {'labels': ['Wins', 'Losses'], 'values': [wins, losses]}
```

---

## 🔌 Integration mit Trading-Bot

### In main.py integrieren

```python
from dashboard import create_dashboard, DashboardModal

class LiveTradingBot:
    def __init__(self):
        # ... bestehender Code ...
        
        # Dashboard hinzufügen
        self.dashboard = create_dashboard(
            trades_file=config.trades_file
        )
        self.dashboard_modal = DashboardModal(self.dashboard)
    
    def show_dashboard(self):
        """Zeige Dashboard-Metriken"""
        self.dashboard.display_metrics_console()
    
    def export_dashboard(self):
        """Exportiere Dashboard"""
        self.dashboard.export_dashboard_html()
        charts = self.dashboard.generate_all_charts()
        logger.info(f"Dashboard exportiert: {len(charts)} Charts")
```

---

## 🔍 Erweiterte Verwendung

### Benutzerdefinierte Diagramme

```python
# Benutzerdefinierten Chart erstellen
custom_chart = {
    'type': 'bar',
    'title': 'My Custom Chart',
    'data_source': 'strategy_stats'
}

# Chart generieren
dashboard.generate_chart_plotly(
    custom_chart,
    'data/charts/custom_chart.html'
)
```

### Mehrere Dashboards

```python
# Dashboard für verschiedene Zeiträume
dashboard_daily = create_dashboard(
    trades_file='data/trades_daily.csv',
    config_file='data/dashboard_daily_config.json'
)

dashboard_weekly = create_dashboard(
    trades_file='data/trades_weekly.csv',
    config_file='data/dashboard_weekly_config.json'
)
```

---

## 📱 Browser-Cache & Speicherung

Die Dashboard-Konfiguration wird automatisch in einer JSON-Datei gespeichert:

- **Speicherort**: `data/dashboard_config.json`
- **Automatisches Speichern**: Bei jeder Änderung über Modal
- **Automatisches Laden**: Beim Dashboard-Start

### Cache leeren

```bash
rm data/dashboard_config.json
```

Das Dashboard verwendet dann die Standard-Konfiguration.

---

## 🎯 Best Practices

### 1. Regelmäßige Dashboard-Updates

```python
# Dashboard alle 5 Minuten aktualisieren
import time

while trading:
    # ... Trading-Logik ...
    
    if time.time() % 300 == 0:  # Alle 5 Minuten
        dashboard.display_metrics_console()
```

### 2. Diagramme nach Trading-Session speichern

```python
def shutdown(self):
    # ... Shutdown-Logik ...
    
    # Dashboard exportieren
    self.dashboard.export_dashboard_html()
    self.dashboard.generate_all_charts()
```

### 3. Modal nur bei Bedarf öffnen

```python
# Modal nur bei Konfiguration öffnen
if user_wants_to_configure:
    modal.open()
    # ... Konfiguration ...
    modal.close()
```

---

## 🐛 Fehlerbehebung

### Matplotlib nicht verfügbar

```bash
pip install matplotlib
```

### Plotly nicht verfügbar

```bash
pip install plotly
```

### Keine Trades vorhanden

Stellen Sie sicher, dass `data/trades.csv` existiert und Trades enthält:

```python
from utils import load_trades_from_csv

trades = load_trades_from_csv('data/trades.csv')
print(f"Anzahl Trades: {len(trades)}")
```

### Charts werden nicht generiert

Überprüfen Sie die Logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 API-Referenz

### DashboardConfig

```python
class DashboardConfig:
    def __init__(self, config_file: str)
    def load_config(self)
    def save_config(self)
    def add_metric(self, metric: str)
    def remove_metric(self, metric: str)
    def add_chart(self, chart_type: str, title: str, data_source: str)
    def remove_chart(self, title: str)
```

### VisualDashboard

```python
class VisualDashboard:
    def __init__(self, trades_file: str, config_file: str)
    def get_metrics(self) -> Dict[str, Any]
    def get_chart_data(self, data_source: str) -> Dict[str, Any]
    def generate_chart_matplotlib(self, chart_config: Dict, output_file: str) -> bool
    def generate_chart_plotly(self, chart_config: Dict, output_file: str) -> bool
    def generate_all_charts(self, output_dir: str, use_plotly: bool) -> List[str]
    def display_metrics_console(self)
    def export_dashboard_html(self, output_file: str)
```

### DashboardModal

```python
class DashboardModal:
    def __init__(self, dashboard: VisualDashboard)
    def open(self)
    def close(self)
    def add_metric(self, metric: str) -> bool
    def remove_metric(self, metric: str) -> bool
    def add_chart(self, chart_type: str, title: str, data_source: str) -> bool
    def remove_chart(self, title: str) -> bool
    def get_available_metrics(self) -> List[str]
    def get_available_chart_types(self) -> List[str]
    def get_available_data_sources(self) -> List[str]
```

---

## 🚀 Nächste Schritte

### Geplante Erweiterungen

- [ ] Echtzeit-WebSocket-Updates
- [ ] Erweiterte Diagrammtypen (Scatter, Heatmap)
- [ ] Benutzerdefinierte Metriken
- [ ] Multi-Symbol-Dashboards
- [ ] Dashboard-Templates
- [ ] Alarm-System für Metriken
- [ ] Export zu PDF/Excel

---

## 📞 Support

Bei Fragen oder Problemen:
1. Überprüfen Sie die Logs in `logs/trading_bot.log`
2. Führen Sie die Tests aus: `python test_dashboard.py`
3. Konsultieren Sie die FAQ im README.md

---

## ⚖️ Lizenz

Dieses Feature ist Teil des Trading-Bot-Projekts und unterliegt der gleichen Lizenz.

**Hinweis**: Nur für Bildungszwecke. Kein Finanzberatungsinstrument.
