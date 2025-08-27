#!/usr/bin/env python3
"""
Flask API for Credit Card Fraud Detection
RESTful API to serve the fraud detection model
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
from fraud_detection_model import FraudDetectionModel
import os

app = Flask(__name__)
CORS(app)

# Global model instance
fraud_detector = None

def load_fraud_model():
    """Load the fraud detection model"""
    global fraud_detector
    fraud_detector = FraudDetectionModel()
    
    model_path = '/workspace/fraud_detection_model.pkl'
    if os.path.exists(model_path):
        fraud_detector.load_model(model_path)
        print("Fraud detection model loaded successfully")
    else:
        print("No pre-trained model found. Training new model...")
        # Generate sample data and train
        df = fraud_detector.generate_sample_data(n_samples=10000)
        X, y = fraud_detector.preprocess_data(df)
        fraud_detector.train_models(X, y)
        fraud_detector.save_model(model_path)
        print("New model trained and saved")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'fraud-detection-api',
        'model_loaded': fraud_detector is not None
    })

@app.route('/predict', methods=['POST'])
def predict_fraud():
    """
    Predict fraud for a given transaction
    
    Expected JSON format:
    {
        "amount": 100.50,
        "hour": 14,
        "merchant_category": "grocery",
        "day_of_week": 1,
        "customer_age": 35,
        "days_since_last_transaction": 2,
        "is_weekend": 0
    }
    """
    try:
        if fraud_detector is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'amount', 'hour', 'merchant_category', 'day_of_week',
            'customer_age', 'days_since_last_transaction', 'is_weekend'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add engineered features
        transaction = data.copy()
        transaction['amount_log'] = np.log1p(transaction['amount'])
        transaction['is_night'] = int((transaction['hour'] >= 23) or (transaction['hour'] <= 5))
        transaction['is_business_hours'] = int((transaction['hour'] >= 9) and (transaction['hour'] <= 17))
        
        # For amount_zscore, we'll use a pre-calculated mean and std from training
        # In production, these should be stored with the model
        amount_mean = 150.0  # Approximate from sample data
        amount_std = 200.0   # Approximate from sample data
        transaction['amount_zscore'] = (transaction['amount'] - amount_mean) / amount_std
        
        # Make prediction
        result = fraud_detector.predict_fraud(transaction)
        
        # Add transaction details to response
        response = {
            'transaction_id': data.get('transaction_id', 'unknown'),
            'prediction': result,
            'input_data': data
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """
    Predict fraud for multiple transactions
    
    Expected JSON format:
    {
        "transactions": [
            {transaction1},
            {transaction2},
            ...
        ]
    }
    """
    try:
        if fraud_detector is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        data = request.get_json()
        transactions = data.get('transactions', [])
        
        if not transactions:
            return jsonify({'error': 'No transactions provided'}), 400
        
        results = []
        for i, transaction in enumerate(transactions):
            try:
                # Add engineered features
                trans = transaction.copy()
                trans['amount_log'] = np.log1p(trans['amount'])
                trans['is_night'] = int((trans['hour'] >= 23) or (trans['hour'] <= 5))
                trans['is_business_hours'] = int((trans['hour'] >= 9) and (trans['hour'] <= 17))
                
                amount_mean = 150.0
                amount_std = 200.0
                trans['amount_zscore'] = (trans['amount'] - amount_mean) / amount_std
                
                prediction = fraud_detector.predict_fraud(trans)
                
                results.append({
                    'transaction_index': i,
                    'transaction_id': transaction.get('transaction_id', f'tx_{i}'),
                    'prediction': prediction
                })
                
            except Exception as e:
                results.append({
                    'transaction_index': i,
                    'transaction_id': transaction.get('transaction_id', f'tx_{i}'),
                    'error': str(e)
                })
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/model_info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    if fraud_detector is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({
        'model_name': getattr(fraud_detector, 'best_model_name', 'unknown'),
        'feature_count': len(getattr(fraud_detector, 'feature_names', [])),
        'features': getattr(fraud_detector, 'feature_names', [])
    })

@app.route('/retrain', methods=['POST'])
def retrain_model():
    """Retrain the model with new data"""
    try:
        global fraud_detector
        
        # Reinitialize and retrain
        fraud_detector = FraudDetectionModel()
        
        # Get sample size from request or use default
        data = request.get_json() or {}
        sample_size = data.get('sample_size', 10000)
        
        df = fraud_detector.generate_sample_data(n_samples=sample_size)
        X, y = fraud_detector.preprocess_data(df)
        fraud_detector.train_models(X, y)
        fraud_detector.save_model()
        
        return jsonify({
            'message': 'Model retrained successfully',
            'model_name': fraud_detector.best_model_name,
            'training_samples': len(df)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Fraud Detection API...")
    load_fraud_model()
    app.run(host='0.0.0.0', port=5000, debug=True)