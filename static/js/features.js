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
        console.log('Feature modules initialized');
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
        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close" aria-label="Close">
                        <i class="fas fa-times"></i>
                    </button>
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
