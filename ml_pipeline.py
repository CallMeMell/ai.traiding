"""
ml_pipeline.py - Machine Learning Pipeline
==========================================
TensorFlow/Keras ML pipeline for trading signal prediction.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import logging
import os
import json
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class TradingMLModel:
    """
    Machine Learning model for trading signal prediction
    
    Predicts BUY/SELL/HOLD signals based on technical indicators
    """
    
    def __init__(
        self,
        input_shape: Tuple[int],
        model_type: str = 'dense',
        model_dir: str = 'models/ml'
    ):
        """
        Initialize ML model
        
        Args:
            input_shape: Shape of input features
            model_type: 'dense', 'lstm', or 'cnn'
            model_dir: Directory to save models
        """
        self.input_shape = input_shape
        self.model_type = model_type
        self.model_dir = model_dir
        self.model = None
        self.scaler = StandardScaler()
        self.history = None
        
        os.makedirs(model_dir, exist_ok=True)
        
        logger.info(f"TradingMLModel initialized: {model_type}, input_shape={input_shape}")
    
    def build_dense_model(
        self,
        hidden_layers: List[int] = [64, 32, 16],
        dropout_rate: float = 0.2,
        activation: str = 'relu'
    ) -> keras.Model:
        """
        Build dense neural network
        
        Args:
            hidden_layers: List of hidden layer sizes
            dropout_rate: Dropout rate for regularization
            activation: Activation function
        
        Returns:
            Keras model
        """
        model = models.Sequential()
        
        # Input layer
        model.add(layers.Input(shape=self.input_shape))
        
        # Hidden layers
        for i, units in enumerate(hidden_layers):
            model.add(layers.Dense(units, activation=activation, name=f'dense_{i}'))
            model.add(layers.Dropout(dropout_rate, name=f'dropout_{i}'))
        
        # Output layer: 3 classes (BUY=0, HOLD=1, SELL=2)
        model.add(layers.Dense(3, activation='softmax', name='output'))
        
        return model
    
    def build_lstm_model(
        self,
        lstm_units: List[int] = [64, 32],
        dropout_rate: float = 0.2
    ) -> keras.Model:
        """
        Build LSTM model for time series
        
        Args:
            lstm_units: List of LSTM layer sizes
            dropout_rate: Dropout rate
        
        Returns:
            Keras model
        """
        model = models.Sequential()
        
        # Input layer
        model.add(layers.Input(shape=self.input_shape))
        
        # LSTM layers
        for i, units in enumerate(lstm_units[:-1]):
            model.add(layers.LSTM(
                units,
                return_sequences=True,
                name=f'lstm_{i}'
            ))
            model.add(layers.Dropout(dropout_rate, name=f'dropout_{i}'))
        
        # Last LSTM layer
        model.add(layers.LSTM(lstm_units[-1], name=f'lstm_{len(lstm_units)-1}'))
        model.add(layers.Dropout(dropout_rate, name=f'dropout_{len(lstm_units)}'))
        
        # Output layer
        model.add(layers.Dense(3, activation='softmax', name='output'))
        
        return model
    
    def build_cnn_model(
        self,
        filters: List[int] = [32, 64],
        kernel_size: int = 3,
        dropout_rate: float = 0.2
    ) -> keras.Model:
        """
        Build CNN model
        
        Args:
            filters: List of filter sizes
            kernel_size: Kernel size for convolution
            dropout_rate: Dropout rate
        
        Returns:
            Keras model
        """
        model = models.Sequential()
        
        # Input layer
        model.add(layers.Input(shape=self.input_shape))
        
        # CNN layers
        for i, n_filters in enumerate(filters):
            model.add(layers.Conv1D(
                n_filters,
                kernel_size,
                activation='relu',
                padding='same',
                name=f'conv_{i}'
            ))
            model.add(layers.MaxPooling1D(2, name=f'pool_{i}'))
            model.add(layers.Dropout(dropout_rate, name=f'dropout_{i}'))
        
        # Flatten and dense layers
        model.add(layers.Flatten(name='flatten'))
        model.add(layers.Dense(64, activation='relu', name='dense'))
        model.add(layers.Dropout(dropout_rate, name='dropout_final'))
        
        # Output layer
        model.add(layers.Dense(3, activation='softmax', name='output'))
        
        return model
    
    def build_model(self, **kwargs) -> keras.Model:
        """Build model based on model_type"""
        if self.model_type == 'dense':
            self.model = self.build_dense_model(**kwargs)
        elif self.model_type == 'lstm':
            self.model = self.build_lstm_model(**kwargs)
        elif self.model_type == 'cnn':
            self.model = self.build_cnn_model(**kwargs)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        logger.info(f"Model built: {self.model_type}")
        return self.model
    
    def compile_model(
        self,
        learning_rate: float = 0.001,
        optimizer: str = 'adam',
        loss: str = 'sparse_categorical_crossentropy',
        metrics: List[str] = ['accuracy']
    ):
        """
        Compile the model
        
        Args:
            learning_rate: Learning rate
            optimizer: Optimizer name
            loss: Loss function
            metrics: Metrics to track
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        if optimizer == 'adam':
            opt = keras.optimizers.Adam(learning_rate=learning_rate)
        elif optimizer == 'sgd':
            opt = keras.optimizers.SGD(learning_rate=learning_rate)
        else:
            opt = optimizer
        
        self.model.compile(
            optimizer=opt,
            loss=loss,
            metrics=metrics
        )
        
        logger.info("Model compiled")
    
    def prepare_data(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        validation_split: float = 0.1
    ) -> Tuple:
        """
        Prepare data for training
        
        Args:
            X: Input features
            y: Labels
            test_size: Test set proportion
            validation_split: Validation set proportion
        
        Returns:
            (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        # Split into train and test
        X_train_full, X_test, y_train_full, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Split train into train and validation
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_full, y_train_full, test_size=validation_split, random_state=42
        )
        
        # Fit scaler on training data
        if len(X_train.shape) == 2:
            self.scaler.fit(X_train)
            X_train = self.scaler.transform(X_train)
            X_val = self.scaler.transform(X_val)
            X_test = self.scaler.transform(X_test)
        else:
            # For 3D data (LSTM/CNN), scale per sample
            original_shape = X_train.shape
            X_train_2d = X_train.reshape(-1, X_train.shape[-1])
            self.scaler.fit(X_train_2d)
            
            X_train = self.scaler.transform(X_train_2d).reshape(original_shape)
            X_val = self.scaler.transform(X_val.reshape(-1, X_val.shape[-1])).reshape(X_val.shape)
            X_test = self.scaler.transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)
        
        logger.info(f"Data prepared: train={X_train.shape}, val={X_val.shape}, test={X_test.shape}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        epochs: int = 50,
        batch_size: int = 32,
        callbacks: Optional[List] = None,
        verbose: int = 1
    ) -> Dict[str, Any]:
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            epochs: Number of epochs
            batch_size: Batch size
            callbacks: Keras callbacks
            verbose: Verbosity level
        
        Returns:
            Training history
        """
        if self.model is None:
            raise ValueError("Model not compiled")
        
        # Default callbacks
        if callbacks is None:
            callbacks = [
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-7
                )
            ]
        
        # Prepare validation data
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
        
        logger.info(f"Training for {epochs} epochs...")
        
        # Train
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose
        )
        
        logger.info("Training completed")
        
        return self.history.history
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate the model
        
        Args:
            X_test: Test features
            y_test: Test labels
        
        Returns:
            Evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        loss, accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        
        # Make predictions
        y_pred_probs = self.model.predict(X_test, verbose=0)
        y_pred = np.argmax(y_pred_probs, axis=1)
        
        # Calculate additional metrics
        from sklearn.metrics import classification_report, confusion_matrix
        
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred, target_names=['BUY', 'HOLD', 'SELL']))
        
        return {
            'loss': loss,
            'accuracy': accuracy,
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Input features
        
        Returns:
            Predicted class (0=BUY, 1=HOLD, 2=SELL)
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        # Scale input
        if len(X.shape) == 2:
            X_scaled = self.scaler.transform(X)
        else:
            original_shape = X.shape
            X_scaled = self.scaler.transform(X.reshape(-1, X.shape[-1])).reshape(original_shape)
        
        # Predict
        predictions = self.model.predict(X_scaled, verbose=0)
        return np.argmax(predictions, axis=1)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        if self.model is None:
            raise ValueError("Model not trained")
        
        # Scale input
        if len(X.shape) == 2:
            X_scaled = self.scaler.transform(X)
        else:
            original_shape = X.shape
            X_scaled = self.scaler.transform(X.reshape(-1, X.shape[-1])).reshape(original_shape)
        
        return self.model.predict(X_scaled, verbose=0)
    
    def save_model(self, name: str = 'model'):
        """Save the model"""
        if self.model is None:
            raise ValueError("No model to save")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_name = f"{self.model_type}_{name}_{timestamp}"
        
        # Save model
        model_path = os.path.join(self.model_dir, f"{model_name}.h5")
        self.model.save(model_path)
        
        # Save scaler
        import joblib
        scaler_path = os.path.join(self.model_dir, f"{model_name}_scaler.pkl")
        joblib.dump(self.scaler, scaler_path)
        
        # Save metadata
        metadata = {
            'model_type': self.model_type,
            'input_shape': self.input_shape,
            'timestamp': timestamp
        }
        metadata_path = os.path.join(self.model_dir, f"{model_name}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Model saved: {model_path}")
        
        return model_path
    
    def load_model(self, model_path: str):
        """Load a saved model"""
        import joblib
        
        self.model = keras.models.load_model(model_path)
        
        # Load scaler
        scaler_path = model_path.replace('.h5', '_scaler.pkl')
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
        
        logger.info(f"Model loaded: {model_path}")
        
        return self.model
