"""
Tests für Alert System (Telegram & Email)
==========================================
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from alerts.telegram_alert import TelegramAlert
from alerts.email_alert import EmailAlert
from alerts.alert_manager import AlertManager


class TestTelegramAlert:
    """Tests für Telegram Alert Integration"""
    
    def test_init_without_credentials(self):
        """Test Initialisierung ohne Credentials"""
        with patch.dict(os.environ, {}, clear=True):
            bot = TelegramAlert()
            assert not bot.enabled
            assert bot.bot_token == ""
            assert bot.chat_id == ""
    
    def test_init_with_credentials(self):
        """Test Initialisierung mit Credentials"""
        bot = TelegramAlert(
            bot_token="test_token",
            chat_id="test_chat_id",
            enabled=True
        )
        assert bot.bot_token == "test_token"
        assert bot.chat_id == "test_chat_id"
        # enabled wird False wenn Verbindung fehlschlägt
    
    def test_send_message_when_disabled(self):
        """Test dass keine Nachricht gesendet wird wenn deaktiviert"""
        bot = TelegramAlert(enabled=False)
        result = bot.send_message("Test message")
        assert result is False
    
    @patch('alerts.telegram_alert.requests.post')
    def test_send_message_success(self, mock_post):
        """Test erfolgreiche Nachricht"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Create bot with mocked verification
        with patch.object(TelegramAlert, '_verify_connection', return_value=True):
            bot = TelegramAlert(
                bot_token="test_token",
                chat_id="test_chat_id",
                enabled=True
            )
            bot.enabled = True  # Force enable for test
            
            result = bot.send_message("Test message")
            assert result is True
            assert mock_post.called
    
    @patch('alerts.telegram_alert.requests.post')
    def test_send_trade_alert(self, mock_post):
        """Test Trade Alert"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with patch.object(TelegramAlert, '_verify_connection', return_value=True):
            bot = TelegramAlert(
                bot_token="test_token",
                chat_id="test_chat_id",
                enabled=True
            )
            bot.enabled = True
            
            result = bot.send_trade_alert(
                order_type="BUY",
                symbol="BTC/USDT",
                price=50000.0,
                quantity=0.1,
                strategies=["RSI", "EMA"],
                capital=10000.0
            )
            assert result is True
    
    @patch('alerts.telegram_alert.requests.post')
    def test_send_circuit_breaker_alert(self, mock_post):
        """Test Circuit Breaker Alert"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with patch.object(TelegramAlert, '_verify_connection', return_value=True):
            bot = TelegramAlert(
                bot_token="test_token",
                chat_id="test_chat_id",
                enabled=True
            )
            bot.enabled = True
            
            result = bot.send_circuit_breaker_alert(
                drawdown=-25.0,
                limit=20.0,
                capital=7500.0,
                initial_capital=10000.0
            )
            assert result is True
    
    @patch('alerts.telegram_alert.requests.post')
    def test_send_performance_update(self, mock_post):
        """Test Performance Update"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with patch.object(TelegramAlert, '_verify_connection', return_value=True):
            bot = TelegramAlert(
                bot_token="test_token",
                chat_id="test_chat_id",
                enabled=True
            )
            bot.enabled = True
            
            result = bot.send_performance_update(
                capital=10500.0,
                initial_capital=10000.0,
                total_trades=25,
                win_rate=65.0,
                profit_factor=1.8,
                sharpe_ratio=1.5
            )
            assert result is True


class TestEmailAlert:
    """Tests für Email Alert Integration"""
    
    def test_init_without_credentials(self):
        """Test Initialisierung ohne Credentials"""
        with patch.dict(os.environ, {}, clear=True):
            email = EmailAlert()
            assert not email.enabled
    
    def test_init_with_credentials(self):
        """Test Initialisierung mit Credentials"""
        email = EmailAlert(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="test@example.com",
            smtp_password="password",
            from_email="test@example.com",
            to_email="recipient@example.com",
            enabled=True
        )
        assert email.smtp_host == "smtp.gmail.com"
        assert email.enabled is True
    
    def test_send_email_when_disabled(self):
        """Test dass keine Email gesendet wird wenn deaktiviert"""
        email = EmailAlert(enabled=False)
        result = email.send_email("Test", "Test message")
        assert result is False
    
    @patch('alerts.email_alert.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test erfolgreiche Email"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email = EmailAlert(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="test@example.com",
            smtp_password="password",
            from_email="test@example.com",
            to_email="recipient@example.com",
            enabled=True
        )
        
        result = email.send_email("Test Subject", "Test Body")
        assert result is True
        assert mock_server.login.called
        assert mock_server.send_message.called
    
    @patch('alerts.email_alert.smtplib.SMTP')
    def test_send_trade_alert(self, mock_smtp):
        """Test Trade Alert Email"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email = EmailAlert(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="test@example.com",
            smtp_password="password",
            from_email="test@example.com",
            to_email="recipient@example.com",
            enabled=True
        )
        
        result = email.send_trade_alert(
            order_type="BUY",
            symbol="BTC/USDT",
            price=50000.0,
            quantity=0.1,
            strategies=["RSI", "EMA"],
            capital=10000.0
        )
        assert result is True
    
    @patch('alerts.email_alert.smtplib.SMTP')
    def test_send_circuit_breaker_alert(self, mock_smtp):
        """Test Circuit Breaker Alert Email"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email = EmailAlert(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="test@example.com",
            smtp_password="password",
            from_email="test@example.com",
            to_email="recipient@example.com",
            enabled=True
        )
        
        result = email.send_circuit_breaker_alert(
            drawdown=-25.0,
            limit=20.0,
            capital=7500.0,
            initial_capital=10000.0
        )
        assert result is True


class TestAlertManager:
    """Tests für Alert Manager"""
    
    def test_init_default(self):
        """Test Standard-Initialisierung"""
        with patch.dict(os.environ, {}, clear=True):
            manager = AlertManager()
            assert not manager.telegram.enabled
            assert not manager.email.enabled
    
    def test_init_with_config(self):
        """Test Initialisierung mit Konfiguration"""
        with patch.object(TelegramAlert, '_verify_connection', return_value=True):
            manager = AlertManager(
                enable_telegram=True,
                telegram_bot_token="test_token",
                telegram_chat_id="test_chat",
                enable_email=True,
                smtp_config={
                    'host': 'smtp.gmail.com',
                    'port': 587,
                    'user': 'test@example.com',
                    'password': 'password',
                    'from_email': 'test@example.com',
                    'to_email': 'recipient@example.com'
                }
            )
            assert manager.telegram.bot_token == "test_token"
            assert manager.email.smtp_host == "smtp.gmail.com"
    
    @patch('alerts.telegram_alert.requests.post')
    @patch('alerts.email_alert.smtplib.SMTP')
    def test_send_trade_alert(self, mock_smtp, mock_post):
        """Test Trade Alert über alle Kanäle"""
        # Mock Telegram
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Mock Email
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        with patch.object(TelegramAlert, '_verify_connection', return_value=True):
            manager = AlertManager(
                enable_telegram=True,
                telegram_bot_token="test_token",
                telegram_chat_id="test_chat",
                enable_email=True,
                smtp_config={
                    'host': 'smtp.gmail.com',
                    'port': 587,
                    'user': 'test@example.com',
                    'password': 'password',
                    'from_email': 'test@example.com',
                    'to_email': 'recipient@example.com'
                }
            )
            # Force enable for test
            manager.telegram.enabled = True
            manager.email.enabled = True
            
            results = manager.send_trade_alert(
                order_type="BUY",
                symbol="BTC/USDT",
                price=50000.0,
                quantity=0.1,
                strategies=["RSI", "EMA"],
                capital=10000.0
            )
            
            assert 'telegram' in results
            assert 'email' in results
    
    def test_get_statistics(self):
        """Test Statistik-Funktion"""
        manager = AlertManager()
        stats = manager.get_statistics()
        
        assert 'total_alerts' in stats
        assert 'telegram_sent' in stats
        assert 'email_sent' in stats
    
    def test_is_any_channel_active(self):
        """Test ob mindestens ein Kanal aktiv"""
        with patch.dict(os.environ, {}, clear=True):
            manager = AlertManager(enable_telegram=False, enable_email=False)
            assert not manager.is_any_channel_active()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
