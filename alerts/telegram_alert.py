"""
Telegram Alert Integration
===========================
Sendet Trading-Benachrichtigungen über Telegram Bot API.
"""
import os
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramAlert:
    """
    Telegram Bot für Trading-Benachrichtigungen
    
    Features:
    - Trade Alerts (BUY/SELL)
    - Performance Updates
    - Circuit Breaker Alerts
    - Error Notifications
    """
    
    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        enabled: bool = True
    ):
        """
        Initialisiere Telegram Bot
        
        Args:
            bot_token: Telegram Bot Token (von BotFather)
            chat_id: Chat/Channel ID für Nachrichten
            enabled: Aktiviere/Deaktiviere Telegram Alerts
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.enabled = enabled and bool(self.bot_token) and bool(self.chat_id)
        
        if not self.enabled:
            if not self.bot_token or not self.chat_id:
                logger.info("⚠️ Telegram Alerts deaktiviert (fehlende Credentials)")
            else:
                logger.info("⚠️ Telegram Alerts deaktiviert (enabled=False)")
        else:
            logger.info("✓ Telegram Alerts aktiviert")
            self._verify_connection()
    
    def _verify_connection(self) -> bool:
        """
        Verifiziere Telegram Bot Verbindung
        
        Returns:
            True wenn Verbindung erfolgreich
        """
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"✓ Telegram Bot verbunden: @{bot_info['result']['username']}")
                return True
            else:
                logger.warning(f"⚠️ Telegram Bot Verbindung fehlgeschlagen: {response.status_code}")
                self.enabled = False
                return False
        except Exception as e:
            logger.warning(f"⚠️ Telegram Bot Verbindung fehlgeschlagen: {e}")
            self.enabled = False
            return False
    
    def send_message(
        self,
        message: str,
        parse_mode: str = "HTML",
        disable_notification: bool = False
    ) -> bool:
        """
        Sende Telegram Nachricht
        
        Args:
            message: Nachrichtentext
            parse_mode: HTML oder Markdown
            disable_notification: Silent notification
            
        Returns:
            True wenn erfolgreich gesendet
        """
        if not self.enabled:
            logger.debug("Telegram deaktiviert - Nachricht nicht gesendet")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification
            }
            
            response = requests.post(url, data=payload, timeout=10)
            
            if response.status_code == 200:
                logger.debug("✓ Telegram Nachricht gesendet")
                return True
            else:
                logger.error(f"❌ Telegram Fehler: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Telegram Fehler: {e}")
            return False
    
    def send_trade_alert(
        self,
        order_type: str,
        symbol: str,
        price: float,
        quantity: float,
        strategies: list,
        capital: float,
        pnl: float = 0.0
    ) -> bool:
        """
        Sende Trade-Benachrichtigung
        
        Args:
            order_type: BUY oder SELL
            symbol: Trading-Symbol (z.B. BTC/USDT)
            price: Ausführungspreis
            quantity: Menge
            strategies: Liste ausgelöster Strategien
            capital: Aktuelles Kapital
            pnl: Profit/Loss
            
        Returns:
            True wenn erfolgreich
        """
        emoji = "📈" if order_type == "BUY" else "📉"
        strategies_str = ", ".join(strategies) if strategies else "N/A"
        
        message = f"""
{emoji} <b>{order_type} Signal</b>

<b>Symbol:</b> {symbol}
<b>Preis:</b> ${price:,.2f}
<b>Menge:</b> {quantity:.6f}
<b>Strategien:</b> {strategies_str}
<b>Kapital:</b> ${capital:,.2f}
"""
        
        if pnl != 0:
            pnl_emoji = "💰" if pnl > 0 else "📉"
            message += f"<b>P&L:</b> {pnl_emoji} ${pnl:+,.2f} ({pnl/capital*100:+.2f}%)\n"
        
        message += f"\n<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return self.send_message(message)
    
    def send_circuit_breaker_alert(
        self,
        drawdown: float,
        limit: float,
        capital: float,
        initial_capital: float
    ) -> bool:
        """
        Sende Circuit Breaker Alarm
        
        Args:
            drawdown: Aktueller Drawdown (%)
            limit: Drawdown-Limit (%)
            capital: Aktuelles Kapital
            initial_capital: Startkapital
            
        Returns:
            True wenn erfolgreich
        """
        loss = initial_capital - capital
        loss_pct = (loss / initial_capital) * 100
        
        message = f"""
🚨 <b>CIRCUIT BREAKER AUSGELÖST!</b>

⚠️ Trading wurde automatisch gestoppt!

<b>Drawdown:</b> {drawdown:.2f}% (Limit: {limit:.2f}%)
<b>Verlust:</b> ${loss:,.2f} ({loss_pct:.2f}%)
<b>Verbleibendes Kapital:</b> ${capital:,.2f}
<b>Start-Kapital:</b> ${initial_capital:,.2f}

<i>Bitte System überprüfen!</i>
<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message, disable_notification=False)
    
    def send_performance_update(
        self,
        capital: float,
        initial_capital: float,
        total_trades: int,
        win_rate: float,
        profit_factor: float,
        sharpe_ratio: float
    ) -> bool:
        """
        Sende Performance-Update
        
        Args:
            capital: Aktuelles Kapital
            initial_capital: Startkapital
            total_trades: Anzahl Trades
            win_rate: Gewinnrate (%)
            profit_factor: Profit Factor
            sharpe_ratio: Sharpe Ratio
            
        Returns:
            True wenn erfolgreich
        """
        roi = ((capital - initial_capital) / initial_capital) * 100
        emoji = "📊" if roi >= 0 else "📉"
        
        message = f"""
{emoji} <b>Performance Update</b>

<b>ROI:</b> {roi:+.2f}%
<b>Kapital:</b> ${capital:,.2f} (Start: ${initial_capital:,.2f})
<b>Trades:</b> {total_trades}
<b>Win Rate:</b> {win_rate:.1f}%
<b>Profit Factor:</b> {profit_factor:.2f}
<b>Sharpe Ratio:</b> {sharpe_ratio:.2f}

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message, disable_notification=True)
    
    def send_error_alert(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Sende Fehler-Benachrichtigung
        
        Args:
            error_type: Art des Fehlers
            error_message: Fehlermeldung
            context: Zusätzlicher Kontext
            
        Returns:
            True wenn erfolgreich
        """
        message = f"""
❌ <b>Fehler: {error_type}</b>

<b>Meldung:</b> {error_message}
"""
        
        if context:
            message += "\n<b>Kontext:</b>\n"
            for key, value in context.items():
                message += f"• {key}: {value}\n"
        
        message += f"\n<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return self.send_message(message)


def send_telegram_alert(message: str) -> bool:
    """
    Convenience-Funktion für einfache Telegram Alerts
    
    Args:
        message: Nachrichtentext
        
    Returns:
        True wenn erfolgreich
    """
    bot = TelegramAlert()
    return bot.send_message(message)


# Demo
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test Telegram Alert
    bot = TelegramAlert()
    
    if bot.enabled:
        # Test Trade Alert
        bot.send_trade_alert(
            order_type="BUY",
            symbol="BTC/USDT",
            price=50000.0,
            quantity=0.1,
            strategies=["RSI", "EMA Crossover"],
            capital=10500.0,
            pnl=500.0
        )
        
        # Test Performance Update
        bot.send_performance_update(
            capital=10500.0,
            initial_capital=10000.0,
            total_trades=25,
            win_rate=65.0,
            profit_factor=1.8,
            sharpe_ratio=1.5
        )
    else:
        print("⚠️ Telegram nicht konfiguriert. Setze TELEGRAM_BOT_TOKEN und TELEGRAM_CHAT_ID in .env")
