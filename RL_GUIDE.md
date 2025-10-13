# 🤖 Reinforcement Learning Trading Guide

Umfassende Anleitung für Reinforcement Learning (RL) im Trading mit DQN und PPO.

---

## 📋 Inhaltsverzeichnis

1. [Überblick](#überblick)
2. [Installation](#installation)
3. [RL Environment](#rl-environment)
4. [Training von Agenten](#training-von-agenten)
5. [Hyperparameter-Tuning](#hyperparameter-tuning)
6. [Deployment](#deployment)
7. [Best Practices](#best-practices)

---

## Überblick

Das Reinforcement Learning (RL) System ermöglicht:

- ✅ **Gym-kompatibles Trading Environment** für RL-Training
- ✅ **DQN und PPO Algorithmen** mit Stable-Baselines3
- ✅ **Hyperparameter-Tuning** mit Optuna
- ✅ **Model Persistence** (Speichern/Laden von Modellen)
- ✅ **Performance Metriken** (ROI, Sharpe Ratio, Drawdown)

### Architektur

```
┌─────────────────────────────────────────────────────┐
│              TradingEnvironment (Gym)               │
│  State: Prices, Indicators, Position, Capital       │
│  Actions: BUY/SELL/HOLD with quantities             │
│  Reward: P&L + Sharpe Bonus - Drawdown Penalty     │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                  RL Agent (DQN/PPO)                 │
│  Training: Stable-Baselines3                        │
│  Evaluation: Backtesting on historical data         │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│            Hyperparameter Tuning (Optuna)           │
│  Optimization: Learning rate, batch size, etc.      │
└─────────────────────────────────────────────────────┘
```

---

## Installation

### Abhängigkeiten installieren

```powershell
# Windows (PowerShell)
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Oder einzeln:
.\venv\Scripts\python.exe -m pip install gym stable-baselines3 optuna tensorflow
```

### Verifikation

```powershell
.\venv\Scripts\python.exe -c "import gym; import stable_baselines3; print('RL dependencies OK')"
```

---

## RL Environment

### Environment erstellen

```python
from rl_environment import TradingEnvironment
import pandas as pd

# Daten laden (mit OHLCV und Indikatoren)
data = pd.read_csv('data/BTC_historical.csv')

# Environment erstellen
env = TradingEnvironment(
    data=data,
    initial_capital=10000.0,
    commission_rate=0.001,  # 0.1% Gebühren
    window_size=30          # 30 Kerzen als State
)
```

### State Space

Der State enthält:
- **Historische Preise** (normalisiert, window_size Kerzen)
- **Technische Indikatoren** (RSI, MA, Volume, etc.)
- **Portfolio Status** (Position, Capital, Holdings)

Shape: `(window_size * n_features + 3,)`

### Action Space

21 diskrete Aktionen:
- **0-9**: BUY 10%, 20%, ..., 100%
- **10**: HOLD (keine Aktion)
- **11-20**: SELL 10%, 20%, ..., 100%

### Reward Function

```
Reward = Portfolio Return + Sharpe Bonus - Drawdown Penalty

Portfolio Return: (current_value - previous_value) / previous_value
Sharpe Bonus: Mean return / Std return * 0.1
Drawdown Penalty: -((max_value - current_value) / max_value) * 0.5
```

---

## Training von Agenten

### PPO Agent trainieren

```python
from rl_agent import train_rl_agent
import pandas as pd

# Daten vorbereiten
train_data = pd.read_csv('data/train.csv')
eval_data = pd.read_csv('data/eval.csv')

# Agent trainieren
agent = train_rl_agent(
    algorithm='PPO',
    train_data=train_data,
    eval_data=eval_data,
    initial_capital=10000.0,
    total_timesteps=100000,
    model_dir='models/rl'
)

# Evaluieren
metrics = agent.evaluate(eval_env, n_episodes=10)
print(f"Mean ROI: {metrics['mean_roi']:.2f}%")
```

### DQN Agent trainieren

```python
from rl_agent import RLAgent
from rl_environment import TradingEnvironment

# Environment erstellen
env = TradingEnvironment(train_data, initial_capital=10000.0)

# DQN Agent
agent = RLAgent(algorithm='DQN', env=env)
agent.create_model(
    learning_rate=0.0001,
    buffer_size=100000,
    batch_size=32
)

# Trainieren
agent.train(total_timesteps=100000)

# Speichern
agent.save_model('my_dqn_model')
```

### Modell laden und verwenden

```python
from rl_agent import RLAgent

# Modell laden
agent = RLAgent(algorithm='PPO')
agent.load_model('models/rl/PPO_my_model_20241013.zip')

# Vorhersage machen
obs = env.reset()
action, _ = agent.predict(obs, deterministic=True)
```

---

## Hyperparameter-Tuning

### Mit Optuna optimieren

```python
from hyperparameter_tuning import tune_rl_agent

# Hyperparameter optimieren
results = tune_rl_agent(
    algorithm='PPO',
    train_data=train_data,
    eval_data=eval_data,
    study_name='ppo_tuning',
    n_trials=50,
    training_timesteps=50000
)

print(f"Best parameters: {results['best_params']}")
print(f"Best ROI: {results['best_value']:.2f}%")
```

### Manuelle Hyperparameter-Suche

```python
from hyperparameter_tuning import HyperparameterTuner

tuner = HyperparameterTuner(
    study_name='custom_tuning',
    direction='maximize'
)

results = tuner.optimize(
    objective_func=tuner.objective_rl_agent,
    n_trials=30,
    algorithm='PPO',
    train_data=train_data,
    eval_data=eval_data
)

# Ergebnisse speichern
tuner.save_results('models/tuning/results.json')
tuner.plot_optimization_history('models/tuning/history.png')
```

---

## Deployment

### Flask API starten

```powershell
# Windows
.\venv\Scripts\python.exe ml_api.py
```

### Modell über API laden

```python
import requests

# Modell laden
response = requests.post('http://localhost:5001/api/rl/load', json={
    'agent_name': 'my_ppo_agent',
    'model_path': 'models/rl/PPO_model_20241013',
    'algorithm': 'PPO'
})

print(response.json())
```

### Prediction über API

```python
# Prediction anfragen
response = requests.post('http://localhost:5001/api/rl/predict', json={
    'agent_name': 'my_ppo_agent',
    'observation': [0.5, 0.3, ...]  # Ihr State
})

result = response.json()
print(f"Action: {result['action_type']}")
print(f"Amount: {result['action_amount']}")
```

---

## Best Practices

### 1. Daten-Vorbereitung

```python
# Indikatoren hinzufügen
def prepare_data(df):
    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss))
    
    # Moving Averages
    df['ma_short'] = df['close'].rolling(10).mean()
    df['ma_long'] = df['close'].rolling(30).mean()
    
    # Volume
    df['volume_ma'] = df['volume'].rolling(20).mean()
    
    return df.fillna(method='bfill')
```

### 2. Train/Test Split

```python
# 80/20 Split
split_idx = int(len(data) * 0.8)
train_data = data[:split_idx]
test_data = data[split_idx:]
```

### 3. Monitoring während Training

```python
from stable_baselines3.common.callbacks import EvalCallback

eval_callback = EvalCallback(
    eval_env,
    best_model_save_path='models/best',
    log_path='logs/',
    eval_freq=10000,
    deterministic=True,
    render=False
)

agent.train(total_timesteps=100000, callback=eval_callback)
```

### 4. Hyperparameter Empfehlungen

**PPO:**
```python
{
    'learning_rate': 0.0003,
    'n_steps': 2048,
    'batch_size': 64,
    'n_epochs': 10,
    'gamma': 0.99,
    'gae_lambda': 0.95,
    'clip_range': 0.2
}
```

**DQN:**
```python
{
    'learning_rate': 0.0001,
    'buffer_size': 100000,
    'batch_size': 32,
    'gamma': 0.99,
    'exploration_fraction': 0.1,
    'exploration_final_eps': 0.01
}
```

### 5. Performance-Optimierung

- **Weniger Features**: Nur relevante Indikatoren verwenden
- **Kürzere Window Size**: 20-30 Kerzen reichen meist
- **Batch Size erhöhen**: Schnelleres Training
- **GPU nutzen**: `device='cuda'` für TensorFlow

---

## Troubleshooting

### Problem: Training ist langsam

**Lösung:**
```python
# Weniger Timesteps pro Trial
training_timesteps = 10000  # Statt 100000

# Größere Batch Size
batch_size = 128  # Statt 32
```

### Problem: Agent lernt nicht

**Lösung:**
- Reward Function anpassen
- Learning Rate erhöhen/verringern
- Mehr Training Steps
- Bessere Feature Engineering

### Problem: Overfitting

**Lösung:**
- Mehr Training Data
- Regularization (Dropout, etc.)
- Walk-Forward Validation
- Ensemble von Modellen

---

## Beispiele

### Vollständiges Training Script

```python
from rl_environment import TradingEnvironment
from rl_agent import RLAgent
import pandas as pd

# Daten laden
data = pd.read_csv('data/historical.csv')
data = prepare_data(data)

# Split
split = int(len(data) * 0.8)
train_data = data[:split]
test_data = data[split:]

# Environment
train_env = TradingEnvironment(train_data, initial_capital=10000)
test_env = TradingEnvironment(test_data, initial_capital=10000)

# Agent
agent = RLAgent(algorithm='PPO', env=train_env)
agent.create_model()

# Training
agent.train(
    total_timesteps=100000,
    eval_env=test_env,
    eval_freq=10000
)

# Evaluation
metrics = agent.evaluate(test_env, n_episodes=10)
print(f"Test ROI: {metrics['mean_roi']:.2f}%")
print(f"Test Sharpe: {metrics['mean_sharpe']:.2f}")

# Speichern
agent.save_model('final_model')
```

---

## Weitere Ressourcen

- [Stable-Baselines3 Docs](https://stable-baselines3.readthedocs.io/)
- [OpenAI Gym Docs](https://www.gymlibrary.dev/)
- [Optuna Docs](https://optuna.readthedocs.io/)
- [ROADMAP.md](ROADMAP.md) - Projekt Roadmap

---

**Made for Windows ⭐ | PowerShell-First | DRY_RUN Default**
