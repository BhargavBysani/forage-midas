#!/usr/bin/env python3
"""
Credit Card Fraud Detection System
Advanced machine learning model for detecting fraudulent transactions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.pipeline import Pipeline
import joblib
import warnings
warnings.filterwarnings('ignore')

class FraudDetectionModel:
    """
    Credit Card Fraud Detection Model using ensemble methods
    """
    
    def __init__(self):
        self.models = {}
        self.scaler = RobustScaler()
        self.best_model = None
        self.feature_names = None
        
    def generate_sample_data(self, n_samples=10000):
        """
        Generate realistic sample credit card transaction data
        """
        np.random.seed(42)
        
        # Normal transaction patterns
        normal_transactions = {
            'amount': np.random.lognormal(mean=3, sigma=1, size=int(n_samples * 0.998)),
            'hour': np.random.choice(range(24), size=int(n_samples * 0.998), 
                                   p=[0.02, 0.01, 0.01, 0.01, 0.02, 0.03, 0.05, 0.07, 
                                      0.08, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.04,
                                      0.05, 0.06, 0.07, 0.08, 0.06, 0.05, 0.04, 0.03]),
            'merchant_category': np.random.choice(['grocery', 'gas', 'restaurant', 'retail', 'online'], 
                                                size=int(n_samples * 0.998),
                                                p=[0.25, 0.15, 0.20, 0.25, 0.15]),
            'day_of_week': np.random.choice(range(7), size=int(n_samples * 0.998)),
            'customer_age': np.random.normal(45, 15, size=int(n_samples * 0.998)).clip(18, 80),
            'days_since_last_transaction': np.random.exponential(2, size=int(n_samples * 0.998)).clip(0, 30),
            'is_weekend': np.random.choice([0, 1], size=int(n_samples * 0.998), p=[5/7, 2/7]),
            'Class': np.zeros(int(n_samples * 0.998))
        }
        
        # Fraudulent transaction patterns (different distributions)
        fraud_transactions = {
            'amount': np.concatenate([
                np.random.lognormal(mean=2, sigma=0.5, size=int(n_samples * 0.001)),  # Small amounts
                np.random.lognormal(mean=8, sigma=0.5, size=int(n_samples * 0.001))   # Large amounts
            ]),
            'hour': np.random.choice(range(24), size=int(n_samples * 0.002),
                                   p=[0.08, 0.09, 0.08, 0.07, 0.06, 0.04, 0.02, 0.02,
                                      0.03, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04,
                                      0.04, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.08]),
            'merchant_category': np.random.choice(['grocery', 'gas', 'restaurant', 'retail', 'online'], 
                                                size=int(n_samples * 0.002),
                                                p=[0.10, 0.10, 0.15, 0.15, 0.50]),  # More online
            'day_of_week': np.random.choice(range(7), size=int(n_samples * 0.002)),
            'customer_age': np.random.normal(35, 20, size=int(n_samples * 0.002)).clip(18, 80),
            'days_since_last_transaction': np.random.exponential(0.5, size=int(n_samples * 0.002)).clip(0, 1),
            'is_weekend': np.random.choice([0, 1], size=int(n_samples * 0.002), p=[0.4, 0.6]),  # More weekend fraud
            'Class': np.ones(int(n_samples * 0.002))
        }
        
        # Combine normal and fraud transactions
        data = {}
        for key in normal_transactions.keys():
            data[key] = np.concatenate([normal_transactions[key], fraud_transactions[key]])
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Add engineered features
        df['amount_log'] = np.log1p(df['amount'])
        df['is_night'] = ((df['hour'] >= 23) | (df['hour'] <= 5)).astype(int)
        df['is_business_hours'] = ((df['hour'] >= 9) & (df['hour'] <= 17)).astype(int)
        df['amount_zscore'] = (df['amount'] - df['amount'].mean()) / df['amount'].std()
        
        # One-hot encode categorical variables
        df_encoded = pd.get_dummies(df, columns=['merchant_category'], prefix='merchant')
        
        # Shuffle the data
        df_encoded = df_encoded.sample(frac=1, random_state=42).reset_index(drop=True)
        
        return df_encoded
    
    def preprocess_data(self, df):
        """
        Preprocess the data for training
        """
        # Separate features and target
        X = df.drop('Class', axis=1)
        y = df['Class']
        
        self.feature_names = X.columns.tolist()
        
        return X, y
    
    def train_models(self, X, y):
        """
        Train multiple models and find the best one
        """
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale the features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Define models
        models = {
            'logistic_regression': LogisticRegression(
                random_state=42, 
                class_weight='balanced',
                max_iter=1000
            ),
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight='balanced',
                max_depth=10
            ),
            'svm': SVC(
                probability=True,
                random_state=42,
                class_weight='balanced',
                kernel='rbf'
            )
        }
        
        # Train and evaluate models
        best_score = 0
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            
            if name == 'logistic_regression' or name == 'svm':
                model.fit(X_train_scaled, y_train)
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            else:
                model.fit(X_train, y_train)
                y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            auc_score = roc_auc_score(y_test, y_pred_proba)
            print(f"{name} AUC Score: {auc_score:.4f}")
            
            self.models[name] = model
            
            if auc_score > best_score:
                best_score = auc_score
                self.best_model = model
                self.best_model_name = name
        
        print(f"\nBest model: {self.best_model_name} with AUC: {best_score:.4f}")
        
        return X_train, X_test, y_train, y_test
    
    def evaluate_model(self, X_test, y_test):
        """
        Evaluate the best model performance
        """
        if self.best_model_name == 'logistic_regression' or self.best_model_name == 'svm':
            X_test_processed = self.scaler.transform(X_test)
        else:
            X_test_processed = X_test
            
        y_pred = self.best_model.predict(X_test_processed)
        y_pred_proba = self.best_model.predict_proba(X_test_processed)[:, 1]
        
        print("\n" + "="*50)
        print("MODEL EVALUATION RESULTS")
        print("="*50)
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        print(f"\nAUC-ROC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(f"True Negatives: {cm[0,0]}")
        print(f"False Positives: {cm[0,1]}")
        print(f"False Negatives: {cm[1,0]}")
        print(f"True Positives: {cm[1,1]}")
        
        return y_pred, y_pred_proba
    
    def plot_feature_importance(self):
        """
        Plot feature importance for tree-based models
        """
        if hasattr(self.best_model, 'feature_importances_'):
            importances = self.best_model.feature_importances_
            indices = np.argsort(importances)[::-1]
            
            plt.figure(figsize=(12, 8))
            plt.title("Feature Importance")
            plt.bar(range(len(importances)), importances[indices])
            plt.xticks(range(len(importances)), 
                      [self.feature_names[i] for i in indices], 
                      rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig('/workspace/feature_importance.png', dpi=300, bbox_inches='tight')
            plt.show()
    
    def plot_roc_curve(self, y_test, y_pred_proba):
        """
        Plot ROC curve
        """
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        auc = roc_auc_score(y_test, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC curve (AUC = {auc:.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve - Credit Card Fraud Detection')
        plt.legend(loc="lower right")
        plt.grid(True)
        plt.savefig('/workspace/roc_curve.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def predict_fraud(self, transaction_data):
        """
        Predict if a transaction is fraudulent
        
        Args:
            transaction_data: dict with transaction features
            
        Returns:
            dict with prediction results
        """
        if self.best_model is None:
            raise ValueError("Model not trained yet. Please train the model first.")
        
        # Convert to DataFrame for consistent preprocessing
        df = pd.DataFrame([transaction_data])
        
        # Apply same preprocessing as training
        if 'merchant_category' in df.columns:
            df_encoded = pd.get_dummies(df, columns=['merchant_category'], prefix='merchant')
            
            # Ensure all merchant categories are present
            for col in self.feature_names:
                if col not in df_encoded.columns:
                    df_encoded[col] = 0
            
            # Reorder columns to match training data
            df_encoded = df_encoded[self.feature_names]
        else:
            df_encoded = df
        
        # Scale if necessary
        if self.best_model_name == 'logistic_regression' or self.best_model_name == 'svm':
            X_processed = self.scaler.transform(df_encoded)
        else:
            X_processed = df_encoded
        
        # Make prediction
        fraud_probability = self.best_model.predict_proba(X_processed)[0, 1]
        is_fraud = fraud_probability > 0.5
        
        # Risk level classification
        if fraud_probability < 0.3:
            risk_level = "Low"
        elif fraud_probability < 0.7:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return {
            'is_fraud': bool(is_fraud),
            'fraud_probability': float(fraud_probability),
            'risk_level': risk_level,
            'model_used': self.best_model_name
        }
    
    def save_model(self, filepath='/workspace/fraud_detection_model.pkl'):
        """
        Save the trained model and scaler
        """
        model_data = {
            'best_model': self.best_model,
            'best_model_name': self.best_model_name,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='/workspace/fraud_detection_model.pkl'):
        """
        Load a trained model and scaler
        """
        model_data = joblib.load(filepath)
        self.best_model = model_data['best_model']
        self.best_model_name = model_data['best_model_name']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        print(f"Model loaded from {filepath}")


def main():
    """
    Main function to demonstrate the fraud detection system
    """
    print("Credit Card Fraud Detection System")
    print("=" * 50)
    
    # Initialize the model
    fraud_detector = FraudDetectionModel()
    
    # Generate sample data
    print("Generating sample transaction data...")
    df = fraud_detector.generate_sample_data(n_samples=10000)
    print(f"Generated {len(df)} transactions")
    print(f"Fraud rate: {df['Class'].mean():.2%}")
    
    # Preprocess data
    X, y = fraud_detector.preprocess_data(df)
    
    # Train models
    print("\nTraining fraud detection models...")
    X_train, X_test, y_train, y_test = fraud_detector.train_models(X, y)
    
    # Evaluate the best model
    y_pred, y_pred_proba = fraud_detector.evaluate_model(X_test, y_test)
    
    # Create visualizations
    fraud_detector.plot_feature_importance()
    fraud_detector.plot_roc_curve(y_test, y_pred_proba)
    
    # Save the model
    fraud_detector.save_model()
    
    # Example prediction
    print("\n" + "="*50)
    print("EXAMPLE TRANSACTION PREDICTION")
    print("="*50)
    
    # Normal transaction example
    normal_transaction = {
        'amount': 85.50,
        'hour': 14,
        'merchant_category': 'grocery',
        'day_of_week': 2,
        'customer_age': 45,
        'days_since_last_transaction': 2,
        'is_weekend': 0,
        'amount_log': np.log1p(85.50),
        'is_night': 0,
        'is_business_hours': 1,
        'amount_zscore': (85.50 - df['amount'].mean()) / df['amount'].std()
    }
    
    result = fraud_detector.predict_fraud(normal_transaction)
    print(f"Normal Transaction: {result}")
    
    # Suspicious transaction example
    suspicious_transaction = {
        'amount': 2500.00,
        'hour': 3,
        'merchant_category': 'online',
        'day_of_week': 6,
        'customer_age': 25,
        'days_since_last_transaction': 0,
        'is_weekend': 1,
        'amount_log': np.log1p(2500.00),
        'is_night': 1,
        'is_business_hours': 0,
        'amount_zscore': (2500.00 - df['amount'].mean()) / df['amount'].std()
    }
    
    result = fraud_detector.predict_fraud(suspicious_transaction)
    print(f"Suspicious Transaction: {result}")
    
    print("\nFraud detection system setup complete!")


if __name__ == "__main__":
    main()