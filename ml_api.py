"""
ml_api.py - Flask API for ML Model Deployment
=============================================
RESTful API for serving trained ML models and RL agents.
"""

from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import logging
import os
from typing import Dict, Any
import json

from ml_pipeline import TradingMLModel
from rl_agent import RLAgent
from rl_environment import TradingEnvironment

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ml-api-secret-change-in-production')

# Global model storage
loaded_models = {
    'ml': {},
    'rl': {}
}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'ml_models_loaded': len(loaded_models['ml']),
        'rl_models_loaded': len(loaded_models['rl'])
    })


@app.route('/api/ml/load', methods=['POST'])
def load_ml_model():
    """
    Load an ML model
    
    Request body:
    {
        "model_name": "my_model",
        "model_path": "models/ml/model.h5"
    }
    """
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        model_path = data.get('model_path')
        
        if not model_name or not model_path:
            return jsonify({'error': 'model_name and model_path required'}), 400
        
        if not os.path.exists(model_path):
            return jsonify({'error': 'Model file not found'}), 404
        
        # Load model
        ml_model = TradingMLModel(input_shape=(10,))  # Placeholder
        ml_model.load_model(model_path)
        
        loaded_models['ml'][model_name] = ml_model
        
        logger.info(f"ML model loaded: {model_name}")
        
        return jsonify({
            'status': 'success',
            'model_name': model_name,
            'model_path': model_path
        })
    
    except Exception as e:
        logger.error(f"Error loading ML model: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ml/predict', methods=['POST'])
def predict_ml():
    """
    Make predictions with ML model
    
    Request body:
    {
        "model_name": "my_model",
        "features": [[1.0, 2.0, ...]]
    }
    """
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        features = data.get('features')
        
        if not model_name or features is None:
            return jsonify({'error': 'model_name and features required'}), 400
        
        if model_name not in loaded_models['ml']:
            return jsonify({'error': 'Model not loaded'}), 404
        
        # Get model
        model = loaded_models['ml'][model_name]
        
        # Convert to numpy array
        X = np.array(features)
        
        # Predict
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)
        
        # Convert to list
        predictions_list = predictions.tolist()
        probabilities_list = probabilities.tolist()
        
        # Map predictions to labels
        labels = ['BUY', 'HOLD', 'SELL']
        predicted_labels = [labels[p] for p in predictions]
        
        return jsonify({
            'status': 'success',
            'predictions': predicted_labels,
            'probabilities': probabilities_list,
            'raw_predictions': predictions_list
        })
    
    except Exception as e:
        logger.error(f"Error making predictions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rl/load', methods=['POST'])
def load_rl_agent():
    """
    Load an RL agent
    
    Request body:
    {
        "agent_name": "my_agent",
        "model_path": "models/rl/PPO_model_20241013.zip",
        "algorithm": "PPO"
    }
    """
    try:
        data = request.get_json()
        agent_name = data.get('agent_name')
        model_path = data.get('model_path')
        algorithm = data.get('algorithm', 'PPO')
        
        if not agent_name or not model_path:
            return jsonify({'error': 'agent_name and model_path required'}), 400
        
        # Load agent
        agent = RLAgent(algorithm=algorithm)
        agent.load_model(model_path)
        
        loaded_models['rl'][agent_name] = agent
        
        logger.info(f"RL agent loaded: {agent_name}")
        
        return jsonify({
            'status': 'success',
            'agent_name': agent_name,
            'algorithm': algorithm
        })
    
    except Exception as e:
        logger.error(f"Error loading RL agent: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rl/predict', methods=['POST'])
def predict_rl():
    """
    Get action from RL agent
    
    Request body:
    {
        "agent_name": "my_agent",
        "observation": [...]
    }
    """
    try:
        data = request.get_json()
        agent_name = data.get('agent_name')
        observation = data.get('observation')
        
        if not agent_name or observation is None:
            return jsonify({'error': 'agent_name and observation required'}), 400
        
        if agent_name not in loaded_models['rl']:
            return jsonify({'error': 'Agent not loaded'}), 404
        
        # Get agent
        agent = loaded_models['rl'][agent_name]
        
        # Convert to numpy array
        obs = np.array(observation, dtype=np.float32)
        
        # Predict
        action, _ = agent.predict(obs, deterministic=True)
        
        # Decode action
        if action < 10:
            action_type = 'BUY'
            action_amount = (action + 1) * 0.1
        elif action == 10:
            action_type = 'HOLD'
            action_amount = 0.0
        else:
            action_type = 'SELL'
            action_amount = (action - 10) * 0.1
        
        return jsonify({
            'status': 'success',
            'action': int(action),
            'action_type': action_type,
            'action_amount': float(action_amount)
        })
    
    except Exception as e:
        logger.error(f"Error getting RL action: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models/list', methods=['GET'])
def list_models():
    """List all loaded models"""
    return jsonify({
        'ml_models': list(loaded_models['ml'].keys()),
        'rl_models': list(loaded_models['rl'].keys())
    })


@app.route('/api/models/unload', methods=['POST'])
def unload_model():
    """
    Unload a model
    
    Request body:
    {
        "model_type": "ml" or "rl",
        "model_name": "my_model"
    }
    """
    try:
        data = request.get_json()
        model_type = data.get('model_type')
        model_name = data.get('model_name')
        
        if not model_type or not model_name:
            return jsonify({'error': 'model_type and model_name required'}), 400
        
        if model_type not in ['ml', 'rl']:
            return jsonify({'error': 'model_type must be "ml" or "rl"'}), 400
        
        if model_name in loaded_models[model_type]:
            del loaded_models[model_type][model_name]
            logger.info(f"Model unloaded: {model_name}")
            return jsonify({'status': 'success', 'message': f'Model {model_name} unloaded'})
        else:
            return jsonify({'error': 'Model not found'}), 404
    
    except Exception as e:
        logger.error(f"Error unloading model: {e}")
        return jsonify({'error': str(e)}), 500


def start_api(host: str = '0.0.0.0', port: int = 5001, debug: bool = False):
    """
    Start the Flask API server
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    print("=" * 70)
    print("🤖 ML/RL API Server Starting...")
    print("=" * 70)
    print(f"🚀 Server running on: http://{host}:{port}")
    print(f"📊 Health check: http://{host}:{port}/health")
    print("=" * 70)
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get port from environment or use default
    port = int(os.environ.get('ML_API_PORT', 5001))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    start_api(port=port, debug=debug)
