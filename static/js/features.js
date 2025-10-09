/**
 * Trading Bot Dashboard - Feature Modules
 * Strategy management, broker connection, and settings
 */

// Feature Module Manager
const Features = {
    activeView: 'dashboard',
    
    // Initialize feature modules
    init() {
        this.setupNavigation();
        this.setupModals();
        this.setupQuickAccess();
        console.log('Feature modules initialized');
    },
    
    // Setup quick access button
    setupQuickAccess() {
        const quickAccessBtn = document.getElementById('quickViewSessions');
        if (quickAccessBtn) {
            quickAccessBtn.addEventListener('click', () => {
                this.showViewSessions();
            });
        }
    },
    
    // Setup navigation between views
    setupNavigation() {
        const navButtons = document.querySelectorAll('.nav-button');
        navButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const buttonText = e.target.textContent.trim();
                this.switchView(buttonText);
            });
        });
    },
    
    // Switch between different views
    switchView(viewName) {
        // Update active button
        document.querySelectorAll('.nav-button').forEach(btn => {
            btn.classList.remove('active');
            if (btn.textContent.trim() === viewName) {
                btn.classList.add('active');
            }
        });
        
        // Handle view switching
        switch(viewName) {
            case 'Dashboard':
                this.showDashboard();
                break;
            case 'Strategies':
                this.showStrategies();
                break;
            case 'Trade History':
                this.showTradeHistory();
                break;
            case 'View Sessions':
                this.showViewSessions();
                break;
            case 'Settings':
                this.showSettings();
                break;
            case 'Broker Connection':
                this.showBrokerConnection();
                break;
        }
        
        this.activeView = viewName;
    },
    
    // Show dashboard view
    showDashboard() {
        document.querySelectorAll('.metrics-grid, .charts-section, .trades-section').forEach(el => {
            el.style.display = '';
        });
        this.hideModals();
    },
    
    // Show strategies view
    showStrategies() {
        this.hideAllViews();
        const modal = this.createModal('Strategy Management', this.getStrategiesContent());
        document.body.appendChild(modal);
    },
    
    // Show trade history view
    showTradeHistory() {
        this.hideAllViews();
        const modal = this.createModal('Trade History', this.getTradeHistoryContent());
        document.body.appendChild(modal);
    },
    
    // Show settings view
    showSettings() {
        this.hideAllViews();
        const modal = this.createModal('Settings', this.getSettingsContent());
        document.body.appendChild(modal);
    },
    
    // Show view sessions view
    showViewSessions() {
        this.hideAllViews();
        const modal = this.createModal('View Sessions', this.getViewSessionsContent());
        document.body.appendChild(modal);
        // Load sessions data
        this.loadSessions();
    },
    
    // Show broker connection view
    showBrokerConnection() {
        this.hideAllViews();
        const modal = this.createModal('Broker Connection', this.getBrokerConnectionContent());
        document.body.appendChild(modal);
    },
    
    // Hide all main views
    hideAllViews() {
        document.querySelectorAll('.metrics-grid, .charts-section, .trades-section').forEach(el => {
            el.style.display = 'none';
        });
    },
    
    // Setup modal functionality
    setupModals() {
        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideModals();
                this.showDashboard();
            }
        });
    },
    
    // Create modal element
    createModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'feature-modal';
        
        // Add quick access to View Sessions unless we're already in View Sessions
        const quickAccessLink = title !== 'View Sessions' ? `
            <button class="modal-quick-access" onclick="Features.showViewSessions()" title="Quick Access to View Sessions">
                <i class="fas fa-folder-open"></i> View Sessions
            </button>
        ` : '';
        
        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <div class="modal-header-actions">
                        ${quickAccessLink}
                        <button class="modal-close" aria-label="Close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        
        // Close button handler
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => {
            this.hideModals();
            this.showDashboard();
        });
        
        // Overlay click to close
        const overlay = modal.querySelector('.modal-overlay');
        overlay.addEventListener('click', () => {
            this.hideModals();
            this.showDashboard();
        });
        
        return modal;
    },
    
    // Hide all modals
    hideModals() {
        document.querySelectorAll('.feature-modal').forEach(modal => {
            modal.remove();
        });
    },
    
    // Get strategies content
    getStrategiesContent() {
        return `
            <div class="strategies-panel">
                <div class="panel-section">
                    <h3><i class="fas fa-robot"></i> Active Strategies</h3>
                    <div class="strategy-list">
                        <div class="strategy-item active">
                            <div class="strategy-info">
                                <strong>MA Crossover</strong>
                                <span class="strategy-status enabled">Enabled</span>
                            </div>
                            <p>Moving Average crossover strategy for trend following</p>
                            <div class="strategy-metrics">
                                <span><i class="fas fa-chart-line"></i> Win Rate: 45%</span>
                                <span><i class="fas fa-dollar-sign"></i> Total P&L: $234.50</span>
                            </div>
                        </div>
                        
                        <div class="strategy-item active">
                            <div class="strategy-info">
                                <strong>RSI Mean Reversion</strong>
                                <span class="strategy-status enabled">Enabled</span>
                            </div>
                            <p>Oversold/Overbought detection using RSI indicator</p>
                            <div class="strategy-metrics">
                                <span><i class="fas fa-chart-line"></i> Win Rate: 38%</span>
                                <span><i class="fas fa-dollar-sign"></i> Total P&L: $156.80</span>
                            </div>
                        </div>
                        
                        <div class="strategy-item">
                            <div class="strategy-info">
                                <strong>Bollinger Bands</strong>
                                <span class="strategy-status disabled">Disabled</span>
                            </div>
                            <p>Volatility breakout strategy using Bollinger Bands</p>
                            <div class="strategy-metrics">
                                <span><i class="fas fa-chart-line"></i> Win Rate: N/A</span>
                                <span><i class="fas fa-dollar-sign"></i> Total P&L: $0.00</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="panel-section">
                    <h3><i class="fas fa-cog"></i> Strategy Settings</h3>
                    <div class="settings-form">
                        <div class="form-group">
                            <label>Cooperation Logic</label>
                            <select class="form-control">
                                <option>AND (Conservative)</option>
                                <option selected>OR (Aggressive)</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Position Size (%)</label>
                            <input type="number" class="form-control" value="10" min="1" max="100">
                        </div>
                        
                        <div class="form-group">
                            <label>Risk Level</label>
                            <input type="range" class="form-control-range" min="1" max="5" value="3">
                            <div class="range-labels">
                                <span>Low</span>
                                <span>Medium</span>
                                <span>High</span>
                            </div>
                        </div>
                        
                        <button class="btn btn-primary">
                            <i class="fas fa-save"></i> Save Settings
                        </button>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Get trade history content
    getTradeHistoryContent() {
        return `
            <div class="trade-history-panel">
                <div class="panel-header">
                    <div class="filter-controls">
                        <input type="date" class="form-control" placeholder="From Date">
                        <input type="date" class="form-control" placeholder="To Date">
                        <select class="form-control">
                            <option>All Strategies</option>
                            <option>MA Crossover</option>
                            <option>RSI Mean Reversion</option>
                        </select>
                        <button class="btn btn-secondary">
                            <i class="fas fa-filter"></i> Filter
                        </button>
                        <button class="btn btn-secondary">
                            <i class="fas fa-download"></i> Export CSV
                        </button>
                    </div>
                </div>
                
                <div class="panel-body">
                    <div class="stats-summary">
                        <div class="stat-box">
                            <span class="stat-label">Total Trades</span>
                            <span class="stat-value">50</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-label">Winning Trades</span>
                            <span class="stat-value success">15</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-label">Losing Trades</span>
                            <span class="stat-value danger">35</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-label">Win Rate</span>
                            <span class="stat-value">30%</span>
                        </div>
                    </div>
                    
                    <div class="trade-details">
                        <p><i class="fas fa-info-circle"></i> Use the Recent Trades table on the dashboard for detailed trade information.</p>
                        <p>Filter options and CSV export coming soon!</p>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Get settings content
    getSettingsContent() {
        return `
            <div class="settings-panel">
                <div class="panel-section">
                    <h3><i class="fas fa-palette"></i> Appearance</h3>
                    <div class="settings-form">
                        <div class="form-group">
                            <label>Theme</label>
                            <div class="button-group">
                                <button class="btn btn-outline">Light</button>
                                <button class="btn btn-outline">Dark</button>
                                <button class="btn btn-outline active">Auto</button>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label>Chart Style</label>
                            <select class="form-control">
                                <option selected>Modern</option>
                                <option>Classic</option>
                                <option>Minimal</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div class="panel-section">
                    <h3><i class="fas fa-bell"></i> Notifications</h3>
                    <div class="settings-form">
                        <div class="form-check">
                            <input type="checkbox" id="notif-trades" checked>
                            <label for="notif-trades">Trade Execution Alerts</label>
                        </div>
                        
                        <div class="form-check">
                            <input type="checkbox" id="notif-profit">
                            <label for="notif-profit">Profit Target Reached</label>
                        </div>
                        
                        <div class="form-check">
                            <input type="checkbox" id="notif-loss">
                            <label for="notif-loss">Stop Loss Triggered</label>
                        </div>
                    </div>
                </div>
                
                <div class="panel-section">
                    <h3><i class="fas fa-sync"></i> Auto-Refresh</h3>
                    <div class="settings-form">
                        <div class="form-group">
                            <label>Refresh Interval</label>
                            <select class="form-control">
                                <option>10 seconds</option>
                                <option selected>30 seconds</option>
                                <option>1 minute</option>
                                <option>5 minutes</option>
                            </select>
                        </div>
                        
                        <div class="form-check">
                            <input type="checkbox" id="pause-hidden" checked>
                            <label for="pause-hidden">Pause when tab is hidden</label>
                        </div>
                    </div>
                </div>
                
                <div class="panel-section">
                    <button class="btn btn-primary">
                        <i class="fas fa-save"></i> Save All Settings
                    </button>
                    <button class="btn btn-outline">
                        <i class="fas fa-undo"></i> Reset to Defaults
                    </button>
                </div>
            </div>
        `;
    },
    
    // Get view sessions content
    getViewSessionsContent() {
        return `
            <div class="sessions-panel">
                <div class="panel-header">
                    <div class="filter-controls">
                        <input type="text" id="sessionSearch" class="form-control" placeholder="Search sessions..." oninput="Features.loadSessions()">
                        <select id="sessionFilter" class="form-control" onchange="Features.loadSessions()">
                            <option value="all">All Sessions</option>
                            <option value="profitable">Profitable Only</option>
                            <option value="loss">Loss Only</option>
                        </select>
                        <input type="date" id="sessionDateFrom" class="form-control" placeholder="From Date" onchange="Features.loadSessions()">
                        <input type="date" id="sessionDateTo" class="form-control" placeholder="To Date" onchange="Features.loadSessions()">
                        <button class="btn btn-secondary" onclick="Features.loadSessions()">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                        <button class="btn btn-outline" onclick="Features.clearFilters()">
                            <i class="fas fa-times"></i> Clear Filters
                        </button>
                    </div>
                </div>
                
                <div class="panel-body">
                    <div id="sessionsLoading" class="loading-indicator" style="display: none;">
                        <i class="fas fa-spinner fa-spin"></i> Loading sessions...
                    </div>
                    
                    <div id="sessionsList" class="sessions-list">
                        <!-- Sessions will be loaded here -->
                    </div>
                    
                    <div id="sessionsEmpty" class="empty-state" style="display: none;">
                        <i class="fas fa-inbox"></i>
                        <p>No trading sessions found</p>
                        <small>Sessions will appear here after running simulated trading</small>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Clear all filters
    clearFilters() {
        const searchEl = document.getElementById('sessionSearch');
        const filterEl = document.getElementById('sessionFilter');
        const dateFromEl = document.getElementById('sessionDateFrom');
        const dateToEl = document.getElementById('sessionDateTo');
        
        if (searchEl) searchEl.value = '';
        if (filterEl) filterEl.value = 'all';
        if (dateFromEl) dateFromEl.value = '';
        if (dateToEl) dateToEl.value = '';
        
        this.loadSessions();
    },
    
    // Parse session date from session ID
    parseSessionDate(sessionId) {
        try {
            // Session ID format: YYYYMMDD_HHMMSS
            const parts = sessionId.split('_');
            if (parts.length >= 1) {
                const dateStr = parts[0];
                const year = dateStr.substring(0, 4);
                const month = dateStr.substring(4, 6);
                const day = dateStr.substring(6, 8);
                return new Date(`${year}-${month}-${day}`);
            }
        } catch (e) {
            console.error('Error parsing session date:', e);
        }
        return null;
    },
    
    // Load sessions from API
    async loadSessions() {
        const loadingEl = document.getElementById('sessionsLoading');
        const listEl = document.getElementById('sessionsList');
        const emptyEl = document.getElementById('sessionsEmpty');
        
        if (!listEl) return;
        
        try {
            if (loadingEl) loadingEl.style.display = 'block';
            if (listEl) listEl.innerHTML = '';
            if (emptyEl) emptyEl.style.display = 'none';
            
            const response = await fetch('/api/sessions');
            const sessions = await response.json();
            
            if (loadingEl) loadingEl.style.display = 'none';
            
            if (!sessions || sessions.length === 0) {
                if (emptyEl) emptyEl.style.display = 'block';
                return;
            }
            
            // Apply filters
            const searchTerm = document.getElementById('sessionSearch')?.value.toLowerCase() || '';
            const filter = document.getElementById('sessionFilter')?.value || 'all';
            const dateFrom = document.getElementById('sessionDateFrom')?.value || '';
            const dateTo = document.getElementById('sessionDateTo')?.value || '';
            
            const filteredSessions = sessions.filter(session => {
                // Search filter
                const matchesSearch = !searchTerm || 
                    session.id.toLowerCase().includes(searchTerm) ||
                    session.timestamp.toLowerCase().includes(searchTerm);
                
                // Performance filter
                let matchesFilter = true;
                if (filter === 'profitable') {
                    matchesFilter = session.total_pnl > 0;
                } else if (filter === 'loss') {
                    matchesFilter = session.total_pnl < 0;
                }
                
                // Date range filter
                let matchesDateRange = true;
                if (dateFrom || dateTo) {
                    // Extract date from session ID (format: YYYYMMDD_HHMMSS)
                    const sessionDate = this.parseSessionDate(session.id);
                    if (sessionDate) {
                        if (dateFrom) {
                            const fromDate = new Date(dateFrom);
                            if (sessionDate < fromDate) matchesDateRange = false;
                        }
                        if (dateTo) {
                            const toDate = new Date(dateTo);
                            toDate.setHours(23, 59, 59); // Include full day
                            if (sessionDate > toDate) matchesDateRange = false;
                        }
                    }
                }
                
                return matchesSearch && matchesFilter && matchesDateRange;
            });
            
            if (filteredSessions.length === 0) {
                if (emptyEl) emptyEl.style.display = 'block';
                return;
            }
            
            // Render sessions
            filteredSessions.forEach(session => {
                const sessionCard = this.createSessionCard(session);
                listEl.appendChild(sessionCard);
            });
            
        } catch (error) {
            console.error('Error loading sessions:', error);
            if (loadingEl) loadingEl.style.display = 'none';
            if (listEl) listEl.innerHTML = '<div class="error-message"><i class="fas fa-exclamation-triangle"></i> Error loading sessions</div>';
        }
    },
    
    // Create session card element
    createSessionCard(session) {
        const card = document.createElement('div');
        card.className = 'session-card';
        
        const pnlClass = session.total_pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
        const pnlIcon = session.total_pnl >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
        
        card.innerHTML = `
            <div class="session-header">
                <div class="session-id">
                    <i class="fas fa-calendar-alt"></i>
                    <strong>Session ${session.id}</strong>
                </div>
                <div class="session-pnl ${pnlClass}">
                    <i class="fas ${pnlIcon}"></i>
                    $${session.total_pnl.toFixed(2)}
                </div>
            </div>
            <div class="session-info">
                <div class="info-row">
                    <span><i class="fas fa-clock"></i> ${session.timestamp || 'N/A'}</span>
                </div>
                <div class="info-row">
                    <span><i class="fas fa-wallet"></i> Capital: $${session.initial_capital.toFixed(2)} → $${session.final_equity.toFixed(2)}</span>
                </div>
                <div class="info-row">
                    <span><i class="fas fa-exchange-alt"></i> Trades: ${session.total_trades || 0}</span>
                    <span><i class="fas fa-percentage"></i> Win Rate: ${(session.win_rate || 0).toFixed(1)}%</span>
                </div>
            </div>
            <div class="session-actions">
                <button class="btn btn-primary btn-sm" onclick="Features.viewSessionDetails('${session.id}')">
                    <i class="fas fa-eye"></i> View Details
                </button>
                <button class="btn btn-secondary btn-sm" onclick="Features.exportSession('${session.id}')">
                    <i class="fas fa-download"></i> Export
                </button>
            </div>
        `;
        
        return card;
    },
    
    // View session details
    async viewSessionDetails(sessionId) {
        try {
            const response = await fetch(`/api/sessions/${sessionId}`);
            const sessionData = await response.json();
            
            if (sessionData.error) {
                alert('Session not found or error loading details');
                return;
            }
            
            // Create detail modal
            const detailModal = this.createModal(`Session Details - ${sessionId}`, this.getSessionDetailContent(sessionData));
            document.body.appendChild(detailModal);
            
            // Render charts
            setTimeout(() => {
                this.renderSessionCharts(sessionData);
            }, 100);
            
        } catch (error) {
            console.error('Error loading session details:', error);
            alert('Error loading session details');
        }
    },
    
    // Get session detail content
    getSessionDetailContent(sessionData) {
        return `
            <div class="session-detail">
                <div class="detail-metrics">
                    <div class="metric-box">
                        <span class="metric-label">Initial Capital</span>
                        <span class="metric-value">$${(sessionData.metrics.initial_capital || 0)}</span>
                    </div>
                    <div class="metric-box">
                        <span class="metric-label">Final Equity</span>
                        <span class="metric-value">$${(sessionData.metrics.final_equity || 0)}</span>
                    </div>
                    <div class="metric-box">
                        <span class="metric-label">Total P&L</span>
                        <span class="metric-value ${(sessionData.metrics.total_pnl >= 0) ? 'success' : 'danger'}">
                            $${(sessionData.metrics.total_pnl || 0)}
                        </span>
                    </div>
                    <div class="metric-box">
                        <span class="metric-label">Total Trades</span>
                        <span class="metric-value">${sessionData.metrics.total_orders || 0}</span>
                    </div>
                </div>
                
                <div class="detail-filters">
                    <h4><i class="fas fa-filter"></i> Filter Trades</h4>
                    <div class="filter-controls">
                        <select id="tradeTypeFilter" class="form-control" onchange="Features.filterTrades()">
                            <option value="all">All Trade Types</option>
                            <option value="BUY">Buy Orders</option>
                            <option value="SELL">Sell Orders</option>
                        </select>
                        <select id="tradeStatusFilter" class="form-control" onchange="Features.filterTrades()">
                            <option value="all">All Status</option>
                            <option value="FILLED">Filled</option>
                            <option value="PARTIAL">Partial</option>
                            <option value="CANCELLED">Cancelled</option>
                        </select>
                        <select id="symbolFilter" class="form-control" onchange="Features.filterTrades()">
                            <option value="all">All Symbols</option>
                            ${this.getUniqueSymbols(sessionData.trades).map(symbol => 
                                `<option value="${symbol}">${symbol}</option>`
                            ).join('')}
                        </select>
                    </div>
                </div>
                
                <div class="detail-charts">
                    <div class="charts-grid">
                        <div class="chart-box">
                            <h4>Cumulative P&L Over Time</h4>
                            <canvas id="sessionPnLChart"></canvas>
                        </div>
                        <div class="chart-box">
                            <h4>Win/Loss Distribution</h4>
                            <canvas id="sessionWinLossChart"></canvas>
                        </div>
                    </div>
                    <div class="charts-grid">
                        <div class="chart-box">
                            <h4>Trade Types Distribution</h4>
                            <canvas id="sessionTradeTypesChart"></canvas>
                        </div>
                        <div class="chart-box">
                            <h4>Execution Prices Timeline</h4>
                            <canvas id="sessionTradesChart"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="detail-trades">
                    <h4><i class="fas fa-list"></i> Execution History</h4>
                    <div class="trades-table-container">
                        <table class="trades-table" id="tradesTable">
                            <thead>
                                <tr>
                                    <th>Order ID</th>
                                    <th>Symbol</th>
                                    <th>Side</th>
                                    <th>Quantity</th>
                                    <th>Price</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody id="tradesTableBody">
                                ${sessionData.trades.map(trade => `
                                    <tr data-side="${trade.side}" data-status="${trade.status}" data-symbol="${trade.symbol}">
                                        <td>${trade.order_id || 'N/A'}</td>
                                        <td>${trade.symbol || 'N/A'}</td>
                                        <td class="${(trade.side === 'BUY') ? 'trade-type-buy' : 'trade-type-sell'}">
                                            ${trade.side || 'N/A'}
                                        </td>
                                        <td>${trade.quantity || trade.filled_quantity || 'N/A'}</td>
                                        <td>$${trade.execution_price || 'N/A'}</td>
                                        <td>${trade.status || 'N/A'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Get unique symbols from trades
    getUniqueSymbols(trades) {
        const symbols = new Set();
        trades.forEach(trade => {
            if (trade.symbol) {
                symbols.add(trade.symbol);
            }
        });
        return Array.from(symbols).sort();
    },
    
    // Filter trades based on selected filters
    filterTrades() {
        const typeFilter = document.getElementById('tradeTypeFilter')?.value || 'all';
        const statusFilter = document.getElementById('tradeStatusFilter')?.value || 'all';
        const symbolFilter = document.getElementById('symbolFilter')?.value || 'all';
        
        const rows = document.querySelectorAll('#tradesTableBody tr');
        rows.forEach(row => {
            const side = row.getAttribute('data-side');
            const status = row.getAttribute('data-status');
            const symbol = row.getAttribute('data-symbol');
            
            let show = true;
            if (typeFilter !== 'all' && side !== typeFilter) show = false;
            if (statusFilter !== 'all' && status !== statusFilter) show = false;
            if (symbolFilter !== 'all' && symbol !== symbolFilter) show = false;
            
            row.style.display = show ? '' : 'none';
        });
    },
    
    // Render session charts
    renderSessionCharts(sessionData) {
        // 1. Cumulative P&L Over Time (Line Chart)
        const pnlCtx = document.getElementById('sessionPnLChart');
        if (pnlCtx && sessionData.chart_data && sessionData.chart_data.pnl_over_time) {
            const pnlData = sessionData.chart_data.pnl_over_time;
            new Chart(pnlCtx, {
                type: 'line',
                data: {
                    labels: pnlData.map(d => `Trade ${d.trade_number}`),
                    datasets: [{
                        label: 'Cumulative P&L ($)',
                        data: pnlData.map(d => d.cumulative_pnl),
                        borderColor: 'rgb(102, 126, 234)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 3,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // 2. Win/Loss Distribution (Bar Chart)
        const winLossCtx = document.getElementById('sessionWinLossChart');
        if (winLossCtx && sessionData.chart_data && sessionData.chart_data.win_loss_distribution) {
            const winLossData = sessionData.chart_data.win_loss_distribution;
            new Chart(winLossCtx, {
                type: 'bar',
                data: {
                    labels: ['Wins', 'Losses'],
                    datasets: [{
                        label: 'Number of Trades',
                        data: [winLossData.wins, winLossData.losses],
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(255, 99, 132, 0.8)'
                        ],
                        borderColor: [
                            'rgb(75, 192, 192)',
                            'rgb(255, 99, 132)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        }
        
        // 3. Trade Types Distribution (Doughnut Chart)
        const tradeTypesCtx = document.getElementById('sessionTradeTypesChart');
        if (tradeTypesCtx && sessionData.chart_data && sessionData.chart_data.trade_types) {
            const tradeTypes = sessionData.chart_data.trade_types;
            new Chart(tradeTypesCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Buy Orders', 'Sell Orders'],
                    datasets: [{
                        data: [tradeTypes.BUY || 0, tradeTypes.SELL || 0],
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(118, 75, 162, 0.8)'
                        ],
                        borderColor: [
                            'rgb(102, 126, 234)',
                            'rgb(118, 75, 162)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        // 4. Execution Prices Timeline (Line Chart)
        const tradesCtx = document.getElementById('sessionTradesChart');
        if (tradesCtx) {
            const trades = sessionData.trades || [];
            const labels = trades.map((t, i) => `Trade ${i + 1}`);
            const prices = trades.map(t => {
                const priceStr = (t.execution_price || '0').replace('$', '').replace(',', '');
                return parseFloat(priceStr) || 0;
            });
            
            new Chart(tradesCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Execution Price ($)',
                        data: prices,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1,
                        pointRadius: 4,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        }
    },
    
    // Export session
    async exportSession(sessionId) {
        try {
            const response = await fetch(`/api/sessions/${sessionId}`);
            const sessionData = await response.json();
            
            if (sessionData.error) {
                alert('Session not found');
                return;
            }
            
            // Convert to CSV
            const csv = this.convertSessionToCSV(sessionData);
            
            // Download
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `session_${sessionId}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error exporting session:', error);
            alert('Error exporting session');
        }
    },
    
    // Convert session to CSV
    convertSessionToCSV(sessionData) {
        const trades = sessionData.trades || [];
        let csv = 'Order ID,Symbol,Side,Quantity,Execution Price,Status\n';
        
        trades.forEach(trade => {
            csv += `${trade.order_id || ''},${trade.symbol || ''},${trade.side || ''},${trade.quantity || trade.filled_quantity || ''},${trade.execution_price || ''},${trade.status || ''}\n`;
        });
        
        return csv;
    },
    
    // Get broker connection content
    getBrokerConnectionContent() {
        return `
            <div class="broker-panel">
                <div class="panel-section">
                    <h3><i class="fas fa-plug"></i> Connection Status</h3>
                    <div class="connection-status">
                        <div class="status-indicator">
                            <div class="status-light success"></div>
                            <strong>Connected</strong>
                        </div>
                        <p>Paper Trading Mode (Simulation)</p>
                    </div>
                </div>
                
                <div class="panel-section">
                    <h3><i class="fas fa-exchange-alt"></i> Broker Configuration</h3>
                    <div class="settings-form">
                        <div class="form-group">
                            <label>Broker Type</label>
                            <select class="form-control">
                                <option selected>Paper Trading (Simulation)</option>
                                <option>Binance (Cryptocurrency)</option>
                                <option>Interactive Brokers</option>
                                <option>Alpaca (Stocks)</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>API Key</label>
                            <input type="password" class="form-control" placeholder="Enter API Key" value="••••••••••••••••">
                        </div>
                        
                        <div class="form-group">
                            <label>API Secret</label>
                            <input type="password" class="form-control" placeholder="Enter API Secret" value="••••••••••••••••">
                        </div>
                        
                        <div class="form-check">
                            <input type="checkbox" id="testnet" checked>
                            <label for="testnet">Use Testnet (Recommended for testing)</label>
                        </div>
                        
                        <button class="btn btn-primary">
                            <i class="fas fa-plug"></i> Test Connection
                        </button>
                        <button class="btn btn-success">
                            <i class="fas fa-save"></i> Save & Connect
                        </button>
                    </div>
                </div>
                
                <div class="panel-section">
                    <h3><i class="fas fa-info-circle"></i> Broker Information</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Account Type:</span>
                            <span class="info-value">Demo/Paper</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Available Balance:</span>
                            <span class="info-value">$10,077.92</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Last Update:</span>
                            <span class="info-value">2 minutes ago</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">API Calls Today:</span>
                            <span class="info-value">247 / 1000</span>
                        </div>
                    </div>
                </div>
                
                <div class="panel-section alert-info">
                    <i class="fas fa-info-circle"></i>
                    <div>
                        <strong>Setup Guide:</strong>
                        <p>For detailed broker integration instructions, see <code>BROKER_INTEGRATION_README.md</code></p>
                    </div>
                </div>
            </div>
        `;
    }
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Features.init());
} else {
    Features.init();
}
