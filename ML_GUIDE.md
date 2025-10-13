# 🧠 Machine Learning Guide

Anleitung für ML-Modelle im Trading (TensorFlow/Keras).

---

## 📋 Überblick

ML-System Features:
- ✅ **Signal Prediction** (BUY/HOLD/SELL)
- ✅ **Multiple Model Types** (Dense, LSTM, CNN)
- ✅ **Model Training & Evaluation**
- ✅ **Model Versioning & Persistence**
- ✅ **Flask API Deployment**

---

## Installation

```powershell
.\venv\Scripts\python.exe -m pip install tensorflow scikit-learn joblib
```

---

## Quick Start

### Modell erstellen und trainieren

```python
from ml_pipeline import TradingMLModel
import numpy as np

# Sample Data (Features: [RSI, MA_Short, MA_Long, Volume, ...])
X_train = np.random.rand(1000, 10)
y_train = np.random.randint(0, 3, 1000)  # 0=BUY, 1=HOLD, 2=SELL

# Modell erstellen
model = TradingMLModel(input_shape=(10,), model_type='dense')
model.build_model(hidden_layers=[64, 32], dropout_rate=0.2)
model.compile_model(learning_rate=0.001)

# Daten vorbereiten
X_train, X_val, X_test, y_train, y_val, y_test = model.prepare_data(
    X_train, y_train, test_size=0.2
)

# Trainieren
history = model.train(X_train, y_train, X_val, y_val, epochs=50)

# Evaluieren
metrics = model.evaluate(X_test, y_test)
print(f"Accuracy: {metrics['accuracy']:.2%}")

# Speichern
model.save_model('my_trading_model')
```

---

## Model Types

### 1. Dense (Feed-Forward)

Für unabhängige Features.

```python
model = TradingMLModel(input_shape=(n_features,), model_type='dense')
model.build_model(
    hidden_layers=[128, 64, 32],
    dropout_rate=0.3,
    activation='relu'
)
```

### 2. LSTM (Time Series)

Für sequenzielle Daten.

```python
# Input Shape: (timesteps, features)
model = TradingMLModel(input_shape=(30, 5), model_type='lstm')
model.build_lstm_model(
    lstm_units=[64, 32],
    dropout_rate=0.2
)
```

### 3. CNN (Patterns)

Für Pattern Recognition.

```python
model = TradingMLModel(input_shape=(window_size, n_features), model_type='cnn')
model.build_cnn_model(
    filters=[32, 64],
    kernel_size=3,
    dropout_rate=0.2
)
```

---

## Flask API

### API starten

```powershell
.\venv\Scripts\python.exe ml_api.py
```

### Modell laden

```python
import requests

response = requests.post('http://localhost:5001/api/ml/load', json={
    'model_name': 'my_model',
    'model_path': 'models/ml/dense_model_20241013.h5'
})
```

### Predictions

```python
response = requests.post('http://localhost:5001/api/ml/predict', json={
    'model_name': 'my_model',
    'features': [[0.5, 0.3, 0.7, ...]]
})

result = response.json()
print(f"Signal: {result['predictions'][0]}")  # BUY/HOLD/SELL
```

---

## Best Practices

### Feature Engineering

```python
def create_features(df):
    """Technische Indikatoren als Features"""
    # Price-based
    df['returns'] = df['close'].pct_change()
    df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
    
    # Momentum
    df['rsi'] = calculate_rsi(df['close'], 14)
    df['macd'] = calculate_macd(df['close'])
    
    # Trend
    df['ma_short'] = df['close'].rolling(10).mean()
    df['ma_long'] = df['close'].rolling(30).mean()
    df['ma_ratio'] = df['ma_short'] / df['ma_long']
    
    # Volatility
    df['bb_upper'], df['bb_lower'] = calculate_bollinger_bands(df['close'])
    df['atr'] = calculate_atr(df)
    
    return df.dropna()
```

### Label Creation

```python
def create_labels(df, forward_window=5, threshold=0.02):
    """Future return-based labels"""
    future_returns = df['close'].shift(-forward_window) / df['close'] - 1
    
    labels = np.where(future_returns > threshold, 0,  # BUY
                     np.where(future_returns < -threshold, 2,  # SELL
                             1))  # HOLD
    
    return labels[:-forward_window]
```

---

## Weitere Infos

Siehe auch:
- [RL_GUIDE.md](RL_GUIDE.md) - Reinforcement Learning
- [PORTFOLIO_OPTIMIZATION_GUIDE.md](PORTFOLIO_OPTIMIZATION_GUIDE.md)

---

**Made for Windows ⭐ | PowerShell-First | DRY_RUN Default**
