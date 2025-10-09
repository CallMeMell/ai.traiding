# 📊 View Session Feature Guide

## Overview

The **View Session** feature provides a comprehensive interface for viewing, analyzing, and managing trading sessions. It allows users to review past trading activity, analyze performance metrics, and export session data for further analysis.

## ✨ Universal Accessibility (NEW)

The View Session feature is now universally accessible from anywhere in the application:

- **Global Header Button**: A prominent "View Sessions" button is always visible in the header, regardless of which view or modal is currently open
- **Quick Access in Modals**: Every modal (Strategies, Trade History, Settings, Broker Connection) includes a "View Sessions" quick access button in its header
- **Seamless Navigation**: Switch to View Sessions from any view without having to close modals or navigate back to the dashboard

This ensures that you can always access your trading session history with a single click, no matter where you are in the application.

## Features

### 📋 Session List View

- **Session Cards**: Each session is displayed as a card showing:
  - Session ID (timestamp-based)
  - Session start time
  - Initial and final capital
  - Total P&L (with color coding: green for profit, red for loss)
  - Total number of trades
  - Win rate percentage

- **Advanced Search and Filter**:
  - Real-time search by session ID or timestamp
  - Filter sessions by performance (All, Profitable Only, Loss Only)
  - **NEW**: Date range filter (From Date / To Date)
  - **NEW**: Clear Filters button to reset all filters
  - Automatic refresh when filters change

### 📈 Session Detail View

Click "View Details" on any session to see:

- **Performance Metrics**:
  - Initial Capital
  - Final Equity
  - Total P&L
  - Total Trades

- **Interactive Trade Filters** (NEW):
  - Filter by Trade Type (All, Buy Orders, Sell Orders)
  - Filter by Status (All, Filled, Partial, Cancelled)
  - Filter by Symbol (All, or specific trading pairs)
  - Real-time filtering of execution history table

- **Enhanced Interactive Charts** (NEW):
  - **Cumulative P&L Over Time**: Line chart showing profit/loss progression
  - **Win/Loss Distribution**: Bar chart showing winning vs losing trades
  - **Trade Types Distribution**: Doughnut chart showing BUY/SELL ratio
  - **Execution Prices Timeline**: Line chart visualizing execution prices
  - All charts built with Chart.js for smooth, responsive interaction

- **Execution History Table**:
  - Complete list of all orders executed in the session
  - Order details: ID, Symbol, Side (BUY/SELL), Quantity, Price, Status
  - Color-coded buy/sell indicators
  - Dynamic filtering based on selected filters

### 💾 Export Functionality

- Export session data to CSV format
- Includes all trade details
- One-click download

## How to Use

### Accessing View Sessions

1. Open the Trading Bot Dashboard
2. Click the **"View Sessions"** button in the navigation menu
3. The session list will load automatically

### Viewing Session Details

1. In the session list, find the session you want to analyze
2. Click the **"View Details"** button
3. A modal will open showing detailed information and charts
4. Close the modal by clicking the X button or pressing Escape

### Filtering Sessions

- **Search**: Type in the search box to filter by session ID or timestamp
- **Performance Filter**: Use the dropdown to show only profitable or loss-making sessions
- **Date Range Filter** (NEW): Select start and end dates to filter sessions by time period
- **Clear Filters** (NEW): Click to reset all filters and show all sessions
- **Refresh**: Click the refresh button to reload the session list

### Filtering Trades in Session Details (NEW)

Once you've opened a session detail view, you can filter the execution history:

1. **Filter by Trade Type**: Select "Buy Orders" or "Sell Orders" to show only specific order types
2. **Filter by Status**: Choose "Filled", "Partial", or "Cancelled" to view orders by execution status
3. **Filter by Symbol**: Select a specific trading pair (e.g., BTCUSDT, ADAUSDT) to view only trades for that symbol
4. Filters can be combined for more specific results
5. The table updates instantly as you change filters

### Exporting Session Data

1. In the session list, click the **"Export"** button for the desired session
2. A CSV file will be downloaded automatically
3. Open in Excel, Google Sheets, or any CSV-compatible application

## Backend API

### Endpoints

#### List All Sessions
```
GET /api/sessions
```

**Response**:
```json
[
  {
    "id": "20240101_120000",
    "filename": "simulated_trading_session_20240101_120000.log",
    "timestamp": "2024-01-01 12:00:00",
    "initial_capital": 10000.0,
    "final_equity": 10234.5,
    "total_pnl": 234.5,
    "total_trades": 15,
    "win_rate": 0.57,
    "status": "completed"
  }
]
```

#### Get Session Details
```
GET /api/sessions/<session_id>
```

**Response**:
```json
{
  "id": "20240101_120000",
  "timestamp": "2024-01-01 12:00:00",
  "metrics": {
    "total_orders": "15",
    "filled_orders": "14",
    "win_rate": "0.57",
    ...
  },
  "trades": [
    {
      "order_id": "SIM_1_1704110400000",
      "symbol": "BTCUSDT",
      "side": "BUY",
      "quantity": "0.1/0.1",
      "execution_price": "$50000.00",
      "status": "FILLED"
    }
  ]
}
```

## Session Log Format

Session logs are stored in the `logs/` directory with the naming convention:
```
simulated_trading_session_YYYYMMDD_HHMMSS.log
```

### Log Structure

1. **Header Section**: Session start/end times, capital information
2. **Performance Metrics**: Comprehensive trading metrics
3. **Execution History**: Detailed order-by-order breakdown

Example:
```
================================================================================
SIMULATED LIVE TRADING SESSION LOG
================================================================================
Session Start: 2024-01-01 12:00:00
Session End: 2024-01-01 14:30:00
Initial Capital: $10,000.00
Final Equity: $10,234.50
Total P&L: $234.50

================================================================================
PERFORMANCE METRICS
================================================================================
total_orders: 15
filled_orders: 14
win_rate: 0.57
...

================================================================================
EXECUTION HISTORY
================================================================================
Order ID: SIM_1_1704110400000
  Symbol: BTCUSDT
  Side: BUY
  Quantity: 0.1/0.1
  Execution Price: $50000.00
  ...
```

## Performance Optimization

The View Session feature includes several optimizations:

1. **Lazy Loading**: Session details are loaded only when requested
2. **Efficient Parsing**: Log files are parsed on-demand
3. **Client-Side Filtering**: Search and filter operations happen in the browser
4. **Caching**: Session list is cached to reduce server load

## Styling and Theming

The View Session feature fully supports the dashboard's theme system:

- **Dark Mode**: Automatically adapts to dark theme
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Smooth Animations**: Fade-in effects and hover states
- **Color Coding**: Visual indicators for profit/loss

## Future Enhancements

Planned features for future releases:

- [ ] Real-time session monitoring for active sessions
- [ ] Session comparison tool (side-by-side comparison)
- [ ] Advanced filtering (date range, strategy type)
- [ ] Session analytics dashboard (aggregate statistics)
- [ ] Auto-archiving of old sessions
- [ ] Session notes and annotations
- [ ] Export to JSON format
- [ ] Print-friendly reports

## Troubleshooting

### No Sessions Displayed

**Problem**: The session list is empty

**Solutions**:
- Check if the `logs/` directory exists
- Verify that session log files follow the naming convention
- Run a simulated trading session to generate logs
- Check browser console for API errors

### Session Details Not Loading

**Problem**: Clicking "View Details" shows an error

**Solutions**:
- Verify the session log file exists and is readable
- Check the log file format is correct
- Look for parsing errors in the server logs

### Export Not Working

**Problem**: Export button doesn't download a file

**Solutions**:
- Check browser's download settings
- Ensure pop-ups are not blocked
- Verify the session exists and is accessible

## Integration with Simulated Trading

The View Session feature integrates seamlessly with the Simulated Live Trading environment:

```python
from simulated_live_trading import SimulatedLiveTradingEnvironment

# Create environment
env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)

# Execute trades
env.place_market_order('BTCUSDT', 0.1, 'BUY')

# Save session log (automatically viewable in dashboard)
env.save_session_log()
```

## Best Practices

1. **Regular Session Reviews**: Review sessions regularly to identify patterns
2. **Compare Strategies**: Use filtering to compare different strategy performances
3. **Export for Analysis**: Export data for deeper analysis in tools like Python or R
4. **Clean Old Sessions**: Periodically archive or delete old session logs
5. **Document Insights**: Keep notes about successful sessions for future reference

## Support and Feedback

For questions, issues, or feature requests:
- Check the main documentation
- Review existing session logs for examples
- Test with demo sessions before live trading

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
