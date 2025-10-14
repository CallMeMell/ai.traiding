-- Database Schema for Trading Bot
-- SQLite compatible schema for trade history and performance metrics

-- Trades Table
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    symbol VARCHAR(20) NOT NULL,
    order_type VARCHAR(10) NOT NULL CHECK(order_type IN ('BUY', 'SELL')),
    price DECIMAL(18, 8) NOT NULL,
    quantity DECIMAL(18, 8) NOT NULL,
    total_value DECIMAL(18, 8) GENERATED ALWAYS AS (price * quantity) STORED,
    triggering_strategies TEXT,
    capital DECIMAL(18, 8) NOT NULL,
    pnl DECIMAL(18, 8) DEFAULT 0.0,
    is_real_money BOOLEAN DEFAULT 0,
    profit_factor DECIMAL(10, 4) DEFAULT 0.0,
    win_rate DECIMAL(10, 4) DEFAULT 0.0,
    sharpe_ratio DECIMAL(10, 4) DEFAULT 0.0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Performance Metrics Table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    capital DECIMAL(18, 8) NOT NULL,
    total_pnl DECIMAL(18, 8) NOT NULL,
    roi_percent DECIMAL(10, 4) NOT NULL,
    total_trades INTEGER NOT NULL,
    winning_trades INTEGER NOT NULL,
    losing_trades INTEGER NOT NULL,
    win_rate DECIMAL(10, 4) NOT NULL,
    profit_factor DECIMAL(10, 4) NOT NULL,
    sharpe_ratio DECIMAL(10, 4) NOT NULL,
    max_drawdown DECIMAL(10, 4) NOT NULL,
    avg_trade_duration_minutes DECIMAL(10, 2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Equity Curve Table
CREATE TABLE IF NOT EXISTS equity_curve (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    equity DECIMAL(18, 8) NOT NULL,
    drawdown_percent DECIMAL(10, 4) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Strategy Performance Table
CREATE TABLE IF NOT EXISTS strategy_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_name VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_signals INTEGER NOT NULL,
    winning_signals INTEGER NOT NULL,
    losing_signals INTEGER NOT NULL,
    win_rate DECIMAL(10, 4) NOT NULL,
    total_pnl DECIMAL(18, 8) NOT NULL,
    avg_pnl_per_trade DECIMAL(18, 8) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- System Logs Table
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    log_level VARCHAR(10) NOT NULL CHECK(log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    module VARCHAR(50),
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Alerts History Table
CREATE TABLE IF NOT EXISTS alerts_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    alert_type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL CHECK(channel IN ('telegram', 'email', 'discord')),
    success BOOLEAN NOT NULL,
    message TEXT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_order_type ON trades(order_type);
CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_equity_timestamp ON equity_curve(timestamp);
CREATE INDEX IF NOT EXISTS idx_strategy_performance_name ON strategy_performance(strategy_name);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_channel ON alerts_history(channel);

-- Views for common queries

-- Recent Trades View
CREATE VIEW IF NOT EXISTS v_recent_trades AS
SELECT 
    id,
    timestamp,
    symbol,
    order_type,
    price,
    quantity,
    total_value,
    pnl,
    capital,
    triggering_strategies
FROM trades
ORDER BY timestamp DESC
LIMIT 100;

-- Daily Performance View
CREATE VIEW IF NOT EXISTS v_daily_performance AS
SELECT 
    DATE(timestamp) as trade_date,
    COUNT(*) as total_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
    SUM(pnl) as daily_pnl,
    AVG(pnl) as avg_pnl_per_trade,
    MIN(capital) as min_capital,
    MAX(capital) as max_capital
FROM trades
GROUP BY DATE(timestamp)
ORDER BY trade_date DESC;

-- Strategy Performance Summary View
CREATE VIEW IF NOT EXISTS v_strategy_summary AS
SELECT 
    triggering_strategies as strategy_name,
    COUNT(*) as total_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
    CAST(SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as win_rate,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl_per_trade,
    MIN(pnl) as worst_trade,
    MAX(pnl) as best_trade
FROM trades
WHERE triggering_strategies IS NOT NULL
GROUP BY triggering_strategies
ORDER BY total_pnl DESC;
