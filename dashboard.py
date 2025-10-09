"""
dashboard.py - Web Dashboard für Trading Bot
===========================================
Professional web dashboard with interactive charts and live metrics
"""
import os
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, render_template, jsonify, send_from_directory
import pandas as pd
import numpy as np

from config import config
from utils import calculate_performance_metrics, format_currency, format_percentage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trading-bot-secret-key-change-in-production'


class DashboardData:
    """Handler für Dashboard-Daten"""
    
    @staticmethod
    def load_trades() -> List[Dict]:
        """Lade Trade-History aus CSV"""
        trades = []
        trades_file = config.trades_file
        
        if not os.path.exists(trades_file):
            return []
        
        try:
            with open(trades_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trades.append(row)
            return trades
        except Exception as e:
            print(f"Error loading trades: {e}")
            return []
    
    @staticmethod
    def get_performance_metrics() -> Dict:
        """Berechne Performance-Metriken"""
        trades = DashboardData.load_trades()
        
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'profit_factor': 0,
                'current_capital': config.initial_capital
            }
        
        # Konvertiere zu DataFrame für Analyse
        df = pd.DataFrame(trades)
        df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['capital'] = pd.to_numeric(df['capital'], errors='coerce')
        
        # Filter nur SELL orders (die haben P&L)
        sell_trades = df[df['order_type'] == 'SELL'].copy()
        
        if len(sell_trades) == 0:
            current_capital = df['capital'].iloc[-1] if len(df) > 0 else config.initial_capital
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'profit_factor': 0,
                'current_capital': current_capital
            }
        
        # Nutze calculate_performance_metrics aus utils
        metrics = calculate_performance_metrics(sell_trades.to_dict('records'))
        metrics['current_capital'] = df['capital'].iloc[-1] if len(df) > 0 else config.initial_capital
        
        return metrics
    
    @staticmethod
    def get_chart_data() -> Dict:
        """Bereite Daten für Charts auf"""
        trades = DashboardData.load_trades()
        
        if not trades:
            return {
                'equity_curve': {'labels': [], 'data': []},
                'pnl_distribution': {'labels': [], 'data': []},
                'strategy_performance': {'labels': [], 'data': []}
            }
        
        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['capital'] = pd.to_numeric(df['capital'], errors='coerce')
        df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
        
        # Equity Curve
        equity_curve = {
            'labels': df['timestamp'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
            'data': df['capital'].tolist()
        }
        
        # P&L Distribution (nur SELL orders)
        sell_trades = df[df['order_type'] == 'SELL'].copy()
        if len(sell_trades) > 0:
            pnl_distribution = {
                'labels': sell_trades['timestamp'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
                'data': sell_trades['pnl'].tolist()
            }
        else:
            pnl_distribution = {'labels': [], 'data': []}
        
        # Strategy Performance
        strategy_stats = {}
        for _, trade in sell_trades.iterrows():
            strategies = trade.get('triggering_strategies', '')
            if strategies:
                for strategy in strategies.split(','):
                    strategy = strategy.strip()
                    if strategy:
                        if strategy not in strategy_stats:
                            strategy_stats[strategy] = {'pnl': 0, 'count': 0}
                        strategy_stats[strategy]['pnl'] += trade['pnl']
                        strategy_stats[strategy]['count'] += 1
        
        strategy_performance = {
            'labels': list(strategy_stats.keys()),
            'data': [stats['pnl'] for stats in strategy_stats.values()],
            'counts': [stats['count'] for stats in strategy_stats.values()]
        }
        
        return {
            'equity_curve': equity_curve,
            'pnl_distribution': pnl_distribution,
            'strategy_performance': strategy_performance
        }
    
    @staticmethod
    def get_recent_trades(limit: int = 10) -> List[Dict]:
        """Hole die letzten N Trades"""
        trades = DashboardData.load_trades()
        return trades[-limit:] if trades else []
    
    @staticmethod
    def get_bot_config() -> Dict:
        """Hole Bot-Konfiguration"""
        return {
            'trading_symbol': config.trading_symbol,
            'timeframe': config.timeframe,
            'initial_capital': config.initial_capital,
            'trade_size': config.trade_size,
            'active_strategies': config.active_strategies,
            'cooperation_logic': config.cooperation_logic,
            'update_interval': config.update_interval
        }


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Haupt-Dashboard"""
    return render_template('dashboard.html')


@app.route('/api/metrics')
def api_metrics():
    """API Endpoint für Performance-Metriken"""
    metrics = DashboardData.get_performance_metrics()
    return jsonify(metrics)


@app.route('/api/charts')
def api_charts():
    """API Endpoint für Chart-Daten"""
    charts = DashboardData.get_chart_data()
    return jsonify(charts)


@app.route('/api/trades')
def api_trades():
    """API Endpoint für Recent Trades"""
    limit = 20
    trades = DashboardData.get_recent_trades(limit)
    return jsonify(trades)


@app.route('/api/config')
def api_config():
    """API Endpoint für Bot-Konfiguration"""
    bot_config = DashboardData.get_bot_config()
    return jsonify(bot_config)


@app.route('/api/status')
def api_status():
    """API Endpoint für Bot-Status"""
    # Prüfe ob bot läuft (hier vereinfacht - könnte mit PID-File gemacht werden)
    return jsonify({
        'status': 'running',  # oder 'stopped'
        'uptime': '2h 15m',
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


def create_templates_directory():
    """Erstelle templates/ Verzeichnis wenn nicht vorhanden"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    return templates_dir


def create_static_directory():
    """Erstelle static/ Verzeichnis wenn nicht vorhanden"""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    return static_dir


def main():
    """Starte Dashboard Server"""
    print("=" * 70)
    print("🌐 Trading Bot Dashboard wird gestartet...")
    print("=" * 70)
    
    # Erstelle Verzeichnisse
    templates_dir = create_templates_directory()
    static_dir = create_static_directory()
    
    print(f"📁 Templates: {templates_dir}")
    print(f"📁 Static: {static_dir}")
    print()
    print("🚀 Dashboard läuft auf: http://localhost:5000")
    print("📊 Drücke Ctrl+C zum Beenden")
    print("=" * 70)
    
    # Starte Flask Server
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
