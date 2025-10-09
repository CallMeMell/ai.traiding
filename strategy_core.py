"""
strategy_core.py - Reversal-Trailing-Stop Strategie
====================================================
Kernstrategie mit sofortigem Markteinstieg, dynamischem Stop-Loss
und automatischer Richtungsumkehr bei Stop-Loss-Durchbruch.

Diese Strategie kombiniert:
- Sofortige Markteinstiege basierend auf Trendumkehrungen
- Dynamischen Trailing Stop-Loss
- Automatische Positionsumkehr bei Stop-Loss Trigger
- Take-Profit Management
"""

import logging
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ReversalTrailingStopStrategy:
    """
    Reversal-Trailing-Stop Strategie
    
    Diese aggressive Strategie:
    1. Erkennt Trendumkehrungen durch Momentum-Indikatoren
    2. Steigt sofort mit Marktorder ein
    3. Setzt dynamischen Trailing-Stop-Loss
    4. Wechselt bei Stop-Loss-Durchbruch sofort die Richtung
    5. Nutzt Take-Profit für Gewinnmitnahmen
    
    Parameter:
    - lookback_period: Periode für Trendanalyse (default: 20)
    - trailing_stop_pct: Trailing Stop in Prozent (default: 2.0%)
    - take_profit_pct: Take-Profit in Prozent (default: 5.0%)
    - reversal_threshold: Schwellwert für Trendumkehr (default: 0.6)
    - atr_multiplier: ATR Multiplikator für Stop-Loss (default: 2.0)
    """
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        Initialisiere Reversal-Trailing-Stop Strategie
        
        Args:
            params: Parameter-Dictionary mit optionalen Werten
        """
        # Default-Parameter
        default_params = {
            'lookback_period': 20,
            'trailing_stop_pct': 2.0,
            'take_profit_pct': 5.0,
            'reversal_threshold': 0.6,
            'atr_multiplier': 2.0,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'volume_threshold': 1.5  # Volumen-Multiplikator für Bestätigung
        }
        
        self.params = {**default_params, **(params or {})}
        self.name = "Reversal-Trailing-Stop"
        self.enabled = True
        
        # Position State
        self.current_position = 0  # 1 = Long, -1 = Short, 0 = None
        self.entry_price = 0.0
        self.stop_loss = 0.0
        self.take_profit = 0.0
        self.highest_price = 0.0  # Für Trailing Stop (Long)
        self.lowest_price = float('inf')  # Für Trailing Stop (Short)
        
        logger.info(f"✓ {self.name} Strategie initialisiert mit Parametern: {self.params}")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Berechnet technische Indikatoren für die Strategie
        
        Args:
            df: DataFrame mit OHLCV-Daten
            
        Returns:
            DataFrame mit zusätzlichen Indikator-Spalten
        """
        df = df.copy()
        
        # RSI (Relative Strength Index)
        df['rsi'] = self._calculate_rsi(df['close'], self.params['rsi_period'])
        
        # ATR (Average True Range) für volatilitätsbasierte Stops
        df['atr'] = self._calculate_atr(df, 14)
        
        # Moving Averages für Trendrichtung
        df['sma_short'] = df['close'].rolling(window=10).mean()
        df['sma_long'] = df['close'].rolling(window=self.params['lookback_period']).mean()
        
        # MACD für Momentum
        df['macd'], df['macd_signal'] = self._calculate_macd(df['close'])
        
        # Volumen-Analyse
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Momentum Score
        df['momentum'] = self._calculate_momentum_score(df)
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generiert Trading-Signal
        
        Args:
            df: DataFrame mit OHLCV-Daten
            
        Returns:
            1 = BUY, -1 = SELL, 0 = HOLD
        """
        if len(df) < self.params['lookback_period'] + 20:
            logger.debug("Nicht genug Daten für Signal-Generierung")
            return 0
        
        # Berechne Indikatoren
        df = self.calculate_indicators(df)
        
        # Aktuelle Werte
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Update Trailing Stops wenn Position offen
        if self.current_position != 0:
            self._update_trailing_stops(current['close'])
        
        # Prüfe Stop-Loss und Take-Profit
        if self.current_position != 0:
            exit_signal = self._check_exit_conditions(current['close'])
            if exit_signal != 0:
                return exit_signal
        
        # Nur neue Signale wenn keine Position offen
        if self.current_position == 0:
            signal = self._detect_reversal_signal(df, current, previous)
            if signal != 0:
                # Setze Entry-Parameter
                self._set_entry_parameters(current['close'], current['atr'], signal)
            return signal
        
        return 0  # HOLD
    
    def _detect_reversal_signal(
        self, 
        df: pd.DataFrame, 
        current: pd.Series, 
        previous: pd.Series
    ) -> int:
        """
        Erkennt Trendumkehrungen
        
        Args:
            df: Vollständiger DataFrame
            current: Aktuelle Kerze
            previous: Vorherige Kerze
            
        Returns:
            1 = Bullish Reversal, -1 = Bearish Reversal, 0 = Keine Umkehr
        """
        # Score System für Reversal-Signale
        bullish_score = 0
        bearish_score = 0
        
        # 1. RSI Reversal
        if current['rsi'] < self.params['rsi_oversold'] and previous['rsi'] >= self.params['rsi_oversold']:
            bullish_score += 1
        if current['rsi'] > self.params['rsi_overbought'] and previous['rsi'] <= self.params['rsi_overbought']:
            bearish_score += 1
        
        # 2. MACD Crossover
        if current['macd'] > current['macd_signal'] and previous['macd'] <= previous['macd_signal']:
            bullish_score += 1
        if current['macd'] < current['macd_signal'] and previous['macd'] >= previous['macd_signal']:
            bearish_score += 1
        
        # 3. MA Crossover
        if current['sma_short'] > current['sma_long'] and previous['sma_short'] <= previous['sma_long']:
            bullish_score += 1
        if current['sma_short'] < current['sma_long'] and previous['sma_short'] >= previous['sma_long']:
            bearish_score += 1
        
        # 4. Momentum Score
        if current['momentum'] > self.params['reversal_threshold']:
            bullish_score += 1
        if current['momentum'] < -self.params['reversal_threshold']:
            bearish_score += 1
        
        # 5. Volumen-Bestätigung
        if current['volume_ratio'] > self.params['volume_threshold']:
            if bullish_score > bearish_score:
                bullish_score += 1
            elif bearish_score > bullish_score:
                bearish_score += 1
        
        # Entscheidung basierend auf Score
        min_score = 2  # Mindestens 2 Indikatoren müssen übereinstimmen
        
        if bullish_score >= min_score and bullish_score > bearish_score:
            logger.info(f"🔄 Bullish Reversal erkannt (Score: {bullish_score})")
            return 1
        elif bearish_score >= min_score and bearish_score > bullish_score:
            logger.info(f"🔄 Bearish Reversal erkannt (Score: {bearish_score})")
            return -1
        
        return 0
    
    def _set_entry_parameters(self, entry_price: float, atr: float, direction: int):
        """
        Setzt Entry-Parameter für neue Position
        
        Args:
            entry_price: Einstiegspreis
            atr: Average True Range
            direction: 1 für Long, -1 für Short
        """
        self.current_position = direction
        self.entry_price = entry_price
        
        # Berechne Stop-Loss basierend auf ATR und Trailing-Stop-Prozent
        atr_stop = atr * self.params['atr_multiplier']
        pct_stop = entry_price * (self.params['trailing_stop_pct'] / 100)
        stop_distance = max(atr_stop, pct_stop)
        
        if direction == 1:  # Long
            self.stop_loss = entry_price - stop_distance
            self.take_profit = entry_price * (1 + self.params['take_profit_pct'] / 100)
            self.highest_price = entry_price
            logger.info(f"📈 LONG Position @ {entry_price:.2f} | SL: {self.stop_loss:.2f} | TP: {self.take_profit:.2f}")
        else:  # Short
            self.stop_loss = entry_price + stop_distance
            self.take_profit = entry_price * (1 - self.params['take_profit_pct'] / 100)
            self.lowest_price = entry_price
            logger.info(f"📉 SHORT Position @ {entry_price:.2f} | SL: {self.stop_loss:.2f} | TP: {self.take_profit:.2f}")
    
    def _update_trailing_stops(self, current_price: float):
        """
        Aktualisiert Trailing Stop-Loss
        
        Args:
            current_price: Aktueller Marktpreis
        """
        if self.current_position == 1:  # Long Position
            # Update höchsten Preis
            if current_price > self.highest_price:
                self.highest_price = current_price
                
                # Berechne neuen Trailing Stop
                new_stop = self.highest_price * (1 - self.params['trailing_stop_pct'] / 100)
                
                # Nur nach oben anpassen
                if new_stop > self.stop_loss:
                    old_stop = self.stop_loss
                    self.stop_loss = new_stop
                    logger.debug(f"🔺 Trailing Stop angepasst: {old_stop:.2f} -> {new_stop:.2f}")
        
        elif self.current_position == -1:  # Short Position
            # Update niedrigsten Preis
            if current_price < self.lowest_price:
                self.lowest_price = current_price
                
                # Berechne neuen Trailing Stop
                new_stop = self.lowest_price * (1 + self.params['trailing_stop_pct'] / 100)
                
                # Nur nach unten anpassen
                if new_stop < self.stop_loss:
                    old_stop = self.stop_loss
                    self.stop_loss = new_stop
                    logger.debug(f"🔻 Trailing Stop angepasst: {old_stop:.2f} -> {new_stop:.2f}")
    
    def _check_exit_conditions(self, current_price: float) -> int:
        """
        Prüft Exit-Bedingungen (Stop-Loss, Take-Profit)
        
        Args:
            current_price: Aktueller Marktpreis
            
        Returns:
            Signal für Exit: -1 für Long Exit (wird zu Short), 
                           1 für Short Exit (wird zu Long),
                           0 für kein Exit
        """
        if self.current_position == 1:  # Long Position
            # Stop-Loss Hit -> Reversal zu Short
            if current_price <= self.stop_loss:
                logger.warning(f"⛔ Stop-Loss Hit bei Long! {current_price:.2f} <= {self.stop_loss:.2f}")
                logger.info(f"🔄 REVERSAL: Long -> Short")
                # Bereite Short-Position vor
                self._reset_position()
                return -1  # Signal für Short Entry
            
            # Take-Profit Hit -> Close Position
            if current_price >= self.take_profit:
                logger.info(f"🎯 Take-Profit erreicht bei Long! {current_price:.2f} >= {self.take_profit:.2f}")
                pnl = current_price - self.entry_price
                logger.info(f"💰 P&L: ${pnl:.2f} ({(pnl/self.entry_price)*100:.2f}%)")
                self._reset_position()
                return 0  # Neutral - Position nur schließen
        
        elif self.current_position == -1:  # Short Position
            # Stop-Loss Hit -> Reversal zu Long
            if current_price >= self.stop_loss:
                logger.warning(f"⛔ Stop-Loss Hit bei Short! {current_price:.2f} >= {self.stop_loss:.2f}")
                logger.info(f"🔄 REVERSAL: Short -> Long")
                # Bereite Long-Position vor
                self._reset_position()
                return 1  # Signal für Long Entry
            
            # Take-Profit Hit -> Close Position
            if current_price <= self.take_profit:
                logger.info(f"🎯 Take-Profit erreicht bei Short! {current_price:.2f} <= {self.take_profit:.2f}")
                pnl = self.entry_price - current_price
                logger.info(f"💰 P&L: ${pnl:.2f} ({(pnl/self.entry_price)*100:.2f}%)")
                self._reset_position()
                return 0  # Neutral - Position nur schließen
        
        return 0  # Keine Exit-Bedingung erfüllt
    
    def _reset_position(self):
        """Setzt Position-State zurück"""
        self.current_position = 0
        self.entry_price = 0.0
        self.stop_loss = 0.0
        self.take_profit = 0.0
        self.highest_price = 0.0
        self.lowest_price = float('inf')
    
    # ========== TECHNISCHE INDIKATOREN ==========
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Berechnet Relative Strength Index (RSI)
        
        Args:
            prices: Preis-Serie
            period: RSI-Periode
            
        Returns:
            RSI-Werte
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Berechnet Average True Range (ATR)
        
        Args:
            df: DataFrame mit OHLC-Daten
            period: ATR-Periode
            
        Returns:
            ATR-Werte
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def _calculate_macd(
        prices: pd.Series, 
        fast: int = 12, 
        slow: int = 26, 
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Berechnet MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: Preis-Serie
            fast: Schnelle EMA-Periode
            slow: Langsame EMA-Periode
            signal: Signal-Linie-Periode
            
        Returns:
            (MACD-Linie, Signal-Linie)
        """
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        
        return macd, macd_signal
    
    def _calculate_momentum_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Berechnet Momentum-Score basierend auf mehreren Faktoren
        
        Args:
            df: DataFrame mit Indikatoren
            
        Returns:
            Momentum-Score (-1 bis 1)
        """
        # Normalisiere Indikatoren
        rsi_norm = (df['rsi'] - 50) / 50  # -1 bis 1
        
        # MACD Momentum
        macd_diff = df['macd'] - df['macd_signal']
        macd_norm = np.tanh(macd_diff / df['close'] * 100)  # Normalisiert auf -1 bis 1
        
        # MA Trend
        ma_diff = df['sma_short'] - df['sma_long']
        ma_norm = np.tanh(ma_diff / df['close'] * 10)
        
        # Gewichteter Durchschnitt
        momentum = (rsi_norm * 0.3 + macd_norm * 0.4 + ma_norm * 0.3)
        
        return momentum
    
    # ========== UTILITY METHODS ==========
    
    def get_position_info(self) -> Dict[str, Any]:
        """
        Gibt aktuelle Position-Informationen zurück
        
        Returns:
            Dictionary mit Position-Details
        """
        return {
            'position': 'LONG' if self.current_position == 1 else ('SHORT' if self.current_position == -1 else 'NONE'),
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'highest_price': self.highest_price if self.current_position == 1 else None,
            'lowest_price': self.lowest_price if self.current_position == -1 else None
        }
    
    def update_params(self, new_params: Dict[str, Any]):
        """
        Aktualisiert Strategie-Parameter
        
        Args:
            new_params: Neue Parameter
        """
        self.params.update(new_params)
        logger.info(f"Parameter aktualisiert für {self.name}: {new_params}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Gibt Strategie-Informationen zurück
        
        Returns:
            Dictionary mit Strategie-Details
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'params': self.params,
            'position': self.get_position_info()
        }


# ========== INTEGRATION MIT BESTEHENDEM SYSTEM ==========

def integrate_with_backtester():
    """
    Beispiel-Integration mit dem bestehenden Backtester
    
    Diese Funktion zeigt, wie die Strategie im Backtester verwendet werden kann.
    """
    from backtester import Backtester
    from utils import generate_sample_data
    
    # Erstelle Strategie mit angepassten Parametern
    strategy = ReversalTrailingStopStrategy({
        'lookback_period': 20,
        'trailing_stop_pct': 2.5,
        'take_profit_pct': 6.0,
        'reversal_threshold': 0.5,
        'atr_multiplier': 2.5
    })
    
    # Generiere Test-Daten
    data = generate_sample_data(n_bars=1000, start_price=30000)
    
    # Führe Backtest durch
    print("=" * 70)
    print("🔄 REVERSAL-TRAILING-STOP STRATEGIE BACKTEST")
    print("=" * 70)
    
    results = []
    position = 0
    entry_price = 0
    
    for i in range(strategy.params['lookback_period'] + 20, len(data)):
        window = data.iloc[:i+1]
        signal = strategy.generate_signal(window)
        
        current_price = window.iloc[-1]['close']
        
        if signal != 0 and signal != position:
            if position != 0:
                # Close existing position
                pnl = (current_price - entry_price) * position
                results.append({
                    'entry': entry_price,
                    'exit': current_price,
                    'side': 'LONG' if position == 1 else 'SHORT',
                    'pnl': pnl
                })
                print(f"{'🟢 LONG' if position == 1 else '🔴 SHORT'} EXIT @ {current_price:.2f} | P&L: ${pnl:.2f}")
            
            # Open new position
            position = signal
            entry_price = current_price
            print(f"{'🟢 LONG' if signal == 1 else '🔴 SHORT'} ENTRY @ {entry_price:.2f}")
    
    # Statistiken
    if results:
        total_pnl = sum(r['pnl'] for r in results)
        winning_trades = [r for r in results if r['pnl'] > 0]
        win_rate = len(winning_trades) / len(results) * 100
        
        print("\n" + "=" * 70)
        print("📊 ERGEBNISSE")
        print("=" * 70)
        print(f"Total Trades: {len(results)}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Total P&L: ${total_pnl:.2f}")
        print("=" * 70)


if __name__ == "__main__":
    # Test der Strategie
    print("🔄 Reversal-Trailing-Stop Strategie - Test")
    print("=" * 70)
    
    # Erstelle Strategie
    strategy = ReversalTrailingStopStrategy()
    print(f"\n✓ Strategie erstellt: {strategy.name}")
    print(f"✓ Parameter: {strategy.params}")
    
    # Zeige Info
    info = strategy.get_info()
    print(f"\n📋 Strategie-Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Test erfolgreich abgeschlossen!")
    print("\n💡 Tipp: Nutze 'integrate_with_backtester()' für vollständigen Backtest")
