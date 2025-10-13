# 🤖 Machine Learning & Reinforcement Learning Features

Umfassende ML/RL-Integration für den KI-Trading-Bot.

---

## 🎯 Quick Start

### Installation

```powershell
# Windows (PowerShell)
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Demo ausführen

```powershell
# RL Training Demo
.\scripts\demo_rl.ps1

# Portfolio Optimization Demo
.\scripts\demo_portfolio.ps1

# ML API starten
.\scripts\start_ml_api.ps1
```

---

## 📁 Projekt-Struktur

```
ai.traiding/
├── rl_environment.py          # OpenAI Gym Trading Environment
├── rl_agent.py                # DQN/PPO Agent Wrapper
├── hyperparameter_tuning.py   # Optuna Hyperparameter Tuning
├── portfolio_optimizer.py     # Portfolio Optimization (Markowitz)
├── ml_pipeline.py             # TensorFlow/Keras ML Models
├── ml_api.py                  # Flask API für Model Deployment
│
├── tests/
│   ├── test_rl_environment.py     # RL Environment Tests
│   └── test_portfolio_optimizer.py # Portfolio Tests
│
├── docs/
│   ├── RL_GUIDE.md                # RL Dokumentation
│   ├── ML_GUIDE.md                # ML Dokumentation
│   └── PORTFOLIO_OPTIMIZATION_GUIDE.md
│
├── demos/
│   ├── demo_rl_training.py        # RL Training Demos
│   └── demo_portfolio_optimization.py
│
└── scripts/
    ├── demo_rl.ps1                # RL Demo Script (Windows)
    ├── demo_portfolio.ps1         # Portfolio Demo Script
    └── start_ml_api.ps1           # ML API Start Script
```

---

## 🚀 Features

### 1. Reinforcement Learning

**Environment:**
- ✅ Gym-kompatible Trading-Umgebung
- ✅ State: Preise, Indikatoren, Position, Kapital
- ✅ Actions: BUY/SELL/HOLD mit Mengen
- ✅ Reward: P&L + Sharpe - Drawdown

**Algorithmen:**
- ✅ Deep Q-Network (DQN)
- ✅ Proximal Policy Optimization (PPO)

**Training:**
```python
from rl_agent import train_rl_agent

agent = train_rl_agent(
    algorithm='PPO',
    train_data=data,
    total_timesteps=100000
)
```

**Dokumentation:** [RL_GUIDE.md](RL_GUIDE.md)

---

### 2. Hyperparameter Tuning

**Optuna Integration:**
- ✅ Bayesian Optimization
- ✅ Automatische Hyperparameter-Suche
- ✅ Visualization & Result Persistence

**Beispiel:**
```python
from hyperparameter_tuning import tune_rl_agent

results = tune_rl_agent(
    algorithm='PPO',
    train_data=train_data,
    eval_data=eval_data,
    n_trials=50
)

print(f"Best parameters: {results['best_params']}")
```

---

### 3. Portfolio Optimization

**Methoden:**
- ✅ Markowitz (Maximum Sharpe Ratio)
- ✅ Minimum Volatility
- ✅ Risk Parity
- ✅ Kelly Criterion
- ✅ Dynamic Rebalancing

**Beispiel:**
```python
from portfolio_optimizer import optimize_portfolio

result = optimize_portfolio(
    prices,
    method='max_sharpe',
    risk_free_rate=0.02
)

for asset, weight in result['weights'].items():
    print(f"{asset}: {weight*100:.1f}%")
```

**Dokumentation:** [PORTFOLIO_OPTIMIZATION_GUIDE.md](PORTFOLIO_OPTIMIZATION_GUIDE.md)

---

### 4. ML Pipeline

**Model Types:**
- ✅ Dense (Feed-Forward)
- ✅ LSTM (Time Series)
- ✅ CNN (Pattern Recognition)

**Features:**
- ✅ Signal Prediction (BUY/HOLD/SELL)
- ✅ Model Versioning
- ✅ StandardScaler Integration

**Beispiel:**
```python
from ml_pipeline import TradingMLModel

model = TradingMLModel(input_shape=(10,), model_type='dense')
model.build_model()
model.compile_model()

history = model.train(X_train, y_train, X_val, y_val)
model.save_model('my_model')
```

**Dokumentation:** [ML_GUIDE.md](ML_GUIDE.md)

---

### 5. Flask API

**Endpoints:**
- `GET /health` - Health Check
- `POST /api/ml/load` - ML Modell laden
- `POST /api/ml/predict` - ML Prediction
- `POST /api/rl/load` - RL Agent laden
- `POST /api/rl/predict` - RL Action abrufen
- `GET /api/models/list` - Alle Modelle auflisten

**Starten:**
```powershell
.\scripts\start_ml_api.ps1
```

**Nutzung:**
```python
import requests

# Modell laden
requests.post('http://localhost:5001/api/ml/load', json={
    'model_name': 'my_model',
    'model_path': 'models/ml/model.h5'
})

# Prediction
response = requests.post('http://localhost:5001/api/ml/predict', json={
    'model_name': 'my_model',
    'features': [[0.5, 0.3, ...]]
})
```

---

## 📊 Performance

### Tests

```powershell
# Alle ML/RL Tests ausführen
.\venv\Scripts\python.exe -m pytest tests/test_rl_environment.py -v
.\venv\Scripts\python.exe -m pytest tests/test_portfolio_optimizer.py -v
```

**Test Results:**
- ✅ RL Environment: 9/9 Tests passing
- ✅ Portfolio Optimizer: 11/11 Tests passing

---

## 🎓 Lernressourcen

### Dokumentation
- [RL_GUIDE.md](RL_GUIDE.md) - Reinforcement Learning Guide
- [ML_GUIDE.md](ML_GUIDE.md) - Machine Learning Guide
- [PORTFOLIO_OPTIMIZATION_GUIDE.md](PORTFOLIO_OPTIMIZATION_GUIDE.md) - Portfolio Theory

### Externe Ressourcen
- [Stable-Baselines3 Docs](https://stable-baselines3.readthedocs.io/)
- [OpenAI Gym](https://www.gymlibrary.dev/)
- [Optuna](https://optuna.readthedocs.io/)
- [TensorFlow](https://www.tensorflow.org/)

---

## 🔧 Troubleshooting

### Import Fehler

```powershell
# Dependencies neu installieren
.\venv\Scripts\python.exe -m pip install -r requirements.txt --upgrade
```

### API startet nicht

```powershell
# Port prüfen
netstat -ano | findstr :5001

# Anderen Port verwenden
$env:ML_API_PORT = "5002"
.\scripts\start_ml_api.ps1
```

### Training langsam

```python
# GPU nutzen (falls verfügbar)
import tensorflow as tf
print(f"GPUs available: {len(tf.config.list_physical_devices('GPU'))}")

# Batch Size erhöhen
agent.create_model(batch_size=128)  # statt 32
```

---

## 🚀 Nächste Schritte

1. **Eigene Daten verwenden:**
   - Historische Preis-Daten laden
   - Indikatoren berechnen
   - Features vorbereiten

2. **Modelle trainieren:**
   - RL Agent für Trading-Strategie
   - ML Modell für Signal-Prediction
   - Portfolio-Optimierung durchführen

3. **Hyperparameter optimieren:**
   - Optuna-Tuning durchführen
   - Beste Parameter speichern
   - Walk-Forward Validation

4. **Deployment:**
   - Models über Flask API bereitstellen
   - Integration in Live-Trading
   - Monitoring & Logging

---

## 📝 Acceptance Criteria (Erfüllt)

- [x] RL-Umgebung ist einsatzbereit
- [x] DQN/PPO-Modelle trainiert und gespeichert
- [x] Optuna-Tuning implementiert
- [x] Portfolio-Optimierung für mehrere Assets
- [x] ML-Modell Deployment über API
- [x] Alle Komponenten getestet
- [x] Dokumentation vollständig

---

## 🙏 Contributing

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

---

**Made for Windows ⭐ | PowerShell-First | DRY_RUN Default**
