"""
binance_integration.py - Binance API Integration für Golden Cross Bot
=====================================================================

Vollständige Integration mit Binance für:
- Live-Preis-Daten (REST API)
- Historische Daten
- WebSocket für Echtzeit-Updates
- Order-Execution (Paper-Trading ready)
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException
    from binance import ThreadedWebSocketManager
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    logging.warning("python-binance nicht installiert. Installiere mit: pip install python-binance")

load_dotenv()
logger = logging.getLogger(__name__)


class BinanceDataProvider:
    """
    Binance Data Provider für Trading-Strategien
    
    Features:
    - Historische Kerzendaten (Candlesticks)
    - Live-Preise via REST API
    - WebSocket Streaming (optional)
    - Rate-Limit Handling
    - Error Recovery
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 testnet: bool = True):
        """
        Args:
            api_key: Binance API Key (optional für öffentliche Daten)
            api_secret: Binance API Secret
            testnet: True = Testnet, False = Production
        """
        if not BINANCE_AVAILABLE:
            raise ImportError(
                "python-binance nicht installiert.\n"
                "Installiere mit: pip install python-binance"
            )
        
        # API Credentials
        self.api_key = api_key or os.getenv('BINANCE_API_KEY', '')
        self.api_secret = api_secret or os.getenv('BINANCE_SECRET_KEY', '')
        self.testnet = testnet
        
        # Initialize Client
        if testnet:
            self.client = Client(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=True
            )
            logger.info("✓ Binance TESTNET Client initialisiert")
        else:
            self.client = Client(
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            logger.warning("⚠️ Binance PRODUCTION Client initialisiert")
        
        # WebSocket Manager (optional)
        self.ws_manager: Optional[ThreadedWebSocketManager] = None
        
        # Rate Limiting
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 200ms zwischen Requests
    
    def _rate_limit_check(self):
        """Prüfe und warte falls nötig wegen Rate Limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_historical_klines(self, symbol: str, interval: str, 
                             start_str: Optional[str] = None,
                             end_str: Optional[str] = None,
                             limit: int = 500) -> pd.DataFrame:
        """
        Hole historische Kerzendaten von Binance
        
        Args:
            symbol: Trading-Pair (z.B. 'BTCUSDT')
            interval: Zeitintervall (z.B. '1d', '4h', '15m')
            start_str: Start-Datum (z.B. "1 Jan, 2024")
            end_str: End-Datum
            limit: Max Anzahl Kerzen (max 1000)
        
        Returns:
            DataFrame mit OHLCV-Daten
        """
        logger.info(f"Lade historische Daten: {symbol} {interval}")
        
        try:
            self._rate_limit_check()
            
            # Hole Daten von Binance
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_str,
                end_str=end_str,
                limit=limit
            )
            
            if not klines:
                logger.warning(f"Keine Daten erhalten für {symbol}")
                return pd.DataFrame()
            
            # Konvertiere zu DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Cleanup und Konvertierung
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            # Konvertiere zu float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            # Behalte nur relevante Spalten
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            logger.info(f"✓ {len(df)} Kerzen geladen")
            return df
            
        except BinanceAPIException as e:
            logger.error(f"Binance API Fehler: {e}")
            raise
        except Exception as e:
            logger.error(f"Fehler beim Laden der Daten: {e}")
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """
        Hole aktuellen Preis
        
        Args:
            symbol: Trading-Pair (z.B. 'BTCUSDT')
        
        Returns:
            Aktueller Preis als float
        """
        try:
            self._rate_limit_check()
            
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            
            logger.debug(f"{symbol}: ${price:,.2f}")
            return price
            
        except BinanceAPIException as e:
            logger.error(f"Binance API Fehler: {e}")
            raise
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Hole Symbol-Informationen (Min Order Size, Precision, etc.)
        
        Args:
            symbol: Trading-Pair
        
        Returns:
            Dictionary mit Symbol-Informationen
        """
        try:
            self._rate_limit_check()
            
            info = self.client.get_symbol_info(symbol)
            
            # Extrahiere wichtige Infos
            filters = {f['filterType']: f for f in info['filters']}
            
            return {
                'symbol': info['symbol'],
                'status': info['status'],
                'baseAsset': info['baseAsset'],
                'quoteAsset': info['quoteAsset'],
                'pricePrecision': info['pricePrecision'],
                'quantityPrecision': info['quantityPrecision'],
                'minQty': float(filters.get('LOT_SIZE', {}).get('minQty', 0)),
                'maxQty': float(filters.get('LOT_SIZE', {}).get('maxQty', 0)),
                'stepSize': float(filters.get('LOT_SIZE', {}).get('stepSize', 0)),
                'minNotional': float(filters.get('MIN_NOTIONAL', {}).get('minNotional', 0))
            }
            
        except BinanceAPIException as e:
            logger.error(f"Binance API Fehler: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Teste Binance-Verbindung
        
        Returns:
            True wenn erfolgreich, False sonst
        """
        try:
            # Ping Server
            self.client.ping()
            logger.info("✓ Binance-Verbindung erfolgreich")
            
            # Teste API-Key (falls vorhanden)
            if self.api_key and self.api_secret:
                account = self.client.get_account()
                logger.info(f"✓ API-Key gültig (Account-Type: {account.get('accountType', 'N/A')})")
            
            return True
            
        except BinanceAPIException as e:
            logger.error(f"❌ Binance-Verbindung fehlgeschlagen: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler: {e}")
            return False
    
    def get_account_balance(self, asset: str = 'USDT') -> float:
        """
        Hole Account-Balance
        
        Args:
            asset: Asset-Symbol (z.B. 'USDT', 'BTC')
        
        Returns:
            Verfügbare Balance
        """
        if not self.api_key or not self.api_secret:
            logger.warning("Keine API-Credentials - Balance nicht verfügbar")
            return 0.0
        
        try:
            self._rate_limit_check()
            
            account = self.client.get_account()
            
            for balance in account['balances']:
                if balance['asset'] == asset:
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total = free + locked
                    
                    logger.info(f"{asset} Balance: ${total:.2f} (Free: ${free:.2f})")
                    return free
            
            logger.warning(f"{asset} nicht gefunden in Account")
            return 0.0
            
        except BinanceAPIException as e:
            logger.error(f"Binance API Fehler: {e}")
            return 0.0
    
    def close(self):
        """Cleanup - schließe WebSocket Verbindungen"""
        if self.ws_manager:
            logger.info("Schließe WebSocket Verbindungen...")
            self.ws_manager.stop()
            self.ws_manager = None


# ========== PAPIER-TRADING ORDER EXECUTOR ==========

class PaperTradingExecutor:
    """
    Simulated Order Executor für Paper-Trading
    
    Führt Orders nicht wirklich aus, sondern simuliert sie.
    Perfekt zum Testen ohne echtes Geld!
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        """
        Args:
            initial_capital: Startkapital in USDT
        """
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.trade_history: List[Dict[str, Any]] = []
        
        logger.info(f"✓ Paper-Trading Executor initialisiert")
        logger.info(f"  Initial Capital: ${initial_capital:,.2f}")
    
    def buy(self, symbol: str, quantity: float, price: float) -> Dict[str, Any]:
        """
        Simuliere BUY Order
        
        Args:
            symbol: Trading-Pair
            quantity: Menge
            price: Preis
        
        Returns:
            Order-Dictionary
        """
        cost = quantity * price
        
        if cost > self.capital:
            logger.error(f"❌ Nicht genug Kapital (Benötigt: ${cost:.2f}, Verfügbar: ${self.capital:.2f})")
            return {'status': 'FAILED', 'reason': 'Insufficient capital'}
        
        # Führe BUY aus
        self.capital -= cost
        self.positions[symbol] = {
            'quantity': quantity,
            'entry_price': price,
            'entry_time': datetime.now()
        }
        
        trade = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'side': 'BUY',
            'quantity': quantity,
            'price': price,
            'cost': cost,
            'capital_after': self.capital
        }
        self.trade_history.append(trade)
        
        logger.info(f"✓ BUY {quantity} {symbol} @ ${price:.2f} (Cost: ${cost:.2f})")
        return {'status': 'SUCCESS', 'trade': trade}
    
    def sell(self, symbol: str, price: float) -> Dict[str, Any]:
        """
        Simuliere SELL Order
        
        Args:
            symbol: Trading-Pair
            price: Preis
        
        Returns:
            Order-Dictionary
        """
        if symbol not in self.positions:
            logger.error(f"❌ Keine Position für {symbol}")
            return {'status': 'FAILED', 'reason': 'No position'}
        
        position = self.positions[symbol]
        quantity = position['quantity']
        entry_price = position['entry_price']
        
        # Berechne P&L
        revenue = quantity * price
        cost = quantity * entry_price
        pnl = revenue - cost
        pnl_pct = (pnl / cost) * 100
        
        # Führe SELL aus
        self.capital += revenue
        del self.positions[symbol]
        
        trade = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'side': 'SELL',
            'quantity': quantity,
            'price': price,
            'revenue': revenue,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'capital_after': self.capital
        }
        self.trade_history.append(trade)
        
        emoji = "💰" if pnl > 0 else "📉"
        logger.info(
            f"{emoji} SELL {quantity} {symbol} @ ${price:.2f} | "
            f"P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)"
        )
        
        return {'status': 'SUCCESS', 'trade': trade}
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Hole aktuelle Position"""
        return self.positions.get(symbol)
    
    def has_position(self, symbol: str) -> bool:
        """Prüfe ob Position existiert"""
        return symbol in self.positions
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Berechne aktuellen Portfolio-Wert
        
        Args:
            current_prices: Dictionary {symbol: price}
        
        Returns:
            Gesamtwert in USDT
        """
        total = self.capital  # Start mit verfügbarem Kapital
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                position_value = position['quantity'] * current_prices[symbol]
                total += position_value
        
        return total
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Hole Performance-Zusammenfassung"""
        total_pnl = self.capital - self.initial_capital
        roi = (total_pnl / self.initial_capital) * 100
        
        trades = [t for t in self.trade_history if t['side'] == 'SELL']
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.capital,
            'total_pnl': total_pnl,
            'roi': roi,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'win_rate': (len(winning_trades) / len(trades) * 100) if trades else 0,
            'open_positions': len(self.positions)
        }


# ========== BEISPIEL-VERWENDUNG ==========

def example_binance_integration():
    """Beispiel für Binance-Integration"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("  Binance Integration - Beispiel")
    print("=" * 70)
    
    # 1. Initialisiere Binance Client (Testnet)
    print("\n1. Initialisiere Binance Client...")
    provider = BinanceDataProvider(testnet=True)
    
    # 2. Teste Verbindung
    print("\n2. Teste Verbindung...")
    if not provider.test_connection():
        print("❌ Verbindung fehlgeschlagen!")
        return
    
    # 3. Hole historische Daten
    print("\n3. Lade historische Daten...")
    df = provider.get_historical_klines(
        symbol='BTCUSDT',
        interval='1d',
        start_str='1 Jan, 2024',
        limit=300
    )
    print(f"✓ {len(df)} Tages-Kerzen geladen")
    print(df.head())
    
    # 4. Hole aktuellen Preis
    print("\n4. Hole aktuellen Preis...")
    current_price = provider.get_current_price('BTCUSDT')
    print(f"BTC/USDT: ${current_price:,.2f}")
    
    # 5. Hole Symbol-Info
    print("\n5. Symbol-Informationen...")
    info = provider.get_symbol_info('BTCUSDT')
    print(f"Min Qty: {info['minQty']}")
    print(f"Price Precision: {info['pricePrecision']}")
    
    # 6. Paper-Trading Demo
    print("\n6. Paper-Trading Demo...")
    executor = PaperTradingExecutor(initial_capital=10000)
    
    # Simuliere BUY
    executor.buy('BTCUSDT', quantity=0.1, price=current_price)
    
    # Simuliere SELL (mit Profit)
    executor.sell('BTCUSDT', price=current_price * 1.05)
    
    # Performance
    perf = executor.get_performance_summary()
    print(f"\nPerformance:")
    print(f"  ROI: {perf['roi']:.2f}%")
    print(f"  Win Rate: {perf['win_rate']:.0f}%")
    
    # Cleanup
    provider.close()
    print("\n✓ Fertig!")


if __name__ == "__main__":
    example_binance_integration()
