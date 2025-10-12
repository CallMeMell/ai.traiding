# 🎬 Video Strategy Implementation Guide - FDmV1bIub_s

**Implementierungsanleitung für YouTube-Video: https://youtu.be/FDmV1bIub_s**

---

## 📋 Übersicht

Dieses Dokument beschreibt die Implementierung einer Trading-Strategie basierend auf dem YouTube-Video mit der ID `FDmV1bIub_s`. Die Implementierung nutzt das Enhanced Base Strategy Framework.

---

## 🎯 Video-Analyse

### Schritt 1: Video analysieren

1. **Video ansehen**: https://youtu.be/FDmV1bIub_s
2. **Kernpunkte dokumentieren**:
   - Welche Indikatoren werden verwendet? (z.B. MA, RSI, MACD, Bollinger Bands)
   - Welche Zeitrahmen werden empfohlen? (z.B. 15m, 1h, 4h)
   - Was sind die Entry-Bedingungen?
   - Was sind die Exit-Bedingungen?
   - Welche Risk-Management-Regeln werden verwendet?
   - Gibt es besondere Filter oder Bestätigungen?

### Schritt 2: Parameter definieren

Basierend auf der Video-Analyse, definiere alle Parameter:

```python
# Beispiel-Parameter (anpassen basierend auf Video)
video_params = {
    # Indikatoren
    'ema_fast': 12,
    'ema_slow': 26,
    'macd_signal': 9,
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'atr_period': 14,
    
    # Entry-Regeln
    'require_volume_confirmation': True,
    'min_volume_ratio': 1.5,
    'require_trend_confirmation': True,
    
    # Exit-Regeln
    'use_trailing_stop': True,
    'trailing_stop_atr_mult': 2.0,
    'take_profit_atr_mult': 3.0,
    
    # Risk Management
    'max_risk_per_trade': 0.02,  # 2%
    'position_sizing': 'fixed'    # oder 'volatility_based'
}
```

---

## 🔨 Implementierung

### Template-Strategie

```python
from base_strategy import EnhancedBaseStrategy
import pandas as pd
import numpy as np

class VideoStrategy_FDmV1bIub_s(EnhancedBaseStrategy):
    """
    Trading-Strategie basierend auf YouTube-Video FDmV1bIub_s
    
    Diese Strategie implementiert:
    - [Beschreibe die Hauptkomponenten]
    - [Beschreibe Entry-Logik]
    - [Beschreibe Exit-Logik]
    - [Beschreibe Risk Management]
    """
    
    def __init__(self, params):
        super().__init__("Video_FDmV1bIub_s", params)
        
        # Extrahiere Parameter aus Video
        self.ema_fast = params.get('ema_fast', 12)
        self.ema_slow = params.get('ema_slow', 26)
        self.macd_signal = params.get('macd_signal', 9)
        self.rsi_period = params.get('rsi_period', 14)
        self.rsi_oversold = params.get('rsi_oversold', 30)
        self.rsi_overbought = params.get('rsi_overbought', 70)
        self.atr_period = params.get('atr_period', 14)
        
        # Entry/Exit Regeln
        self.require_volume_confirmation = params.get('require_volume_confirmation', True)
        self.min_volume_ratio = params.get('min_volume_ratio', 1.5)
        self.require_trend_confirmation = params.get('require_trend_confirmation', True)
        
        # Risk Management
        self.trailing_stop_atr_mult = params.get('trailing_stop_atr_mult', 2.0)
        self.take_profit_atr_mult = params.get('take_profit_atr_mult', 3.0)
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generiere Trading-Signal basierend auf Video-Strategie
        
        Args:
            df: DataFrame mit OHLCV-Daten
        
        Returns:
            1 = BUY, 0 = HOLD, -1 = SELL
        """
        if not self.validate_data(df):
            return 0
        
        # Benötige genug Daten für alle Indikatoren
        min_periods = max(self.ema_slow, self.rsi_period, self.atr_period) + 10
        if len(df) < min_periods:
            return 0
        
        df_copy = df.copy()
        
        # ========== INDIKATOREN BERECHNEN ==========
        
        # 1. EMAs für Trend-Richtung
        df_copy['ema_fast'] = df_copy['close'].ewm(
            span=self.ema_fast, adjust=False
        ).mean()
        df_copy['ema_slow'] = df_copy['close'].ewm(
            span=self.ema_slow, adjust=False
        ).mean()
        
        # 2. MACD für Momentum
        ema_12 = df_copy['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df_copy['close'].ewm(span=26, adjust=False).mean()
        df_copy['macd'] = ema_12 - ema_26
        df_copy['macd_signal'] = df_copy['macd'].ewm(
            span=self.macd_signal, adjust=False
        ).mean()
        df_copy['macd_hist'] = df_copy['macd'] - df_copy['macd_signal']
        
        # 3. RSI für Überkauft/Überverkauft
        delta = df_copy['close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        rs = avg_gain / avg_loss
        df_copy['rsi'] = 100 - (100 / (1 + rs))
        
        # 4. ATR für Volatilität
        high_low = df_copy['high'] - df_copy['low']
        high_close = np.abs(df_copy['high'] - df_copy['close'].shift())
        low_close = np.abs(df_copy['low'] - df_copy['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df_copy['atr'] = true_range.rolling(self.atr_period).mean()
        
        # 5. Volume-Bestätigung
        df_copy['avg_volume'] = df_copy['volume'].rolling(20).mean()
        df_copy['volume_ratio'] = df_copy['volume'] / df_copy['avg_volume']
        
        # ========== SIGNALE GENERIEREN ==========
        
        # Aktuelle Werte
        ema_fast_curr = df_copy['ema_fast'].iloc[-1]
        ema_slow_curr = df_copy['ema_slow'].iloc[-1]
        macd_curr = df_copy['macd'].iloc[-1]
        macd_signal_curr = df_copy['macd_signal'].iloc[-1]
        macd_hist_curr = df_copy['macd_hist'].iloc[-1]
        rsi_curr = df_copy['rsi'].iloc[-1]
        volume_ratio_curr = df_copy['volume_ratio'].iloc[-1]
        
        # Vorherige Werte (für Crossover-Erkennung)
        ema_fast_prev = df_copy['ema_fast'].iloc[-2]
        ema_slow_prev = df_copy['ema_slow'].iloc[-2]
        macd_hist_prev = df_copy['macd_hist'].iloc[-2]
        
        # NaN-Check
        if pd.isna(ema_fast_curr) or pd.isna(rsi_curr) or pd.isna(macd_curr):
            return 0
        
        # ========== BUY-SIGNAL ==========
        buy_conditions = []
        
        # 1. Trend: EMA Fast > EMA Slow (Aufwärtstrend)
        if self.require_trend_confirmation:
            buy_conditions.append(ema_fast_curr > ema_slow_curr)
        
        # 2. EMA Crossover (bullish)
        ema_crossover_bullish = (ema_fast_curr > ema_slow_curr and 
                                 ema_fast_prev <= ema_slow_prev)
        buy_conditions.append(ema_crossover_bullish)
        
        # 3. MACD Histogram steigt (Momentum)
        buy_conditions.append(macd_hist_curr > macd_hist_prev)
        buy_conditions.append(macd_curr > macd_signal_curr)
        
        # 4. RSI nicht überkauft
        buy_conditions.append(rsi_curr < self.rsi_overbought)
        
        # 5. Volume-Bestätigung
        if self.require_volume_confirmation:
            buy_conditions.append(volume_ratio_curr >= self.min_volume_ratio)
        
        # BUY wenn alle Bedingungen erfüllt
        if all(buy_conditions):
            return 1  # BUY
        
        # ========== SELL-SIGNAL ==========
        sell_conditions = []
        
        # 1. Trend: EMA Fast < EMA Slow (Abwärtstrend)
        if self.require_trend_confirmation:
            sell_conditions.append(ema_fast_curr < ema_slow_curr)
        
        # 2. EMA Crossover (bearish)
        ema_crossover_bearish = (ema_fast_curr < ema_slow_curr and 
                                 ema_fast_prev >= ema_slow_prev)
        sell_conditions.append(ema_crossover_bearish)
        
        # 3. MACD Histogram fällt
        sell_conditions.append(macd_hist_curr < macd_hist_prev)
        sell_conditions.append(macd_curr < macd_signal_curr)
        
        # 4. RSI nicht überverkauft
        sell_conditions.append(rsi_curr > self.rsi_oversold)
        
        # 5. Volume-Bestätigung
        if self.require_volume_confirmation:
            sell_conditions.append(volume_ratio_curr >= self.min_volume_ratio)
        
        # SELL wenn alle Bedingungen erfüllt
        if all(sell_conditions):
            return -1  # SELL
        
        return 0  # HOLD
    
    def _calculate_confidence(self, df: pd.DataFrame, signal: int) -> float:
        """
        Berechne Confidence-Score für das Signal
        
        Returns:
            Confidence zwischen 0 und 1
        """
        if signal == 0:
            return 0.0
        
        # Einfaches Beispiel: Basierend auf RSI-Distanz
        df_copy = df.copy()
        delta = df_copy['close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi_curr = rsi.iloc[-1]
        
        if pd.isna(rsi_curr):
            return 0.5
        
        if signal == 1:  # BUY
            # Je mehr überverkauft, desto höher die Confidence
            distance_from_oversold = max(0, self.rsi_oversold - rsi_curr)
            confidence = min(1.0, 0.5 + (distance_from_oversold / self.rsi_oversold))
        else:  # SELL
            # Je mehr überkauft, desto höher die Confidence
            distance_from_overbought = max(0, rsi_curr - self.rsi_overbought)
            confidence = min(1.0, 0.5 + (distance_from_overbought / (100 - self.rsi_overbought)))
        
        return confidence
```

---

## 📝 Registrierung

### 1. In config.py hinzufügen

```python
strategies: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
    # ... bestehende Strategien ...
    "video_strategy": {
        "ema_fast": 12,
        "ema_slow": 26,
        "macd_signal": 9,
        "rsi_period": 14,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "atr_period": 14,
        "require_volume_confirmation": True,
        "min_volume_ratio": 1.5,
        "require_trend_confirmation": True,
        "trailing_stop_atr_mult": 2.0,
        "take_profit_atr_mult": 3.0
    }
})
```

### 2. In strategy.py registrieren

```python
# In der Datei mit deiner Strategie-Implementierung
from video_strategy import VideoStrategy_FDmV1bIub_s

# In StrategyManager.__init__
self.STRATEGY_MAP['video_strategy'] = VideoStrategy_FDmV1bIub_s
```

### 3. Aktivieren

```python
active_strategies: list = field(default_factory=lambda: [
    "video_strategy",
    # ... andere Strategien
])
```

---

## 🧪 Testing

### Backtesting

```python
from backtester import Backtester
from utils import generate_sample_data

# Konfiguration
config = {
    'initial_capital': 10000,
    'trade_size': 100,
    'active_strategies': ['video_strategy'],
    'cooperation_logic': 'OR',
    'strategies': {
        'video_strategy': {
            'ema_fast': 12,
            'ema_slow': 26,
            # ... weitere Parameter
        }
    }
}

# Historische Daten laden
df = generate_sample_data(n_bars=1000, start_price=50000)

# Backtest durchführen
backtester = Backtester(config)
results = backtester.run(df)

# Ergebnisse analysieren
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
```

### Paper Trading

```powershell
# Windows PowerShell
$env:DRY_RUN = "true"
.\venv\Scripts\python.exe main.py
```

---

## 📊 Performance-Erwartungen

Basierend auf dem Video sollte die Strategie folgende Eigenschaften haben:

- **Win Rate**: [Aus Video entnehmen]
- **Durchschnittlicher Gewinn pro Trade**: [Aus Video entnehmen]
- **Max Drawdown**: [Aus Video entnehmen]
- **Empfohlene Zeitrahmen**: [Aus Video entnehmen]
- **Beste Marktbedingungen**: [Aus Video entnehmen]

---

## ⚠️ Wichtige Hinweise

1. **Immer zuerst Paper Trading**: Teste die Strategie ausgiebig mit `DRY_RUN=true`
2. **Backtesting ist keine Garantie**: Historische Performance garantiert keine zukünftigen Ergebnisse
3. **Risk Management**: Verwende immer Stop-Loss und Position Sizing
4. **Marktbedingungen**: Die Strategie funktioniert möglicherweise besser in bestimmten Marktphasen
5. **Parameter-Optimierung**: Passe Parameter basierend auf Backtesting-Ergebnissen an
6. **Überwachung**: Überwache die Strategie kontinuierlich im Live-Betrieb

---

## 📚 Zusätzliche Ressourcen

- [Base Strategy Guide](BASE_STRATEGY_GUIDE.md) - Vollständige Dokumentation des Frameworks
- [Backtesting Guide](../BACKTESTING_GUIDE.md) - Anleitung zum Backtesting
- [Live Trading Setup](../LIVE_TRADING_SETUP_GUIDE.md) - Live-Trading-Anleitung
- YouTube-Video: https://youtu.be/FDmV1bIub_s

---

## 📞 Support

Bei Fragen oder Problemen:

1. Überprüfe die Dokumentation
2. Teste mit Backtesting
3. Aktiviere Debug-Logging: `log_level="DEBUG"`
4. Öffne ein GitHub Issue mit Details

---

**Made for Windows ⭐ | Video-Based Strategy | Always Paper Trade First!**
