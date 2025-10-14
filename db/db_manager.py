"""
Database Manager
================
SQLite database management for trade history and performance metrics.
"""
import os
import sqlite3
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database Manager für Trading Bot
    
    Features:
    - Trade History Persistence
    - Performance Metrics Storage
    - Equity Curve Tracking
    - Strategy Performance Analytics
    - System Logs
    - Alert History
    """
    
    def __init__(self, db_path: str = "data/trading_bot.db"):
        """
        Initialisiere Database Manager
        
        Args:
            db_path: Pfad zur SQLite Datenbank
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        
        # Erstelle Verzeichnis falls nicht vorhanden
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialisiere Datenbank
        self._initialize_database()
        
        logger.info(f"✓ Database Manager initialisiert: {db_path}")
    
    def _initialize_database(self):
        """Initialisiere Datenbank mit Schema"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            
            # Lade und führe Schema aus
            schema_path = Path(__file__).parent / "schema.sql"
            
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                    self.conn.executescript(schema_sql)
                    self.conn.commit()
                logger.info("✓ Database schema initialized")
            else:
                logger.warning(f"Schema file not found: {schema_path}")
                
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def close(self):
        """Schließe Datenbankverbindung"""
        if self.conn:
            self.conn.close()
            logger.info("✓ Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    # ========== TRADE OPERATIONS ==========
    
    def insert_trade(
        self,
        symbol: str,
        order_type: str,
        price: float,
        quantity: float,
        strategies: List[str],
        capital: float,
        pnl: float = 0.0,
        is_real_money: bool = False,
        profit_factor: float = 0.0,
        win_rate: float = 0.0,
        sharpe_ratio: float = 0.0,
        notes: Optional[str] = None
    ) -> int:
        """
        Speichere Trade in Datenbank
        
        Args:
            symbol: Trading Symbol (z.B. BTC/USDT)
            order_type: BUY oder SELL
            price: Ausführungspreis
            quantity: Menge
            strategies: Liste der Strategien
            capital: Aktuelles Kapital
            pnl: Profit/Loss
            is_real_money: Real Money Trading
            profit_factor: Profit Factor
            win_rate: Win Rate
            sharpe_ratio: Sharpe Ratio
            notes: Zusätzliche Notizen
            
        Returns:
            Trade ID
        """
        try:
            strategies_str = ','.join(strategies) if strategies else None
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO trades (
                    symbol, order_type, price, quantity,
                    triggering_strategies, capital, pnl,
                    is_real_money, profit_factor, win_rate, sharpe_ratio, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol, order_type, price, quantity,
                strategies_str, capital, pnl,
                is_real_money, profit_factor, win_rate, sharpe_ratio, notes
            ))
            
            self.conn.commit()
            trade_id = cursor.lastrowid
            
            logger.debug(f"✓ Trade saved: ID={trade_id}, {order_type} {symbol} @ ${price:.2f}")
            return trade_id
            
        except Exception as e:
            logger.error(f"❌ Failed to insert trade: {e}")
            self.conn.rollback()
            raise
    
    def get_trades(
        self,
        limit: int = 100,
        symbol: Optional[str] = None,
        order_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Hole Trades aus Datenbank
        
        Args:
            limit: Maximale Anzahl Trades
            symbol: Filter nach Symbol
            order_type: Filter nach Order Type
            start_date: Start-Datum
            end_date: End-Datum
            
        Returns:
            Liste von Trade-Dictionaries
        """
        try:
            query = "SELECT * FROM trades WHERE 1=1"
            params = []
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            
            if order_type:
                query += " AND order_type = ?"
                params.append(order_type)
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            rows = cursor.fetchall()
            trades = [dict(row) for row in rows]
            
            return trades
            
        except Exception as e:
            logger.error(f"❌ Failed to get trades: {e}")
            return []
    
    def get_trades_df(self, **kwargs) -> pd.DataFrame:
        """
        Hole Trades als Pandas DataFrame
        
        Args:
            **kwargs: Parameter für get_trades()
            
        Returns:
            DataFrame mit Trades
        """
        trades = self.get_trades(**kwargs)
        
        if not trades:
            return pd.DataFrame()
        
        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    # ========== PERFORMANCE METRICS ==========
    
    def insert_performance_metric(
        self,
        capital: float,
        total_pnl: float,
        roi_percent: float,
        total_trades: int,
        winning_trades: int,
        losing_trades: int,
        win_rate: float,
        profit_factor: float,
        sharpe_ratio: float,
        max_drawdown: float,
        avg_trade_duration: Optional[float] = None
    ) -> int:
        """
        Speichere Performance Metric
        
        Returns:
            Metric ID
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO performance_metrics (
                    capital, total_pnl, roi_percent,
                    total_trades, winning_trades, losing_trades,
                    win_rate, profit_factor, sharpe_ratio,
                    max_drawdown, avg_trade_duration_minutes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                capital, total_pnl, roi_percent,
                total_trades, winning_trades, losing_trades,
                win_rate, profit_factor, sharpe_ratio,
                max_drawdown, avg_trade_duration
            ))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"❌ Failed to insert performance metric: {e}")
            self.conn.rollback()
            raise
    
    def get_latest_performance(self) -> Optional[Dict[str, Any]]:
        """
        Hole letzte Performance Metric
        
        Returns:
            Performance Dictionary oder None
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM performance_metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get latest performance: {e}")
            return None
    
    # ========== EQUITY CURVE ==========
    
    def insert_equity_point(self, equity: float, drawdown_percent: float) -> int:
        """
        Speichere Equity Curve Punkt
        
        Args:
            equity: Aktuelles Eigenkapital
            drawdown_percent: Drawdown in Prozent
            
        Returns:
            Point ID
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO equity_curve (equity, drawdown_percent)
                VALUES (?, ?)
            """, (equity, drawdown_percent))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"❌ Failed to insert equity point: {e}")
            self.conn.rollback()
            raise
    
    def get_equity_curve(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Hole Equity Curve
        
        Args:
            limit: Maximale Anzahl Punkte
            
        Returns:
            Liste von Equity Points
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM equity_curve
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ Failed to get equity curve: {e}")
            return []
    
    # ========== STRATEGY PERFORMANCE ==========
    
    def insert_strategy_performance(
        self,
        strategy_name: str,
        total_signals: int,
        winning_signals: int,
        losing_signals: int,
        win_rate: float,
        total_pnl: float,
        avg_pnl_per_trade: float
    ) -> int:
        """
        Speichere Strategy Performance
        
        Returns:
            Performance ID
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO strategy_performance (
                    strategy_name, total_signals, winning_signals, losing_signals,
                    win_rate, total_pnl, avg_pnl_per_trade
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                strategy_name, total_signals, winning_signals, losing_signals,
                win_rate, total_pnl, avg_pnl_per_trade
            ))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"❌ Failed to insert strategy performance: {e}")
            self.conn.rollback()
            raise
    
    # ========== ANALYTICS & REPORTS ==========
    
    def get_daily_performance(self) -> pd.DataFrame:
        """
        Hole Daily Performance Report
        
        Returns:
            DataFrame mit täglicher Performance
        """
        try:
            query = "SELECT * FROM v_daily_performance"
            df = pd.read_sql_query(query, self.conn)
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to get daily performance: {e}")
            return pd.DataFrame()
    
    def get_strategy_summary(self) -> pd.DataFrame:
        """
        Hole Strategy Performance Summary
        
        Returns:
            DataFrame mit Strategy Performance
        """
        try:
            query = "SELECT * FROM v_strategy_summary"
            return pd.read_sql_query(query, self.conn)
            
        except Exception as e:
            logger.error(f"❌ Failed to get strategy summary: {e}")
            return pd.DataFrame()
    
    def get_trade_statistics(self) -> Dict[str, Any]:
        """
        Hole Trade-Statistiken
        
        Returns:
            Dictionary mit Statistiken
        """
        try:
            cursor = self.conn.cursor()
            
            # Gesamt-Statistiken
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                    SUM(pnl) as total_pnl,
                    AVG(pnl) as avg_pnl,
                    MIN(pnl) as worst_trade,
                    MAX(pnl) as best_trade,
                    AVG(capital) as avg_capital
                FROM trades
            """)
            
            row = cursor.fetchone()
            stats = dict(row) if row else {}
            
            # Win Rate berechnen
            if stats.get('total_trades', 0) > 0:
                stats['win_rate'] = (stats.get('winning_trades', 0) / stats['total_trades']) * 100
            else:
                stats['win_rate'] = 0.0
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get trade statistics: {e}")
            return {}
    
    # ========== MIGRATION FROM CSV ==========
    
    def migrate_from_csv(self, csv_path: str) -> int:
        """
        Migriere Trades von CSV zu Database
        
        Args:
            csv_path: Pfad zur CSV-Datei
            
        Returns:
            Anzahl migrierter Trades
        """
        try:
            if not os.path.exists(csv_path):
                logger.warning(f"CSV file not found: {csv_path}")
                return 0
            
            df = pd.read_csv(csv_path)
            count = 0
            
            for _, row in df.iterrows():
                strategies = row.get('triggering_strategies', '').split(',') if pd.notna(row.get('triggering_strategies')) else []
                
                self.insert_trade(
                    symbol=row.get('symbol', 'UNKNOWN'),
                    order_type=row.get('order_type', 'BUY'),
                    price=float(row.get('price', 0)),
                    quantity=float(row.get('quantity', 0)),
                    strategies=strategies,
                    capital=float(row.get('capital', 0)),
                    pnl=float(row.get('pnl', 0)),
                    is_real_money=bool(row.get('is_real_money', False)),
                    profit_factor=float(row.get('profit_factor', 0)),
                    win_rate=float(row.get('win_rate', 0)),
                    sharpe_ratio=float(row.get('sharpe_ratio', 0))
                )
                count += 1
            
            logger.info(f"✓ Migrated {count} trades from CSV")
            return count
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate from CSV: {e}")
            return 0


# Demo
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test Database Manager
    with DatabaseManager("data/test_trading_bot.db") as db:
        # Test Trade Insert
        trade_id = db.insert_trade(
            symbol="BTC/USDT",
            order_type="BUY",
            price=50000.0,
            quantity=0.1,
            strategies=["RSI", "EMA"],
            capital=10000.0
        )
        print(f"✓ Trade inserted: ID={trade_id}")
        
        # Test Get Trades
        trades = db.get_trades(limit=10)
        print(f"✓ Retrieved {len(trades)} trades")
        
        # Test Statistics
        stats = db.get_trade_statistics()
        print(f"✓ Statistics: {stats}")
