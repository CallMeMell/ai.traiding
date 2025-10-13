# 📊 Portfolio Optimization Guide

Umfassende Anleitung für Portfolio-Optimierung mit Modern Portfolio Theory (Markowitz).

---

## 📋 Inhaltsverzeichnis

1. [Überblick](#überblick)
2. [Installation](#installation)
3. [Markowitz-Optimierung](#markowitz-optimierung)
4. [Risk Parity](#risk-parity)
5. [Kelly Criterion](#kelly-criterion)
6. [Rebalancing](#rebalancing)
7. [Beispiele](#beispiele)

---

## Überblick

Das Portfolio-Optimierungs-System bietet:

- ✅ **Markowitz Mean-Variance Optimization** (Maximum Sharpe Ratio)
- ✅ **Minimum Volatility Portfolio**
- ✅ **Risk Parity Allocation**
- ✅ **Kelly Criterion Position Sizing**
- ✅ **Dynamic Rebalancing**
- ✅ **Efficient Frontier Berechnung**

### Theorie

**Modern Portfolio Theory (MPT)** von Harry Markowitz:
- Optimierung des Trade-offs zwischen Rendite und Risiko
- Diversifikation reduziert Portfolio-Volatilität
- Efficient Frontier: Set optimaler Portfolios

---

## Installation

```powershell
# Windows
.\venv\Scripts\python.exe -m pip install scipy scikit-learn matplotlib
```

---

## Markowitz-Optimierung

### Maximum Sharpe Ratio

Findet das Portfolio mit der besten risikobereinigten Rendite.

```python
from portfolio_optimizer import PortfolioOptimizer
import pandas as pd

# Preis-Daten laden
prices = pd.read_csv('data/portfolio_prices.csv', index_col=0, parse_dates=True)

# Optimizer erstellen
optimizer = PortfolioOptimizer(risk_free_rate=0.02)

# Returns und Covariance berechnen
returns = optimizer.calculate_returns(prices)
expected_returns = optimizer.calculate_expected_returns(returns)
cov_matrix = optimizer.calculate_covariance_matrix(returns)

# Optimieren für Max Sharpe
result = optimizer.maximize_sharpe_ratio(expected_returns, cov_matrix)

print(f"Expected Return: {result['expected_return']*100:.2f}%")
print(f"Volatility: {result['volatility']*100:.2f}%")
print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")

for asset, weight in result['weights'].items():
    print(f"{asset}: {weight*100:.1f}%")
```

### Minimum Volatility

Findet das Portfolio mit dem geringsten Risiko.

```python
result = optimizer.minimize_volatility(expected_returns, cov_matrix)

print(f"Minimum Volatility: {result['volatility']*100:.2f}%")
for asset, weight in result['weights'].items():
    print(f"{asset}: {weight*100:.1f}%")
```

### Mit Target Return

Portfolio mit minimalem Risiko für eine Ziel-Rendite.

```python
target_return = 0.15  # 15% jährlich

result = optimizer.minimize_volatility(
    expected_returns, 
    cov_matrix, 
    target_return=target_return
)

print(f"Target Return: {target_return*100:.0f}%")
print(f"Achieved Return: {result['expected_return']*100:.2f}%")
print(f"Volatility: {result['volatility']*100:.2f}%")
```

---

## Risk Parity

Allokation basierend auf gleichem Risiko-Beitrag jedes Assets.

```python
result = optimizer.risk_parity(cov_matrix)

print("Risk Parity Weights:")
for asset, weight in result['weights'].items():
    print(f"{asset}: {weight*100:.1f}%")
```

**Vorteile:**
- Kein Asset dominiert das Portfolio-Risiko
- Gut für diversifizierte Portfolios
- Weniger sensitiv gegenüber erwarteten Returns

**Anwendung:**
- Multi-Asset Portfolios (Aktien, Bonds, Commodities)
- Defensive Strategien
- Langfristige Investments

---

## Kelly Criterion

Optimale Position Size basierend auf Win Rate und Win/Loss Ratio.

```python
# Beispiel: 60% Win Rate, 2:1 Win/Loss Ratio
win_rate = 0.60
win_loss_ratio = 2.0

kelly = optimizer.kelly_criterion(win_rate, win_loss_ratio)
print(f"Optimal Position Size: {kelly*100:.1f}%")
```

### Praktische Anwendung

```python
# Basierend auf Backtest-Ergebnissen
def calculate_kelly_from_backtest(trades):
    """Kelly aus Trade-History berechnen"""
    wins = [t for t in trades if t['profit'] > 0]
    losses = [t for t in trades if t['profit'] < 0]
    
    win_rate = len(wins) / len(trades)
    
    avg_win = sum(t['profit'] for t in wins) / len(wins)
    avg_loss = abs(sum(t['profit'] for t in losses) / len(losses))
    win_loss_ratio = avg_win / avg_loss
    
    return optimizer.kelly_criterion(win_rate, win_loss_ratio)

# Kelly für eine Strategie
kelly_size = calculate_kelly_from_backtest(my_trades)
print(f"Empfohlene Position Size: {kelly_size*100:.1f}%")
```

**Warnung:** Kelly Criterion kann aggressiv sein. Half-Kelly (50% des Kelly-Werts) ist sicherer.

---

## Rebalancing

### Portfolio Drift erkennen

```python
from portfolio_optimizer import rebalance_portfolio

# Aktuelle Weights (durch Marktbewegung verändert)
current_weights = {
    'BTC': 0.45,
    'ETH': 0.30,
    'STOCK': 0.15,
    'BOND': 0.10
}

# Target Weights (von Optimierung)
target_weights = {
    'BTC': 0.40,
    'ETH': 0.30,
    'STOCK': 0.20,
    'BOND': 0.10
}

# Rebalancing-Trades berechnen
trades = rebalance_portfolio(
    current_weights, 
    target_weights, 
    threshold=0.05  # Nur rebalancen wenn >5% Abweichung
)

for asset, trade in trades.items():
    action = "BUY" if trade > 0 else "SELL"
    print(f"{action} {asset}: {abs(trade)*100:.1f}%")
```

### Dynamisches Rebalancing

```python
def dynamic_rebalance(prices, frequency='monthly'):
    """
    Periodisches Rebalancing mit Portfolio-Optimierung
    
    Args:
        prices: DataFrame mit Asset-Preisen
        frequency: 'daily', 'weekly', 'monthly'
    """
    optimizer = PortfolioOptimizer()
    
    # Initiales Portfolio optimieren
    returns = optimizer.calculate_returns(prices)
    expected_returns = optimizer.calculate_expected_returns(returns)
    cov_matrix = optimizer.calculate_covariance_matrix(returns)
    
    result = optimizer.maximize_sharpe_ratio(expected_returns, cov_matrix)
    target_weights = result['weights']
    
    # Portfolio-Wert tracken
    portfolio_values = []
    rebalance_dates = []
    
    # Simulation
    current_weights = target_weights.copy()
    
    for date in prices.index:
        # Rebalancing prüfen (z.B. monatlich)
        if should_rebalance(date, frequency):
            trades = rebalance_portfolio(current_weights, target_weights)
            if trades:
                # Rebalancing durchführen
                current_weights = target_weights.copy()
                rebalance_dates.append(date)
        
        # Portfolio-Wert berechnen
        portfolio_value = calculate_portfolio_value(current_weights, prices.loc[date])
        portfolio_values.append(portfolio_value)
    
    return portfolio_values, rebalance_dates
```

---

## Efficient Frontier

Visualisierung aller optimalen Risk/Return-Kombinationen.

```python
import matplotlib.pyplot as plt

# Efficient Frontier berechnen
frontier = optimizer.efficient_frontier(
    expected_returns, 
    cov_matrix, 
    n_points=50
)

# Plotten
plt.figure(figsize=(10, 6))
plt.plot(frontier['volatility']*100, frontier['return']*100, 'b-', linewidth=2)
plt.scatter(frontier['volatility']*100, frontier['return']*100, 
            c=frontier['sharpe'], cmap='viridis', s=50)
plt.colorbar(label='Sharpe Ratio')
plt.xlabel('Volatility (%)')
plt.ylabel('Expected Return (%)')
plt.title('Efficient Frontier')
plt.grid(True)
plt.show()
```

---

## Beispiele

### Multi-Asset Portfolio Optimierung

```python
import pandas as pd
from portfolio_optimizer import optimize_portfolio

# Preis-Daten für verschiedene Assets
prices = pd.DataFrame({
    'BTC': [...],
    'ETH': [...],
    'STOCK_INDEX': [...],
    'BOND_ETF': [...],
    'GOLD': [...]
})

# Optimieren
result = optimize_portfolio(prices, method='max_sharpe', risk_free_rate=0.02)

print("Optimal Portfolio:")
for asset, weight in result['weights'].items():
    print(f"  {asset}: {weight*100:.1f}%")

print(f"\nExpected Annual Return: {result['expected_return']*100:.1f}%")
print(f"Annual Volatility: {result['volatility']*100:.1f}%")
print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
```

### Strategie-basiertes Portfolio

```python
# Portfolio aus verschiedenen Trading-Strategien
strategies = {
    'Reversal': {'return': 0.25, 'volatility': 0.18},
    'Momentum': {'return': 0.30, 'volatility': 0.22},
    'Mean_Reversion': {'return': 0.15, 'volatility': 0.12},
    'Arbitrage': {'return': 0.08, 'volatility': 0.05}
}

# Correlation Matrix (geschätzt)
correlation = pd.DataFrame([
    [1.0, 0.3, -0.2, 0.0],
    [0.3, 1.0, -0.1, 0.0],
    [-0.2, -0.1, 1.0, 0.1],
    [0.0, 0.0, 0.1, 1.0]
], columns=strategies.keys(), index=strategies.keys())

# Covariance Matrix berechnen
volatilities = [s['volatility'] for s in strategies.values()]
cov_matrix = correlation * np.outer(volatilities, volatilities)

# Expected Returns
expected_returns = pd.Series({k: v['return'] for k, v in strategies.items()})

# Optimieren
optimizer = PortfolioOptimizer()
result = optimizer.maximize_sharpe_ratio(expected_returns, cov_matrix)

print("Optimal Strategy Allocation:")
for strategy, weight in result['weights'].items():
    print(f"  {strategy}: {weight*100:.1f}%")
```

---

## Best Practices

### 1. Datenqualität

```python
# Mindestens 1-2 Jahre historische Daten
assert len(prices) >= 252  # 1 Jahr Daily Data

# Keine fehlenden Werte
assert not prices.isnull().any().any()

# Konsistente Frequenz
assert prices.index.to_series().diff().mode()[0] == pd.Timedelta('1 day')
```

### 2. Constraints hinzufügen

```python
# Maximale Position Size begrenzen
constraints = [
    {'type': 'ineq', 'fun': lambda x: 0.30 - x[0]},  # Asset 0 max 30%
    {'type': 'ineq', 'fun': lambda x: 0.40 - x[1]}   # Asset 1 max 40%
]

result = optimizer.maximize_sharpe_ratio(
    expected_returns, 
    cov_matrix, 
    constraints=constraints
)
```

### 3. Walk-Forward Validation

```python
def walk_forward_optimization(prices, window=252, step=21):
    """Rolling window optimization"""
    results = []
    
    for i in range(0, len(prices) - window, step):
        # Training Window
        train_prices = prices.iloc[i:i+window]
        
        # Optimize
        result = optimize_portfolio(train_prices, method='max_sharpe')
        
        # Test auf nächster Periode
        test_prices = prices.iloc[i+window:i+window+step]
        test_return = calculate_portfolio_return(result['weights'], test_prices)
        
        results.append({
            'date': prices.index[i+window],
            'weights': result['weights'],
            'test_return': test_return
        })
    
    return results
```

### 4. Transaction Costs berücksichtigen

```python
def optimize_with_costs(prices, transaction_cost=0.001):
    """Optimierung mit Transaction Costs"""
    optimizer = PortfolioOptimizer()
    
    returns = optimizer.calculate_returns(prices)
    
    # Costs von Returns abziehen
    adjusted_returns = returns - transaction_cost
    
    expected_returns = adjusted_returns.mean() * 252
    cov_matrix = adjusted_returns.cov() * 252
    
    return optimizer.maximize_sharpe_ratio(expected_returns, cov_matrix)
```

---

## Troubleshooting

### Problem: Optimization schlägt fehl

**Lösung:**
- Mehr historische Daten verwenden
- Regularization der Covariance Matrix
- Constraints lockern

### Problem: Unrealistische Weights

**Lösung:**
```python
# Bounds setzen
bounds = tuple((0.05, 0.30) for _ in range(n_assets))  # Min 5%, Max 30%
```

### Problem: Zu häufiges Rebalancing

**Lösung:**
```python
# Höherer Threshold
trades = rebalance_portfolio(current, target, threshold=0.10)  # 10% statt 5%
```

---

## Weitere Ressourcen

- [SciPy Optimize Docs](https://docs.scipy.org/doc/scipy/reference/optimize.html)
- [Markowitz Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory)
- [Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion)
- [ROADMAP.md](ROADMAP.md)

---

**Made for Windows ⭐ | PowerShell-First | DRY_RUN Default**
