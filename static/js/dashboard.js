/**
 * Trading Bot Dashboard - Enhanced JavaScript
 * Real-time data updates with smooth animations and caching
 */

// Configuration
const CONFIG = {
    AUTO_REFRESH_INTERVAL: 30000, // 30 seconds
    CACHE_DURATION: 10000, // 10 seconds
    API_ENDPOINTS: {
        metrics: '/api/metrics',
        charts: '/api/charts',
        trades: '/api/trades',
        status: '/api/status'
    }
};

// State management
const state = {
    charts: {
        equity: null,
        pnl: null,
        strategy: null
    },
    cache: new Map(),
    isDarkMode: false,
    isLoading: false
};

// Cache management
function getCachedData(key) {
    const cached = state.cache.get(key);
    if (cached && Date.now() - cached.timestamp < CONFIG.CACHE_DURATION) {
        return cached.data;
    }
    return null;
}

function setCachedData(key, data) {
    state.cache.set(key, {
        data: data,
        timestamp: Date.now()
    });
}

// API calls with caching
async function fetchWithCache(url) {
    const cached = getCachedData(url);
    if (cached) {
        console.log(`Using cached data for ${url}`);
        return cached;
    }
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setCachedData(url, data);
        return data;
    } catch (error) {
        console.error(`Error fetching ${url}:`, error);
        throw error;
    }
}

// Utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

function formatPercentage(value) {
    return value.toFixed(2) + '%';
}

function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

// Theme management
function initTheme() {
    const savedTheme = localStorage.getItem('dashboard-theme');
    if (savedTheme === 'dark') {
        enableDarkMode();
    }
}

function toggleTheme() {
    state.isDarkMode = !state.isDarkMode;
    if (state.isDarkMode) {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
}

function enableDarkMode() {
    document.body.classList.add('dark-mode');
    state.isDarkMode = true;
    localStorage.setItem('dashboard-theme', 'dark');
    updateChartThemes();
}

function disableDarkMode() {
    document.body.classList.remove('dark-mode');
    state.isDarkMode = false;
    localStorage.setItem('dashboard-theme', 'light');
    updateChartThemes();
}

function updateChartThemes() {
    // Update chart colors based on theme
    const textColor = state.isDarkMode ? '#f8fafc' : '#111827';
    const gridColor = state.isDarkMode ? '#334155' : '#e5e7eb';
    
    Object.values(state.charts).forEach(chart => {
        if (chart) {
            chart.options.scales.x.ticks.color = textColor;
            chart.options.scales.y.ticks.color = textColor;
            chart.options.scales.x.grid.color = gridColor;
            chart.options.scales.y.grid.color = gridColor;
            chart.update('none'); // Update without animation
        }
    });
}

// Metrics loading
async function loadMetrics() {
    try {
        const metrics = await fetchWithCache(CONFIG.API_ENDPOINTS.metrics);
        
        const grid = document.getElementById('metricsGrid');
        if (!grid) return;
        
        grid.innerHTML = '';
        
        const metricConfigs = [
            { key: 'total_pnl', label: 'Total P&L', icon: 'fa-dollar-sign', format: 'currency', checkSign: true },
            { key: 'current_capital', label: 'Current Capital', icon: 'fa-wallet', format: 'currency' },
            { key: 'total_trades', label: 'Total Trades', icon: 'fa-exchange-alt', format: 'number' },
            { key: 'win_rate', label: 'Win Rate', icon: 'fa-percentage', format: 'percentage', checkSign: true },
            { key: 'best_trade', label: 'Best Trade', icon: 'fa-trophy', format: 'currency' },
            { key: 'worst_trade', label: 'Worst Trade', icon: 'fa-exclamation-triangle', format: 'currency' }
        ];
        
        metricConfigs.forEach((config, index) => {
            const value = metrics[config.key] || 0;
            const card = document.createElement('div');
            card.className = 'metric-card';
            card.style.animationDelay = `${index * 0.1}s`;
            
            if (config.checkSign) {
                if (value > 0) card.classList.add('positive');
                else if (value < 0) card.classList.add('negative');
            }
            
            let displayValue = value;
            if (config.format === 'currency') {
                displayValue = formatCurrency(value);
            } else if (config.format === 'percentage') {
                displayValue = formatPercentage(value);
            } else if (config.format === 'number') {
                displayValue = formatNumber(value);
            }
            
            card.innerHTML = `
                <div class="label">
                    <i class="fas ${config.icon}"></i>
                    ${config.label}
                </div>
                <div class="value">${displayValue}</div>
            `;
            
            grid.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading metrics:', error);
        showError('Failed to load metrics');
    }
}

// Chart loading
async function loadCharts() {
    try {
        const chartsData = await fetchWithCache(CONFIG.API_ENDPOINTS.charts);
        
        // Equity Curve
        if (chartsData.pnl_history && chartsData.pnl_history.labels) {
            createEquityChart(chartsData.pnl_history);
        }
        
        // P&L Distribution
        if (chartsData.win_loss && chartsData.win_loss.labels) {
            createPnLChart(chartsData.win_loss);
        }
        
        // Strategy Performance
        if (chartsData.strategy_stats && chartsData.strategy_stats.labels) {
            createStrategyChart(chartsData.strategy_stats);
        }
    } catch (error) {
        console.error('Error loading charts:', error);
        showError('Failed to load charts');
    }
}

function createEquityChart(data) {
    const ctx = document.getElementById('equityChart');
    if (!ctx) return;
    
    if (state.charts.equity) {
        state.charts.equity.destroy();
    }
    
    const textColor = state.isDarkMode ? '#f8fafc' : '#111827';
    const gridColor = state.isDarkMode ? '#334155' : '#e5e7eb';
    
    state.charts.equity = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Capital',
                data: data.values,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 3,
                pointHoverRadius: 6,
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 },
                    callbacks: {
                        label: function(context) {
                            return 'Capital: ' + formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: textColor },
                    grid: { color: gridColor, display: false }
                },
                y: {
                    ticks: { 
                        color: textColor,
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    },
                    grid: { color: gridColor }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function createPnLChart(data) {
    const ctx = document.getElementById('pnlChart');
    if (!ctx) return;
    
    if (state.charts.pnl) {
        state.charts.pnl.destroy();
    }
    
    const textColor = state.isDarkMode ? '#f8fafc' : '#111827';
    const gridColor = state.isDarkMode ? '#334155' : '#e5e7eb';
    const values = data.values || [];
    const colors = values.map(v => v >= 0 ? '#10b981' : '#ef4444');
    
    state.charts.pnl = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'P&L',
                data: values,
                backgroundColor: colors,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 },
                    callbacks: {
                        label: function(context) {
                            return 'P&L: ' + formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: textColor },
                    grid: { color: gridColor, display: false }
                },
                y: {
                    ticks: { 
                        color: textColor,
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    },
                    grid: { color: gridColor }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function createStrategyChart(data) {
    const ctx = document.getElementById('strategyChart');
    if (!ctx) return;
    
    if (state.charts.strategy) {
        state.charts.strategy.destroy();
    }
    
    const textColor = state.isDarkMode ? '#f8fafc' : '#111827';
    
    state.charts.strategy = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#4facfe',
                    '#00f2fe',
                    '#43e97b'
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: textColor,
                        padding: 15,
                        font: { size: 12, weight: '600' },
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Trades loading
async function loadTrades() {
    try {
        const trades = await fetchWithCache(CONFIG.API_ENDPOINTS.trades);
        
        const tbody = document.getElementById('tradesBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        const recentTrades = trades.slice(-20).reverse();
        
        recentTrades.forEach((trade, index) => {
            const row = document.createElement('tr');
            row.style.animationDelay = `${index * 0.05}s`;
            
            const pnl = parseFloat(trade.pnl || 0);
            const pnlClass = pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
            const typeClass = trade.order_type === 'BUY' ? 'trade-type-buy' : 'trade-type-sell';
            
            row.innerHTML = `
                <td>${trade.timestamp}</td>
                <td class="${typeClass}">${trade.order_type}</td>
                <td>${formatCurrency(parseFloat(trade.price))}</td>
                <td>${trade.quantity}</td>
                <td>${trade.triggering_strategies || '-'}</td>
                <td class="${pnlClass}">${formatCurrency(pnl)}</td>
                <td>${formatCurrency(parseFloat(trade.capital))}</td>
            `;
            
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading trades:', error);
        showError('Failed to load trades');
    }
}

// Status indicator
function showLoading(show = true) {
    const loading = document.getElementById('loading');
    if (loading) {
        if (show) {
            loading.classList.add('active');
        } else {
            loading.classList.remove('active');
        }
    }
    
    const refreshBtn = document.querySelector('.refresh-button');
    if (refreshBtn) {
        if (show) {
            refreshBtn.classList.add('spinning');
        } else {
            refreshBtn.classList.remove('spinning');
        }
    }
}

function showError(message) {
    console.error(message);
    // Could display a toast notification here
}

// Main data loading function
async function loadAllData() {
    if (state.isLoading) {
        console.log('Already loading data...');
        return;
    }
    
    state.isLoading = true;
    showLoading(true);
    
    try {
        await Promise.all([
            loadMetrics(),
            loadCharts(),
            loadTrades()
        ]);
        console.log('Data loaded successfully');
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to refresh dashboard data');
    } finally {
        state.isLoading = false;
        showLoading(false);
    }
}

// Auto-refresh functionality
let autoRefreshInterval = null;

function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    autoRefreshInterval = setInterval(loadAllData, CONFIG.AUTO_REFRESH_INTERVAL);
    console.log(`Auto-refresh started (${CONFIG.AUTO_REFRESH_INTERVAL / 1000}s interval)`);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        console.log('Auto-refresh stopped');
    }
}

// Page visibility handling
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        loadAllData();
        startAutoRefresh();
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initializing...');
    
    // Initialize theme
    initTheme();
    
    // Setup theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Load initial data
    loadAllData();
    
    // Start auto-refresh
    startAutoRefresh();
    
    console.log('Dashboard initialized successfully');
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
    Object.values(state.charts).forEach(chart => {
        if (chart) chart.destroy();
    });
});
