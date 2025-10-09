"""
alert_system.py - Comprehensive Alerting and Notification System
=================================================================
Real-time alerts for critical trading events:
- Trading signals
- Loss thresholds
- System errors
- Performance metrics
- Market conditions

Supports multiple notification channels:
- Console/Logging
- Email
- Webhooks (Slack, Discord, etc.)
- File-based alerts
"""
import os
import json
import logging
import smtplib
import requests
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AlertType(Enum):
    """Types of alerts"""
    TRADE_SIGNAL = "TRADE_SIGNAL"
    TRADE_EXECUTED = "TRADE_EXECUTED"
    LOSS_THRESHOLD = "LOSS_THRESHOLD"
    PROFIT_TARGET = "PROFIT_TARGET"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    API_ERROR = "API_ERROR"
    CONNECTION_LOST = "CONNECTION_LOST"
    DAILY_SUMMARY = "DAILY_SUMMARY"
    RISK_LIMIT = "RISK_LIMIT"
    PERFORMANCE_ALERT = "PERFORMANCE_ALERT"


@dataclass
class Alert:
    """Alert data structure"""
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            "type": self.alert_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }
    
    def to_json(self) -> str:
        """Convert alert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class AlertChannel:
    """Base class for alert channels"""
    
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
    
    def send(self, alert: Alert) -> bool:
        """Send alert through this channel"""
        raise NotImplementedError


class ConsoleAlertChannel(AlertChannel):
    """Console/logging alert channel"""
    
    def __init__(self, enabled: bool = True):
        super().__init__("console", enabled)
    
    def send(self, alert: Alert) -> bool:
        """Send alert to console"""
        if not self.enabled:
            return False
        
        # Color codes for severity
        colors = {
            AlertSeverity.INFO: "\033[94m",      # Blue
            AlertSeverity.WARNING: "\033[93m",   # Yellow
            AlertSeverity.ERROR: "\033[91m",     # Red
            AlertSeverity.CRITICAL: "\033[95m"   # Magenta
        }
        reset = "\033[0m"
        
        color = colors.get(alert.severity, "")
        
        # Icon for alert type
        icons = {
            AlertType.TRADE_SIGNAL: "📊",
            AlertType.TRADE_EXECUTED: "✅",
            AlertType.LOSS_THRESHOLD: "⚠️",
            AlertType.PROFIT_TARGET: "🎯",
            AlertType.SYSTEM_ERROR: "❌",
            AlertType.API_ERROR: "🔌",
            AlertType.CONNECTION_LOST: "📡",
            AlertType.DAILY_SUMMARY: "📈",
            AlertType.RISK_LIMIT: "🛑",
            AlertType.PERFORMANCE_ALERT: "📊"
        }
        icon = icons.get(alert.alert_type, "📢")
        
        message = f"{color}{icon} [{alert.severity.value}] {alert.title}{reset}\n  {alert.message}"
        
        # Log based on severity
        if alert.severity == AlertSeverity.CRITICAL:
            logger.critical(message)
        elif alert.severity == AlertSeverity.ERROR:
            logger.error(message)
        elif alert.severity == AlertSeverity.WARNING:
            logger.warning(message)
        else:
            logger.info(message)
        
        return True


class FileAlertChannel(AlertChannel):
    """File-based alert channel"""
    
    def __init__(self, filepath: str = "logs/alerts.log", enabled: bool = True):
        super().__init__("file", enabled)
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    def send(self, alert: Alert) -> bool:
        """Send alert to file"""
        if not self.enabled:
            return False
        
        try:
            with open(self.filepath, 'a', encoding='utf-8') as f:
                f.write(f"{alert.timestamp.isoformat()} | {alert.severity.value} | "
                       f"{alert.alert_type.value} | {alert.title}\n")
                f.write(f"  {alert.message}\n")
                if alert.data:
                    f.write(f"  Data: {json.dumps(alert.data)}\n")
                f.write("-" * 80 + "\n")
            return True
        except Exception as e:
            logger.error(f"Failed to write alert to file: {e}")
            return False


class EmailAlertChannel(AlertChannel):
    """Email alert channel"""
    
    def __init__(self, smtp_config: Dict[str, Any], enabled: bool = False):
        super().__init__("email", enabled)
        self.smtp_config = smtp_config
        self.required_keys = ['smtp_server', 'smtp_port', 'username', 'password', 'to_address']
    
    def send(self, alert: Alert) -> bool:
        """Send alert via email"""
        if not self.enabled:
            return False
        
        # Validate config
        for key in self.required_keys:
            if key not in self.smtp_config:
                logger.error(f"Email config missing key: {key}")
                return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = self.smtp_config['to_address']
            msg['Subject'] = f"[{alert.severity.value}] {alert.title}"
            
            body = f"""
Trading System Alert

Type: {alert.alert_type.value}
Severity: {alert.severity.value}
Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{alert.message}

Additional Data:
{json.dumps(alert.data, indent=2)}
"""
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_config['smtp_server'], 
                            self.smtp_config['smtp_port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], 
                           self.smtp_config['password'])
                server.send_message(msg)
            
            logger.info(f"Alert email sent to {self.smtp_config['to_address']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False


class WebhookAlertChannel(AlertChannel):
    """Webhook alert channel (Slack, Discord, etc.)"""
    
    def __init__(self, webhook_url: str, webhook_type: str = "generic", enabled: bool = False):
        super().__init__("webhook", enabled)
        self.webhook_url = webhook_url
        self.webhook_type = webhook_type  # 'slack', 'discord', 'generic'
    
    def send(self, alert: Alert) -> bool:
        """Send alert via webhook"""
        if not self.enabled or not self.webhook_url:
            return False
        
        try:
            # Format message based on webhook type
            if self.webhook_type == 'slack':
                payload = self._format_slack(alert)
            elif self.webhook_type == 'discord':
                payload = self._format_discord(alert)
            else:
                payload = alert.to_dict()
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Alert sent to {self.webhook_type} webhook")
                return True
            else:
                logger.error(f"Webhook returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False
    
    def _format_slack(self, alert: Alert) -> Dict[str, Any]:
        """Format alert for Slack"""
        color_map = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9900",
            AlertSeverity.ERROR: "#ff0000",
            AlertSeverity.CRITICAL: "#990000"
        }
        
        return {
            "attachments": [{
                "color": color_map.get(alert.severity, "#36a64f"),
                "title": alert.title,
                "text": alert.message,
                "fields": [
                    {"title": "Type", "value": alert.alert_type.value, "short": True},
                    {"title": "Severity", "value": alert.severity.value, "short": True}
                ],
                "footer": "Trading System",
                "ts": int(alert.timestamp.timestamp())
            }]
        }
    
    def _format_discord(self, alert: Alert) -> Dict[str, Any]:
        """Format alert for Discord"""
        color_map = {
            AlertSeverity.INFO: 3447003,      # Blue
            AlertSeverity.WARNING: 16776960,  # Yellow
            AlertSeverity.ERROR: 15158332,    # Red
            AlertSeverity.CRITICAL: 10038562  # Dark red
        }
        
        return {
            "embeds": [{
                "title": alert.title,
                "description": alert.message,
                "color": color_map.get(alert.severity, 3447003),
                "fields": [
                    {"name": "Type", "value": alert.alert_type.value, "inline": True},
                    {"name": "Severity", "value": alert.severity.value, "inline": True}
                ],
                "timestamp": alert.timestamp.isoformat()
            }]
        }


class CallbackAlertChannel(AlertChannel):
    """Custom callback alert channel"""
    
    def __init__(self, callback: Callable[[Alert], bool], name: str = "callback", 
                 enabled: bool = True):
        super().__init__(name, enabled)
        self.callback = callback
    
    def send(self, alert: Alert) -> bool:
        """Send alert via callback"""
        if not self.enabled:
            return False
        
        try:
            return self.callback(alert)
        except Exception as e:
            logger.error(f"Callback alert failed: {e}")
            return False


class AlertSystem:
    """
    Comprehensive alerting system for trading platform
    """
    
    def __init__(self):
        """Initialize alert system"""
        self.channels: List[AlertChannel] = []
        self.alert_history: List[Alert] = []
        self.max_history = 1000  # Keep last 1000 alerts
        
        # Default channels
        self.add_channel(ConsoleAlertChannel(enabled=True))
        self.add_channel(FileAlertChannel(enabled=True))
        
        logger.info("✓ Alert System initialized")
    
    def add_channel(self, channel: AlertChannel):
        """Add alert channel"""
        self.channels.append(channel)
        logger.info(f"✓ Added alert channel: {channel.name}")
    
    def remove_channel(self, channel_name: str):
        """Remove alert channel by name"""
        self.channels = [ch for ch in self.channels if ch.name != channel_name]
    
    def configure_email(self, smtp_config: Dict[str, Any]):
        """Configure email alerts"""
        email_channel = EmailAlertChannel(smtp_config, enabled=True)
        self.add_channel(email_channel)
    
    def configure_webhook(self, webhook_url: str, webhook_type: str = "generic"):
        """Configure webhook alerts"""
        webhook_channel = WebhookAlertChannel(webhook_url, webhook_type, enabled=True)
        self.add_channel(webhook_channel)
    
    def add_callback(self, callback: Callable[[Alert], bool], name: str = "callback"):
        """Add custom callback alert handler"""
        callback_channel = CallbackAlertChannel(callback, name, enabled=True)
        self.add_channel(callback_channel)
    
    def send_alert(self, alert: Alert):
        """
        Send alert through all enabled channels
        
        Args:
            alert: Alert to send
        """
        # Add to history
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)
        
        # Send through all channels
        for channel in self.channels:
            if channel.enabled:
                try:
                    channel.send(alert)
                except Exception as e:
                    logger.error(f"Failed to send alert through {channel.name}: {e}")
    
    def alert(self, alert_type: AlertType, severity: AlertSeverity, 
             title: str, message: str, data: Optional[Dict[str, Any]] = None):
        """
        Create and send alert
        
        Args:
            alert_type: Type of alert
            severity: Alert severity
            title: Alert title
            message: Alert message
            data: Additional data
        """
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            data=data or {}
        )
        self.send_alert(alert)
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get recent alert history"""
        return self.alert_history[-limit:]
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total = len(self.alert_history)
        if total == 0:
            return {"total": 0}
        
        by_type = {}
        by_severity = {}
        
        for alert in self.alert_history:
            # Count by type
            alert_type = alert.alert_type.value
            by_type[alert_type] = by_type.get(alert_type, 0) + 1
            
            # Count by severity
            severity = alert.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total": total,
            "by_type": by_type,
            "by_severity": by_severity,
            "channels": [{"name": ch.name, "enabled": ch.enabled} 
                        for ch in self.channels]
        }


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize alert system
    alerts = AlertSystem()
    
    # Test different alert types
    print("\n=== Testing Alert System ===\n")
    
    # Trade signal
    alerts.alert(
        AlertType.TRADE_SIGNAL,
        AlertSeverity.INFO,
        "Buy Signal Detected",
        "RSI and EMA strategies both indicate BUY for BTC/USDT at $50,234.50",
        data={"symbol": "BTC/USDT", "price": 50234.50, "strategies": ["RSI", "EMA"]}
    )
    
    # Loss threshold
    alerts.alert(
        AlertType.LOSS_THRESHOLD,
        AlertSeverity.WARNING,
        "Daily Loss Threshold Approaching",
        "Current daily loss: -3.8%. Threshold: -5%",
        data={"current_loss": -3.8, "threshold": -5.0}
    )
    
    # System error
    alerts.alert(
        AlertType.SYSTEM_ERROR,
        AlertSeverity.CRITICAL,
        "API Connection Failed",
        "Unable to connect to Binance API. Retrying...",
        data={"error": "ConnectionTimeout", "retry_count": 3}
    )
    
    # Print stats
    print("\n=== Alert Statistics ===")
    print(json.dumps(alerts.get_alert_stats(), indent=2))
