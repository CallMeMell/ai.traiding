"""
Email Alert Integration
========================
Sendet Trading-Benachrichtigungen per Email (SMTP).
"""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailAlert:
    """
    Email Alert System für Trading-Benachrichtigungen
    
    Features:
    - Trade Alerts (BUY/SELL)
    - Performance Reports
    - Circuit Breaker Alerts
    - Error Notifications
    - HTML Email Templates
    """
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        to_email: Optional[str] = None,
        enabled: bool = True,
        use_tls: bool = True
    ):
        """
        Initialisiere Email Alert System
        
        Args:
            smtp_host: SMTP Server (z.B. smtp.gmail.com)
            smtp_port: SMTP Port (z.B. 587 für TLS)
            smtp_user: SMTP Benutzername
            smtp_password: SMTP Passwort
            from_email: Absender Email
            to_email: Empfänger Email
            enabled: Aktiviere/Deaktiviere Email Alerts
            use_tls: Verwende TLS/SSL
        """
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.from_email = from_email or os.getenv("EMAIL_FROM", "")
        self.to_email = to_email or os.getenv("EMAIL_TO", "")
        self.use_tls = use_tls
        
        # Validiere Konfiguration
        self.enabled = enabled and all([
            self.smtp_host,
            self.smtp_port,
            self.smtp_user,
            self.smtp_password,
            self.from_email,
            self.to_email
        ])
        
        if not self.enabled:
            if enabled:
                logger.info("⚠️ Email Alerts deaktiviert (fehlende Credentials)")
            else:
                logger.info("⚠️ Email Alerts deaktiviert (enabled=False)")
        else:
            logger.info("✓ Email Alerts aktiviert")
    
    def send_email(
        self,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        priority: str = "normal"
    ) -> bool:
        """
        Sende Email
        
        Args:
            subject: Email Betreff
            body_text: Plain-Text Body
            body_html: HTML Body (optional)
            priority: normal, high, low
            
        Returns:
            True wenn erfolgreich
        """
        if not self.enabled:
            logger.debug("Email deaktiviert - Nachricht nicht gesendet")
            return False
        
        try:
            # Erstelle Email Message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Priorität setzen
            if priority == "high":
                msg['X-Priority'] = '1'
                msg['Importance'] = 'high'
            elif priority == "low":
                msg['X-Priority'] = '5'
                msg['Importance'] = 'low'
            
            # Plain-Text Part
            part1 = MIMEText(body_text, 'plain', 'utf-8')
            msg.attach(part1)
            
            # HTML Part (optional)
            if body_html:
                part2 = MIMEText(body_html, 'html', 'utf-8')
                msg.attach(part2)
            
            # Verbinde zu SMTP Server
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.debug("✓ Email gesendet")
            return True
            
        except Exception as e:
            logger.error(f"❌ Email Fehler: {e}")
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
            symbol: Trading-Symbol
            price: Ausführungspreis
            quantity: Menge
            strategies: Liste ausgelöster Strategien
            capital: Aktuelles Kapital
            pnl: Profit/Loss
            
        Returns:
            True wenn erfolgreich
        """
        emoji = "📈" if order_type == "BUY" else "📉"
        subject = f"{emoji} Trading Alert: {order_type} {symbol}"
        
        strategies_str = ", ".join(strategies) if strategies else "N/A"
        
        # Plain Text
        body_text = f"""
{order_type} Signal - {symbol}

Preis: ${price:,.2f}
Menge: {quantity:.6f}
Strategien: {strategies_str}
Kapital: ${capital:,.2f}
"""
        
        if pnl != 0:
            body_text += f"P&L: ${pnl:+,.2f} ({pnl/capital*100:+.2f}%)\n"
        
        body_text += f"\nZeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # HTML
        pnl_color = "#2ecc71" if pnl >= 0 else "#e74c3c"
        body_html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: {'#2ecc71' if order_type == 'BUY' else '#e74c3c'}; 
                   color: white; padding: 20px; border-radius: 5px; }}
        .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; border-radius: 5px; }}
        .metric {{ margin: 10px 0; }}
        .label {{ font-weight: bold; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #777; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{emoji} {order_type} Signal</h2>
            <h3>{symbol}</h3>
        </div>
        <div class="content">
            <div class="metric">
                <span class="label">Preis:</span> ${price:,.2f}
            </div>
            <div class="metric">
                <span class="label">Menge:</span> {quantity:.6f}
            </div>
            <div class="metric">
                <span class="label">Strategien:</span> {strategies_str}
            </div>
            <div class="metric">
                <span class="label">Kapital:</span> ${capital:,.2f}
            </div>
"""
        
        if pnl != 0:
            body_html += f"""
            <div class="metric">
                <span class="label">P&L:</span> 
                <span style="color: {pnl_color}; font-weight: bold;">
                    ${pnl:+,.2f} ({pnl/capital*100:+.2f}%)
                </span>
            </div>
"""
        
        body_html += f"""
        </div>
        <div class="footer">
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(subject, body_text, body_html, priority="high")
    
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
        subject = "🚨 CIRCUIT BREAKER AUSGELÖST - Trading gestoppt!"
        
        loss = initial_capital - capital
        loss_pct = (loss / initial_capital) * 100
        
        body_text = f"""
⚠️ CIRCUIT BREAKER ALARM ⚠️

Trading wurde automatisch gestoppt!

Drawdown: {drawdown:.2f}% (Limit: {limit:.2f}%)
Verlust: ${loss:,.2f} ({loss_pct:.2f}%)
Verbleibendes Kapital: ${capital:,.2f}
Start-Kapital: ${initial_capital:,.2f}

Bitte System überprüfen!

Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        body_html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .alert {{ background-color: #e74c3c; color: white; padding: 20px; 
                  border-radius: 5px; text-align: center; }}
        .content {{ background-color: #fff5f5; padding: 20px; margin-top: 20px; 
                    border-radius: 5px; border: 2px solid #e74c3c; }}
        .metric {{ margin: 15px 0; font-size: 16px; }}
        .label {{ font-weight: bold; }}
        .warning {{ background-color: #fff3cd; padding: 15px; margin-top: 20px; 
                    border-radius: 5px; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="alert">
            <h1>🚨 CIRCUIT BREAKER AUSGELÖST</h1>
            <p>Trading wurde automatisch gestoppt!</p>
        </div>
        <div class="content">
            <div class="metric">
                <span class="label">Drawdown:</span> {drawdown:.2f}% 
                (Limit: {limit:.2f}%)
            </div>
            <div class="metric">
                <span class="label">Verlust:</span> 
                <span style="color: #e74c3c; font-weight: bold;">
                    ${loss:,.2f} ({loss_pct:.2f}%)
                </span>
            </div>
            <div class="metric">
                <span class="label">Verbleibendes Kapital:</span> ${capital:,.2f}
            </div>
            <div class="metric">
                <span class="label">Start-Kapital:</span> ${initial_capital:,.2f}
            </div>
        </div>
        <div class="warning">
            <strong>⚠️ Aktion erforderlich:</strong><br>
            Bitte überprüfen Sie das Trading-System und die Strategie-Performance!
        </div>
        <div style="margin-top: 20px; font-size: 12px; color: #777;">
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(subject, body_text, body_html, priority="high")
    
    def send_performance_report(
        self,
        capital: float,
        initial_capital: float,
        total_trades: int,
        win_rate: float,
        profit_factor: float,
        sharpe_ratio: float
    ) -> bool:
        """
        Sende Performance Report
        
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
        subject = f"📊 Performance Report - ROI: {roi:+.2f}%"
        
        body_text = f"""
Performance Report

ROI: {roi:+.2f}%
Kapital: ${capital:,.2f} (Start: ${initial_capital:,.2f})
Trades: {total_trades}
Win Rate: {win_rate:.1f}%
Profit Factor: {profit_factor:.2f}
Sharpe Ratio: {sharpe_ratio:.2f}

Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        roi_color = "#2ecc71" if roi >= 0 else "#e74c3c"
        body_html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #3498db; color: white; padding: 20px; border-radius: 5px; }}
        .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; border-radius: 5px; }}
        .metric {{ margin: 15px 0; font-size: 16px; }}
        .label {{ font-weight: bold; color: #555; }}
        .value {{ float: right; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📊 Performance Report</h2>
        </div>
        <div class="content">
            <div class="metric">
                <span class="label">ROI:</span>
                <span class="value" style="color: {roi_color}; font-weight: bold;">
                    {roi:+.2f}%
                </span>
            </div>
            <div class="metric">
                <span class="label">Aktuelles Kapital:</span>
                <span class="value">${capital:,.2f}</span>
            </div>
            <div class="metric">
                <span class="label">Start-Kapital:</span>
                <span class="value">${initial_capital:,.2f}</span>
            </div>
            <div class="metric">
                <span class="label">Anzahl Trades:</span>
                <span class="value">{total_trades}</span>
            </div>
            <div class="metric">
                <span class="label">Win Rate:</span>
                <span class="value">{win_rate:.1f}%</span>
            </div>
            <div class="metric">
                <span class="label">Profit Factor:</span>
                <span class="value">{profit_factor:.2f}</span>
            </div>
            <div class="metric">
                <span class="label">Sharpe Ratio:</span>
                <span class="value">{sharpe_ratio:.2f}</span>
            </div>
        </div>
        <div style="margin-top: 20px; font-size: 12px; color: #777;">
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(subject, body_text, body_html, priority="normal")


# Demo
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test Email Alert
    email = EmailAlert()
    
    if email.enabled:
        # Test Trade Alert
        email.send_trade_alert(
            order_type="BUY",
            symbol="BTC/USDT",
            price=50000.0,
            quantity=0.1,
            strategies=["RSI", "EMA Crossover"],
            capital=10500.0,
            pnl=500.0
        )
    else:
        print("⚠️ Email nicht konfiguriert. Setze SMTP Credentials in .env")
