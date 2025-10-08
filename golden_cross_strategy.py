"""
golden_cross_strategy.py - Professionelle Golden Cross / Death Cross Strategie
==============================================================================

Die Golden Cross Strategie ist eine klassische Trend-Following Strategie:
- Golden Cross: MA_50 kreuzt ÜBER MA_200 → Bullish (BUY)
- Death Cross:  MA_50 kreuzt UNTER MA_200 → Bearish (SELL)

Features:
- Whipsaw-Schutz durch Confirmation Period
- Volumen-Bestätigung
- Trend-Stärke-Filter
- Umfassendes Risikomanagement
- Detailliertes Logging
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

# Import aus Master-Version
from strategy import BaseStrategy

logger = logging.getLogger(__name__)


class GoldenCrossStrategy(BaseStrategy):
    """
    Golden Cross / Death Cross Trading-Strategie
    
    Klassische Trend-Following Strategie mit:
    - 50-Tage MA (kurzfristig)
    - 200-Tage MA (langfristig)
    
    Golden Cross = Bullish Signal (BUY)
    Death Cross = Bearish Signal (SELL)
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Args:
            params: Parameter-Dictionary mit:
                - short_window: Kurzfristiger MA (default: 50)
                - long_window: Langfristiger MA (default: 200)
                - confirmation_days: Tage zur Bestätigung (default: 3)
                - min_spread_pct: Minimum Spread in % (default: 1.0)
                - volume_confirmation: Volumen prüfen? (default: True)
                - trend_strength_filter: Trend-Stärke prüfen? (default: True)
                - volatility_filter: Volatilität prüfen? (default: True)
                - max_volatility: Max erlaubte Volatilität (default: 0.05)
        """
        super().__init__("GoldenCross", params)
        
        # MA Windows
        self.short_window = params.get('short_window', 50)
        self.long_window = params.get('long_window', 200)
        
        # Confirmation & Filters
        self.confirmation_days = params.get('confirmation_days', 3)
        self.min_spread_pct = params.get('min_spread_pct', 1.0)
        self.volume_confirmation = params.get('volume_confirmation', True)
        self.trend_strength_filter = params.get('trend_strength_filter', True)
        self.volatility_filter = params.get('volatility_filter', True)
        self.max_volatility = params.get('max_volatility', 0.05)  # 5%
        
        # State tracking für Confirmation
        self.last_cross_date: Optional[datetime] = None
        self.last_cross_type: Optional[str] = None  # 'golden' oder 'death'
        self.confirmed: bool = False
        
        logger.info(f"✓ Golden Cross Strategie initialisiert")
        logger.info(f"  - Short MA: {self.short_window} Tage")
        logger.info(f"  - Long MA:  {self.long_window} Tage")
        logger.info(f"  - Confirmation: {self.confirmation_days} Tage")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Berechne alle benötigten Indikatoren
        
        Args:
            df: OHLCV DataFrame
        
        Returns:
            DataFrame mit zusätzlichen Spalten:
            - MA_50, MA_200: Moving Averages
            - volume_sma: Volumen-Durchschnitt
            - volatility: Tägliche Volatilität
            - trend_strength: Trend-Stärke Indikator
        """
        df_copy = df.copy()
        
        # Moving Averages
        df_copy[f'MA_{self.short_window}'] = df_copy['close'].rolling(
            window=self.short_window, 
            min_periods=self.short_window
        ).mean()
        
        df_copy[f'MA_{self.long_window}'] = df_copy['close'].rolling(
            window=self.long_window, 
            min_periods=self.long_window
        ).mean()
        
        # Spread zwischen MAs (für Flat Market Detection)
        df_copy['ma_spread'] = abs(
            df_copy[f'MA_{self.short_window}'] - df_copy[f'MA_{self.long_window}']
        )
        df_copy['ma_spread_pct'] = (df_copy['ma_spread'] / df_copy['close']) * 100
        
        # Volumen-Durchschnitt (für Volume Confirmation)
        df_copy['volume_sma'] = df_copy['volume'].rolling(
            window=20, 
            min_periods=20
        ).mean()
        
        # Volatilität (für Volatility Filter)
        df_copy['returns'] = df_copy['close'].pct_change()
        df_copy['volatility'] = df_copy['returns'].rolling(
            window=20, 
            min_periods=20
        ).std()
        
        # Trend-Stärke (beide MAs sollten in gleiche Richtung zeigen)
        if self.trend_strength_filter:
            df_copy['ma_short_slope'] = df_copy[f'MA_{self.short_window}'].diff()
            df_copy['ma_long_slope'] = df_copy[f'MA_{self.long_window}'].diff()
        
        return df_copy
    
    def detect_cross(self, df: pd.DataFrame) -> Tuple[Optional[str], Optional[datetime]]:
        """
        Erkenne Golden Cross oder Death Cross
        
        Args:
            df: DataFrame mit berechneten MAs
        
        Returns:
            (cross_type, cross_date) oder (None, None)
            cross_type: 'golden' oder 'death'
        """
        if len(df) < 2:
            return None, None
        
        # Aktuelle und vorherige MA-Werte
        ma_short_curr = df[f'MA_{self.short_window}'].iloc[-1]
        ma_short_prev = df[f'MA_{self.short_window}'].iloc[-2]
        ma_long_curr = df[f'MA_{self.long_window}'].iloc[-1]
        ma_long_prev = df[f'MA_{self.long_window}'].iloc[-2]
        
        # Prüfe auf NaN
        if any(pd.isna(val) for val in [ma_short_curr, ma_short_prev, ma_long_curr, ma_long_prev]):
            return None, None
        
        cross_date = df['timestamp'].iloc[-1] if 'timestamp' in df.columns else datetime.now()
        
        # GOLDEN CROSS: Short MA kreuzt ÜBER Long MA
        if ma_short_prev <= ma_long_prev and ma_short_curr > ma_long_curr:
            logger.info(f"🌟 GOLDEN CROSS erkannt am {cross_date}")
            logger.info(f"   MA_{self.short_window}: {ma_short_curr:.2f}")
            logger.info(f"   MA_{self.long_window}: {ma_long_curr:.2f}")
            return 'golden', cross_date
        
        # DEATH CROSS: Short MA kreuzt UNTER Long MA
        elif ma_short_prev >= ma_long_prev and ma_short_curr < ma_long_curr:
            logger.info(f"💀 DEATH CROSS erkannt am {cross_date}")
            logger.info(f"   MA_{self.short_window}: {ma_short_curr:.2f}")
            logger.info(f"   MA_{self.long_window}: {ma_long_curr:.2f}")
            return 'death', cross_date
        
        return None, None
    
    def check_confirmation(self, df: pd.DataFrame, cross_type: str) -> bool:
        """
        Prüfe ob Cross nach Confirmation Period noch gültig ist
        
        Args:
            df: DataFrame mit aktuellen Daten
            cross_type: 'golden' oder 'death'
        
        Returns:
            True wenn bestätigt, False sonst
        """
        if len(df) < 1:
            return False
        
        ma_short = df[f'MA_{self.short_window}'].iloc[-1]
        ma_long = df[f'MA_{self.long_window}'].iloc[-1]
        
        if pd.isna(ma_short) or pd.isna(ma_long):
            return False
        
        # Prüfe ob Cross noch intakt ist
        if cross_type == 'golden':
            # Short MA muss immer noch über Long MA sein
            confirmed = ma_short > ma_long
            if confirmed:
                logger.info(f"✓ Golden Cross bestätigt nach {self.confirmation_days} Tagen")
            else:
                logger.warning(f"✗ Golden Cross ungültig geworden (Whipsaw)")
            return confirmed
        
        elif cross_type == 'death':
            # Short MA muss immer noch unter Long MA sein
            confirmed = ma_short < ma_long
            if confirmed:
                logger.info(f"✓ Death Cross bestätigt nach {self.confirmation_days} Tagen")
            else:
                logger.warning(f"✗ Death Cross ungültig geworden (Whipsaw)")
            return confirmed
        
        return False
    
    def check_spread_filter(self, df: pd.DataFrame) -> bool:
        """
        Prüfe ob Spread zwischen MAs groß genug ist (Flat Market Filter)
        
        Args:
            df: DataFrame mit ma_spread_pct
        
        Returns:
            True wenn Spread ausreichend, False sonst
        """
        if 'ma_spread_pct' not in df.columns:
            return True  # Wenn nicht berechnet, ignoriere Filter
        
        spread_pct = df['ma_spread_pct'].iloc[-1]
        
        if pd.isna(spread_pct):
            return True
        
        if spread_pct < self.min_spread_pct:
            logger.warning(
                f"⚠️ Spread zu klein ({spread_pct:.2f}% < {self.min_spread_pct}%) - "
                f"Möglicher Flat Market"
            )
            return False
        
        logger.info(f"✓ Spread Filter passed ({spread_pct:.2f}%)")
        return True
    
    def check_volume_confirmation(self, df: pd.DataFrame) -> bool:
        """
        Prüfe ob Volumen das Signal bestätigt
        
        Args:
            df: DataFrame mit volume und volume_sma
        
        Returns:
            True wenn Volumen erhöht, False sonst
        """
        if not self.volume_confirmation:
            return True  # Filter deaktiviert
        
        if 'volume_sma' not in df.columns or len(df) < 1:
            return True  # Wenn nicht verfügbar, ignoriere
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume_sma'].iloc[-1]
        
        if pd.isna(current_volume) or pd.isna(avg_volume):
            return True
        
        # Volumen sollte mindestens 120% des Durchschnitts sein
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio < 1.2:
            logger.warning(
                f"⚠️ Volumen-Bestätigung fehlt "
                f"(Ratio: {volume_ratio:.2f}x < 1.2x)"
            )
            return False
        
        logger.info(f"✓ Volumen-Bestätigung ({volume_ratio:.2f}x Durchschnitt)")
        return True
    
    def check_trend_strength(self, df: pd.DataFrame, cross_type: str) -> bool:
        """
        Prüfe Trend-Stärke (beide MAs sollten in gleiche Richtung zeigen)
        
        Args:
            df: DataFrame mit ma_short_slope und ma_long_slope
            cross_type: 'golden' oder 'death'
        
        Returns:
            True wenn Trend stark, False sonst
        """
        if not self.trend_strength_filter:
            return True  # Filter deaktiviert
        
        if 'ma_short_slope' not in df.columns or len(df) < 1:
            return True
        
        short_slope = df['ma_short_slope'].iloc[-1]
        long_slope = df['ma_long_slope'].iloc[-1]
        
        if pd.isna(short_slope) or pd.isna(long_slope):
            return True
        
        if cross_type == 'golden':
            # Beide MAs sollten steigen
            both_rising = short_slope > 0 and long_slope > 0
            if not both_rising:
                logger.warning(
                    f"⚠️ Trend-Stärke schwach "
                    f"(Short: {short_slope:.2f}, Long: {long_slope:.2f})"
                )
            else:
                logger.info("✓ Starker Aufwärtstrend bestätigt")
            return both_rising
        
        elif cross_type == 'death':
            # Beide MAs sollten fallen
            both_falling = short_slope < 0 and long_slope < 0
            if not both_falling:
                logger.warning(
                    f"⚠️ Trend-Stärke schwach "
                    f"(Short: {short_slope:.2f}, Long: {long_slope:.2f})"
                )
            else:
                logger.info("✓ Starker Abwärtstrend bestätigt")
            return both_falling
        
        return True
    
    def check_volatility_filter(self, df: pd.DataFrame) -> bool:
        """
        Prüfe ob Volatilität im akzeptablen Bereich ist
        
        Args:
            df: DataFrame mit volatility
        
        Returns:
            True wenn Volatilität OK, False wenn zu hoch
        """
        if not self.volatility_filter:
            return True  # Filter deaktiviert
        
        if 'volatility' not in df.columns or len(df) < 1:
            return True
        
        volatility = df['volatility'].iloc[-1]
        
        if pd.isna(volatility):
            return True
        
        if volatility > self.max_volatility:
            logger.warning(
                f"⚠️ Volatilität zu hoch "
                f"({volatility:.4f} > {self.max_volatility:.4f}) - "
                f"Extrem unsicherer Markt"
            )
            return False
        
        logger.info(f"✓ Volatilität OK ({volatility:.4f})")
        return True
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generiere Trading-Signal basierend auf Golden/Death Cross
        
        Args:
            df: DataFrame mit OHLCV-Daten
        
        Returns:
            1 = BUY (Golden Cross bestätigt)
            0 = HOLD
            -1 = SELL (Death Cross bestätigt)
        """
        if not self.enabled:
            return 0
        
        if not self.validate_data(df):
            return 0
        
        # Brauche mindestens long_window + confirmation_days + 1 Datenpunkte
        min_data = self.long_window + self.confirmation_days + 1
        if len(df) < min_data:
            logger.debug(
                f"Nicht genug Daten für Golden Cross "
                f"({len(df)} < {min_data})"
            )
            return 0
        
        # Berechne alle Indikatoren
        df_ind = self.calculate_indicators(df)
        
        # Erkenne neue Crosses
        cross_type, cross_date = self.detect_cross(df_ind)
        
        if cross_type:
            # Neuer Cross erkannt
            self.last_cross_date = cross_date
            self.last_cross_type = cross_type
            self.confirmed = False
            
            logger.info(f"Warte {self.confirmation_days} Tage zur Bestätigung...")
            return 0  # HOLD während Confirmation Period
        
        # Prüfe ob wir in Confirmation Period sind
        if self.last_cross_date and not self.confirmed:
            current_date = df_ind['timestamp'].iloc[-1] if 'timestamp' in df_ind.columns else datetime.now()
            
            # Konvertiere zu datetime wenn nötig
            if isinstance(current_date, str):
                current_date = pd.to_datetime(current_date)
            if isinstance(self.last_cross_date, str):
                self.last_cross_date = pd.to_datetime(self.last_cross_date)
            
            days_since_cross = (current_date - self.last_cross_date).days
            
            if days_since_cross >= self.confirmation_days:
                # Confirmation Period vorbei - prüfe Bestätigung
                
                # 1. Prüfe ob Cross noch intakt
                if not self.check_confirmation(df_ind, self.last_cross_type):
                    logger.warning("Cross nicht mehr gültig - zurücksetzen")
                    self.last_cross_date = None
                    self.last_cross_type = None
                    return 0  # HOLD
                
                # 2. Prüfe Spread Filter
                if not self.check_spread_filter(df_ind):
                    logger.warning("Spread Filter nicht bestanden")
                    self.last_cross_date = None
                    self.last_cross_type = None
                    return 0  # HOLD
                
                # 3. Prüfe Volumen-Bestätigung
                if not self.check_volume_confirmation(df_ind):
                    logger.warning("Volumen-Bestätigung fehlgeschlagen")
                    self.last_cross_date = None
                    self.last_cross_type = None
                    return 0  # HOLD
                
                # 4. Prüfe Trend-Stärke
                if not self.check_trend_strength(df_ind, self.last_cross_type):
                    logger.warning("Trend-Stärke nicht ausreichend")
                    self.last_cross_date = None
                    self.last_cross_type = None
                    return 0  # HOLD
                
                # 5. Prüfe Volatilität
                if not self.check_volatility_filter(df_ind):
                    logger.warning("Volatilität zu hoch")
                    self.last_cross_date = None
                    self.last_cross_type = None
                    return 0  # HOLD
                
                # ALLE FILTER BESTANDEN!
                self.confirmed = True
                
                if self.last_cross_type == 'golden':
                    logger.info("=" * 60)
                    logger.info("🎯 GOLDEN CROSS VOLLSTÄNDIG BESTÄTIGT - BUY SIGNAL!")
                    logger.info("=" * 60)
                    return 1  # BUY
                
                elif self.last_cross_type == 'death':
                    logger.info("=" * 60)
                    logger.info("🎯 DEATH CROSS VOLLSTÄNDIG BESTÄTIGT - SELL SIGNAL!")
                    logger.info("=" * 60)
                    return -1  # SELL
            
            else:
                # Noch in Confirmation Period
                logger.debug(
                    f"Confirmation läuft: {days_since_cross}/{self.confirmation_days} Tage"
                )
                return 0  # HOLD
        
        # Kein aktives Signal
        return 0  # HOLD
    
    def get_info(self) -> Dict[str, Any]:
        """
        Hole erweiterte Strategie-Informationen
        
        Returns:
            Dictionary mit Status und Parametern
        """
        base_info = super().get_info()
        
        # Füge Golden Cross spezifische Info hinzu
        base_info.update({
            'short_window': self.short_window,
            'long_window': self.long_window,
            'confirmation_days': self.confirmation_days,
            'last_cross_type': self.last_cross_type,
            'last_cross_date': str(self.last_cross_date) if self.last_cross_date else None,
            'confirmed': self.confirmed,
            'filters': {
                'spread': {'enabled': True, 'min_pct': self.min_spread_pct},
                'volume': {'enabled': self.volume_confirmation},
                'trend_strength': {'enabled': self.trend_strength_filter},
                'volatility': {'enabled': self.volatility_filter, 'max': self.max_volatility}
            }
        })
        
        return base_info


# ========== BEISPIEL-VERWENDUNG ==========

def example_usage():
    """Beispiel für die Verwendung der Golden Cross Strategie"""
    
    # Setup Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 1. Erstelle Strategie mit Standard-Parametern
    params = {
        'short_window': 50,
        'long_window': 200,
        'confirmation_days': 3,
        'min_spread_pct': 1.0,
        'volume_confirmation': True,
        'trend_strength_filter': True,
        'volatility_filter': True,
        'max_volatility': 0.05
    }
    
    strategy = GoldenCrossStrategy(params)
    
    # 2. Generiere Test-Daten (in Production: von Binance API)
    from utils import generate_sample_data
    df = generate_sample_data(n_bars=300, start_price=30000)
    
    # 3. Generiere Signal
    signal = strategy.generate_signal(df)
    
    signal_text = {1: "BUY", 0: "HOLD", -1: "SELL"}[signal]
    print(f"\nSignal: {signal_text}")
    
    # 4. Hole Strategie-Info
    info = strategy.get_info()
    print(f"\nStrategie-Info: {info}")


if __name__ == "__main__":
    example_usage()
