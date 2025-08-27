#!/usr/bin/env python3
"""
Credit Card Fraud Detection System Runner
Comprehensive script to set up and run the complete fraud detection system
"""

import os
import sys
import subprocess
import time
import signal
import threading
import requests
from pathlib import Path

class FraudDetectionSystemRunner:
    """Manager for running the complete fraud detection system"""
    
    def __init__(self):
        self.processes = []
        self.workspace = Path("/workspace")
        self.python_process = None
        self.java_process = None
        
    def check_prerequisites(self):
        """Check if all prerequisites are installed"""
        print("Checking prerequisites...")
        
        # Check Python dependencies
        try:
            import pandas, sklearn, flask, matplotlib, seaborn, joblib
            print("✓ Python dependencies available")
        except ImportError as e:
            print(f"✗ Missing Python dependency: {e}")
            print("Installing Python dependencies...")
            self.install_python_dependencies()
        
        # Check Java
        try:
            result = subprocess.run(["java", "-version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Java is available")
            else:
                print("✗ Java not found")
                return False
        except FileNotFoundError:
            print("✗ Java not found")
            return False
        
        # Check Maven
        try:
            result = subprocess.run(["./mvnw", "--version"], 
                                  cwd=self.workspace,
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Maven wrapper is available")
            else:
                print("✗ Maven wrapper not working")
                return False
        except FileNotFoundError:
            print("✗ Maven wrapper not found")
            return False
        
        return True
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        print("Installing Python dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.workspace / "requirements.txt")
            ], check=True)
            print("✓ Python dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install Python dependencies: {e}")
            sys.exit(1)
    
    def generate_sample_data(self):
        """Generate sample data for testing"""
        print("Generating sample data...")
        try:
            subprocess.run([
                sys.executable, 
                str(self.workspace / "sample_data_generator.py")
            ], check=True, cwd=self.workspace)
            print("✓ Sample data generated")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to generate sample data: {e}")
    
    def train_ml_model(self):
        """Train the machine learning model"""
        print("Training ML model...")
        try:
            subprocess.run([
                sys.executable, 
                str(self.workspace / "fraud_detection_model.py")
            ], check=True, cwd=self.workspace)
            print("✓ ML model trained and saved")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to train ML model: {e}")
    
    def start_python_api(self):
        """Start the Python ML API"""
        print("Starting Python ML API...")
        try:
            self.python_process = subprocess.Popen([
                sys.executable,
                str(self.workspace / "fraud_detection_api.py")
            ], cwd=self.workspace)
            
            # Wait for API to be ready
            for attempt in range(30):
                try:
                    response = requests.get("http://localhost:5000/health", timeout=5)
                    if response.status_code == 200:
                        print("✓ Python ML API is running on http://localhost:5000")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(2)
            
            print("✗ Python ML API failed to start")
            return False
            
        except Exception as e:
            print(f"✗ Failed to start Python ML API: {e}")
            return False
    
    def build_java_app(self):
        """Build the Java Spring Boot application"""
        print("Building Java Spring Boot application...")
        try:
            result = subprocess.run([
                "./mvnw", "clean", "package", "-DskipTests"
            ], cwd=self.workspace, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Java application built successfully")
                return True
            else:
                print(f"✗ Java build failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Failed to build Java application: {e}")
            return False
    
    def start_java_api(self):
        """Start the Java Spring Boot API"""
        print("Starting Java Spring Boot API...")
        try:
            self.java_process = subprocess.Popen([
                "./mvnw", "spring-boot:run"
            ], cwd=self.workspace)
            
            # Wait for API to be ready
            for attempt in range(60):
                try:
                    response = requests.get("http://localhost:8080/api/v1/fraud-detection/health", timeout=5)
                    if response.status_code == 200:
                        print("✓ Java Spring Boot API is running on http://localhost:8080")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(3)
            
            print("✗ Java Spring Boot API failed to start")
            return False
            
        except Exception as e:
            print(f"✗ Failed to start Java Spring Boot API: {e}")
            return False
    
    def run_tests(self):
        """Run the API tests"""
        print("Running API tests...")
        try:
            result = subprocess.run([
                sys.executable,
                str(self.workspace / "test_fraud_detection_api.py")
            ], cwd=self.workspace)
            
            if result.returncode == 0:
                print("✓ All tests passed!")
                return True
            else:
                print("✗ Some tests failed")
                return False
                
        except Exception as e:
            print(f"✗ Failed to run tests: {e}")
            return False
    
    def cleanup(self):
        """Clean up running processes"""
        print("\nCleaning up...")
        
        if self.python_process:
            self.python_process.terminate()
            self.python_process.wait()
            print("✓ Python ML API stopped")
        
        if self.java_process:
            self.java_process.terminate()
            self.java_process.wait()
            print("✓ Java Spring Boot API stopped")
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print("\nReceived interrupt signal. Shutting down...")
        self.cleanup()
        sys.exit(0)
    
    def run_system(self, run_tests=True):
        """Run the complete fraud detection system"""
        print("="*60)
        print("CREDIT CARD FRAUD DETECTION SYSTEM")
        print("JPMC Advanced Software Engineering Program")
        print("="*60)
        
        # Set up signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                print("Prerequisites check failed. Exiting.")
                return False
            
            # Generate sample data
            self.generate_sample_data()
            
            # Train ML model
            self.train_ml_model()
            
            # Start Python ML API
            if not self.start_python_api():
                print("Warning: Python ML API failed to start. Using fallback rules.")
            
            # Build Java application
            if not self.build_java_app():
                print("Java build failed. Exiting.")
                return False
            
            # Start Java API
            if not self.start_java_api():
                print("Java API failed to start. Exiting.")
                return False
            
            print("\n" + "="*60)
            print("SYSTEM SUCCESSFULLY STARTED!")
            print("="*60)
            print("Services running:")
            print("  • Java Spring Boot API: http://localhost:8080")
            print("  • Python ML API: http://localhost:5000")
            print("  • API Documentation: http://localhost:8080/swagger-ui.html")
            print("\nAPI Endpoints:")
            print("  • Health: GET /api/v1/fraud-detection/health")
            print("  • Single Prediction: POST /api/v1/fraud-detection/predict")
            print("  • Batch Prediction: POST /api/v1/fraud-detection/predict/batch")
            print("  • Model Info: GET /api/v1/fraud-detection/model/info")
            print("="*60)
            
            # Run tests if requested
            if run_tests:
                print("\nRunning comprehensive tests...")
                time.sleep(5)  # Give services time to fully start
                self.run_tests()
            
            # Keep services running
            print("\nServices are running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
        except Exception as e:
            print(f"Error running system: {e}")
            return False
        finally:
            self.cleanup()
        
        return True
    
    def demo_mode(self):
        """Run in demo mode with example predictions"""
        print("\n" + "="*60)
        print("DEMO MODE - Example Predictions")
        print("="*60)
        
        # Example transactions
        examples = [
            {
                "name": "Normal grocery purchase",
                "transaction": {
                    "transactionId": "DEMO_001",
                    "amount": 85.50,
                    "hour": 14,
                    "merchantCategory": "grocery",
                    "dayOfWeek": 2,
                    "customerAge": 45,
                    "daysSinceLastTransaction": 2,
                    "isWeekend": 0
                }
            },
            {
                "name": "Suspicious late night online purchase",
                "transaction": {
                    "transactionId": "DEMO_002",
                    "amount": 2500.00,
                    "hour": 3,
                    "merchantCategory": "online",
                    "dayOfWeek": 6,
                    "customerAge": 25,
                    "daysSinceLastTransaction": 0,
                    "isWeekend": 1
                }
            },
            {
                "name": "High amount gas station purchase",
                "transaction": {
                    "transactionId": "DEMO_003",
                    "amount": 1200.00,
                    "hour": 2,
                    "merchantCategory": "gas",
                    "dayOfWeek": 1,
                    "customerAge": 30,
                    "daysSinceLastTransaction": 0,
                    "isWeekend": 0
                }
            }
        ]
        
        for example in examples:
            print(f"\n--- {example['name']} ---")
            try:
                response = requests.post(
                    "http://localhost:8080/api/v1/fraud-detection/predict",
                    json=example['transaction'],
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    fraud_status = "🚨 FRAUD DETECTED" if result['fraud'] else "✅ LEGITIMATE"
                    print(f"Result: {fraud_status}")
                    print(f"Fraud Probability: {result['fraudProbability']:.1%}")
                    print(f"Risk Level: {result['riskLevel']}")
                    print(f"Model Used: {result['modelUsed']}")
                else:
                    print(f"Error: {response.status_code}")
                    
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n" + "="*60)


def main():
    """Main entry point"""
    runner = FraudDetectionSystemRunner()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--no-tests":
        success = runner.run_system(run_tests=False)
    elif len(sys.argv) > 1 and sys.argv[1] == "--demo":
        success = runner.run_system(run_tests=False)
        if success:
            time.sleep(2)
            runner.demo_mode()
    else:
        success = runner.run_system(run_tests=True)
    
    return success


if __name__ == "__main__":
    main()