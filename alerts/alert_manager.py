"""
Unified Alert Manager
=====================
Zentrales Alert-System für alle Benachrichtigungskanäle.
"""
import logging
from typing import Optional, Dict, Any, List
from .telegram_alert import TelegramAlert
from .email_alert import EmailAlert

logger = logging.getLogger(__name__)


class AlertManager:
    """
    Zentraler Alert Manager für Multi-Channel Benachrichtigungen
    
    Features:
    - Telegram Integration
    - Email Integration
    - Discord Integration (geplant)
    - Alert Priorität & Routing
    - Rate Limiting
    """
    
    def __init__(
        self,
        enable_telegram: bool = True,
        enable_email: bool = True,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        smtp_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialisiere Alert Manager
        
        Args:
            enable_telegram: Aktiviere Telegram Alerts
            enable_email: Aktiviere Email Alerts
            telegram_bot_token: Telegram Bot Token
            telegram_chat_id: Telegram Chat ID
            smtp_config: SMTP Konfiguration für Email
        """
        # Initialisiere Telegram
        self.telegram = TelegramAlert(
            bot_token=telegram_bot_token,
            chat_id=telegram_chat_id,
            enabled=enable_telegram
        )
        
        # Initialisiere Email
        if smtp_config:
            self.email = EmailAlert(
                smtp_host=smtp_config.get('host'),
                smtp_port=smtp_config.get('port'),
                smtp_user=smtp_config.get('user'),
                smtp_password=smtp_config.get('password'),
                from_email=smtp_config.get('from_email'),
                to_email=smtp_config.get('to_email'),
                enabled=enable_email
            )
        else:
            self.email = EmailAlert(enabled=enable_email)
        
        # Alert Statistiken
        self.stats = {
            'telegram_sent': 0,
            'telegram_failed': 0,
            'email_sent': 0,
            'email_failed': 0,
            'total_alerts': 0
        }
        
        logger.info("✓ Alert Manager initialisiert")
        self._log_status()
    
    def _log_status(self):
        """Logge Status aller Alert-Kanäle"""
        status = []
        if self.telegram.enabled:
            status.append("Telegram ✓")
        if self.email.enabled:
            status.append("Email ✓")
        
        if status:
            logger.info(f"Aktive Alert-Kanäle: {', '.join(status)}")
        else:
            logger.warning("⚠️ Keine Alert-Kanäle aktiviert")
    
    def send_trade_alert(
        self,
        order_type: str,
        symbol: str,
        price: float,
        quantity: float,
        strategies: List[str],
        capital: float,
        pnl: float = 0.0,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Sende Trade-Benachrichtigung über alle aktiven Kanäle
        
        Args:
            order_type: BUY oder SELL
            symbol: Trading-Symbol
            price: Ausführungspreis
            quantity: Menge
            strategies: Liste ausgelöster Strategien
            capital: Aktuelles Kapital
            pnl: Profit/Loss
            channels: Liste von Kanälen (None = alle)
            
        Returns:
            Dictionary mit Erfolgs-Status pro Kanal
        """
        results = {}
        self.stats['total_alerts'] += 1
        
        # Telegram
        if (channels is None or 'telegram' in channels) and self.telegram.enabled:
            success = self.telegram.send_trade_alert(
                order_type, symbol, price, quantity, strategies, capital, pnl
            )
            results['telegram'] = success
            if success:
                self.stats['telegram_sent'] += 1
            else:
                self.stats['telegram_failed'] += 1
        
        # Email
        if (channels is None or 'email' in channels) and self.email.enabled:
            success = self.email.send_trade_alert(
                order_type, symbol, price, quantity, strategies, capital, pnl
            )
            results['email'] = success
            if success:
                self.stats['email_sent'] += 1
            else:
                self.stats['email_failed'] += 1
        
        return results
    
    def send_circuit_breaker_alert(
        self,
        drawdown: float,
        limit: float,
        capital: float,
        initial_capital: float,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Sende Circuit Breaker Alarm über alle aktiven Kanäle
        
        Args:
            drawdown: Aktueller Drawdown (%)
            limit: Drawdown-Limit (%)
            capital: Aktuelles Kapital
            initial_capital: Startkapital
            channels: Liste von Kanälen (None = alle)
            
        Returns:
            Dictionary mit Erfolgs-Status pro Kanal
        """
        results = {}
        self.stats['total_alerts'] += 1
        
        # Telegram
        if (channels is None or 'telegram' in channels) and self.telegram.enabled:
            success = self.telegram.send_circuit_breaker_alert(
                drawdown, limit, capital, initial_capital
            )
            results['telegram'] = success
            if success:
                self.stats['telegram_sent'] += 1
            else:
                self.stats['telegram_failed'] += 1
        
        # Email
        if (channels is None or 'email' in channels) and self.email.enabled:
            success = self.email.send_circuit_breaker_alert(
                drawdown, limit, capital, initial_capital
            )
            results['email'] = success
            if success:
                self.stats['email_sent'] += 1
            else:
                self.stats['email_failed'] += 1
        
        return results
    
    def send_performance_update(
        self,
        capital: float,
        initial_capital: float,
        total_trades: int,
        win_rate: float,
        profit_factor: float,
        sharpe_ratio: float,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Sende Performance-Update über alle aktiven Kanäle
        
        Args:
            capital: Aktuelles Kapital
            initial_capital: Startkapital
            total_trades: Anzahl Trades
            win_rate: Gewinnrate (%)
            profit_factor: Profit Factor
            sharpe_ratio: Sharpe Ratio
            channels: Liste von Kanälen (None = alle)
            
        Returns:
            Dictionary mit Erfolgs-Status pro Kanal
        """
        results = {}
        self.stats['total_alerts'] += 1
        
        # Telegram
        if (channels is None or 'telegram' in channels) and self.telegram.enabled:
            success = self.telegram.send_performance_update(
                capital, initial_capital, total_trades, 
                win_rate, profit_factor, sharpe_ratio
            )
            results['telegram'] = success
            if success:
                self.stats['telegram_sent'] += 1
            else:
                self.stats['telegram_failed'] += 1
        
        # Email
        if (channels is None or 'email' in channels) and self.email.enabled:
            success = self.email.send_performance_report(
                capital, initial_capital, total_trades,
                win_rate, profit_factor, sharpe_ratio
            )
            results['email'] = success
            if success:
                self.stats['email_sent'] += 1
            else:
                self.stats['email_failed'] += 1
        
        return results
    
    def send_error_alert(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Sende Fehler-Benachrichtigung
        
        Args:
            error_type: Art des Fehlers
            error_message: Fehlermeldung
            context: Zusätzlicher Kontext
            channels: Liste von Kanälen (None = alle)
            
        Returns:
            Dictionary mit Erfolgs-Status pro Kanal
        """
        results = {}
        self.stats['total_alerts'] += 1
        
        # Telegram
        if (channels is None or 'telegram' in channels) and self.telegram.enabled:
            success = self.telegram.send_error_alert(
                error_type, error_message, context
            )
            results['telegram'] = success
            if success:
                self.stats['telegram_sent'] += 1
            else:
                self.stats['telegram_failed'] += 1
        
        # Email (nutzt Generic Message)
        if (channels is None or 'email' in channels) and self.email.enabled:
            subject = f"❌ Fehler: {error_type}"
            body = f"Fehler: {error_message}\n"
            if context:
                body += "\nKontext:\n"
                for key, value in context.items():
                    body += f"• {key}: {value}\n"
            
            success = self.email.send_email(subject, body, priority="high")
            results['email'] = success
            if success:
                self.stats['email_sent'] += 1
            else:
                self.stats['email_failed'] += 1
        
        return results
    
    def send_custom_message(
        self,
        message: str,
        subject: Optional[str] = None,
        channels: Optional[List[str]] = None,
        priority: str = "normal"
    ) -> Dict[str, bool]:
        """
        Sende benutzerdefinierte Nachricht
        
        Args:
            message: Nachrichtentext
            subject: Email Betreff (optional)
            channels: Liste von Kanälen (None = alle)
            priority: normal, high, low
            
        Returns:
            Dictionary mit Erfolgs-Status pro Kanal
        """
        results = {}
        self.stats['total_alerts'] += 1
        
        # Telegram
        if (channels is None or 'telegram' in channels) and self.telegram.enabled:
            success = self.telegram.send_message(message)
            results['telegram'] = success
            if success:
                self.stats['telegram_sent'] += 1
            else:
                self.stats['telegram_failed'] += 1
        
        # Email
        if (channels is None or 'email' in channels) and self.email.enabled:
            email_subject = subject or "Trading Bot Benachrichtigung"
            success = self.email.send_email(
                email_subject, message, priority=priority
            )
            results['email'] = success
            if success:
                self.stats['email_sent'] += 1
            else:
                self.stats['email_failed'] += 1
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Hole Alert-Statistiken
        
        Returns:
            Dictionary mit Statistiken
        """
        return self.stats.copy()
    
    def is_any_channel_active(self) -> bool:
        """
        Prüfe ob mindestens ein Kanal aktiv ist
        
        Returns:
            True wenn mindestens ein Kanal aktiv
        """
        return self.telegram.enabled or self.email.enabled


# Demo
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test Alert Manager
    alert_manager = AlertManager()
    
    if alert_manager.is_any_channel_active():
        # Test Trade Alert
        results = alert_manager.send_trade_alert(
            order_type="BUY",
            symbol="BTC/USDT",
            price=50000.0,
            quantity=0.1,
            strategies=["RSI", "EMA Crossover"],
            capital=10500.0,
            pnl=500.0
        )
        
        print(f"Trade Alert Results: {results}")
        
        # Test Performance Update
        results = alert_manager.send_performance_update(
            capital=10500.0,
            initial_capital=10000.0,
            total_trades=25,
            win_rate=65.0,
            profit_factor=1.8,
            sharpe_ratio=1.5
        )
        
        print(f"Performance Update Results: {results}")
        
        # Zeige Statistiken
        stats = alert_manager.get_statistics()
        print(f"\nAlert-Statistiken: {stats}")
    else:
        print("⚠️ Keine Alert-Kanäle konfiguriert")
