#!/usr/bin/env python3
"""
Test Script for Credit Card Fraud Detection API
Tests both Python ML API and Java Spring Boot API
"""

import requests
import json
import time
import subprocess
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import threading

class FraudDetectionAPITester:
    """Test the fraud detection API endpoints"""
    
    def __init__(self, java_api_url="http://localhost:8080", python_api_url="http://localhost:5000"):
        self.java_api_url = java_api_url
        self.python_api_url = python_api_url
        self.test_results = []
        
    def wait_for_service(self, url, service_name, max_attempts=30):
        """Wait for a service to become available"""
        print(f"Waiting for {service_name} to start...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✓ {service_name} is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            print(f"  Attempt {attempt + 1}/{max_attempts} - {service_name} not ready yet...")
            time.sleep(2)
        
        print(f"✗ {service_name} failed to start after {max_attempts} attempts")
        return False
    
    def test_health_endpoint(self, url, service_name):
        """Test the health endpoint"""
        print(f"\n=== Testing {service_name} Health Endpoint ===")
        
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Health check passed: {data}")
                return True
            else:
                print(f"✗ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Health check error: {e}")
            return False
    
    def test_single_prediction(self):
        """Test single transaction prediction"""
        print(f"\n=== Testing Single Transaction Prediction ===")
        
        # Test normal transaction
        normal_transaction = {
            "transactionId": "TEST_NORMAL_001",
            "amount": 85.50,
            "hour": 14,
            "merchantCategory": "grocery",
            "dayOfWeek": 2,
            "customerAge": 45,
            "daysSinceLastTransaction": 2,
            "isWeekend": 0
        }
        
        try:
            response = requests.post(
                f"{self.java_api_url}/api/v1/fraud-detection/predict",
                json=normal_transaction,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Normal transaction prediction: {result}")
                print(f"  Fraud: {result['fraud']}, Probability: {result['fraudProbability']:.3f}")
                return True
            else:
                print(f"✗ Normal transaction prediction failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Normal transaction prediction error: {e}")
            return False
    
    def test_suspicious_prediction(self):
        """Test suspicious transaction prediction"""
        print(f"\n=== Testing Suspicious Transaction Prediction ===")
        
        # Test suspicious transaction
        suspicious_transaction = {
            "transactionId": "TEST_FRAUD_001",
            "amount": 2500.00,
            "hour": 3,
            "merchantCategory": "online",
            "dayOfWeek": 6,
            "customerAge": 25,
            "daysSinceLastTransaction": 0,
            "isWeekend": 1
        }
        
        try:
            response = requests.post(
                f"{self.java_api_url}/api/v1/fraud-detection/predict",
                json=suspicious_transaction,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Suspicious transaction prediction: {result}")
                print(f"  Fraud: {result['fraud']}, Probability: {result['fraudProbability']:.3f}")
                return True
            else:
                print(f"✗ Suspicious transaction prediction failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Suspicious transaction prediction error: {e}")
            return False
    
    def test_batch_prediction(self):
        """Test batch transaction prediction"""
        print(f"\n=== Testing Batch Transaction Prediction ===")
        
        # Create batch of transactions
        batch_request = {
            "transactions": [
                {
                    "transactionId": "BATCH_001",
                    "amount": 100.00,
                    "hour": 14,
                    "merchantCategory": "grocery",
                    "dayOfWeek": 2,
                    "customerAge": 45,
                    "daysSinceLastTransaction": 2,
                    "isWeekend": 0
                },
                {
                    "transactionId": "BATCH_002",
                    "amount": 3000.00,
                    "hour": 2,
                    "merchantCategory": "online",
                    "dayOfWeek": 6,
                    "customerAge": 25,
                    "daysSinceLastTransaction": 0,
                    "isWeekend": 1
                },
                {
                    "transactionId": "BATCH_003",
                    "amount": 50.00,
                    "hour": 12,
                    "merchantCategory": "restaurant",
                    "dayOfWeek": 3,
                    "customerAge": 35,
                    "daysSinceLastTransaction": 1,
                    "isWeekend": 0
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.java_api_url}/api/v1/fraud-detection/predict/batch",
                json=batch_request,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Batch prediction completed")
                print(f"  Total transactions: {result['totalTransactions']}")
                print(f"  Fraudulent transactions: {result['fraudulentTransactions']}")
                print(f"  Processing time: {result['processingTimeMs']}ms")
                
                for i, prediction in enumerate(result['results']):
                    print(f"  Transaction {i+1}: {prediction['transactionId']} - "
                          f"Fraud: {prediction['fraud']}, "
                          f"Probability: {prediction['fraudProbability']:.3f}")
                
                return True
            else:
                print(f"✗ Batch prediction failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Batch prediction error: {e}")
            return False
    
    def test_model_info(self):
        """Test model info endpoint"""
        print(f"\n=== Testing Model Info Endpoint ===")
        
        try:
            response = requests.get(f"{self.java_api_url}/api/v1/fraud-detection/model/info")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Model info retrieved: {result}")
                return True
            else:
                print(f"✗ Model info failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Model info error: {e}")
            return False
    
    def test_validation_errors(self):
        """Test validation error handling"""
        print(f"\n=== Testing Validation Error Handling ===")
        
        # Invalid transaction (missing required fields)
        invalid_transaction = {
            "transactionId": "TEST_INVALID",
            "amount": -50.00,  # Invalid negative amount
            "hour": 25,        # Invalid hour
            "merchantCategory": "invalid_category"  # Invalid category
        }
        
        try:
            response = requests.post(
                f"{self.java_api_url}/api/v1/fraud-detection/predict",
                json=invalid_transaction,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 400:
                print(f"✓ Validation errors handled correctly: {response.status_code}")
                print(f"  Error response: {response.json()}")
                return True
            else:
                print(f"✗ Validation not working: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Validation test error: {e}")
            return False
    
    def performance_test(self, num_requests=10):
        """Test API performance with concurrent requests"""
        print(f"\n=== Performance Test ({num_requests} concurrent requests) ===")
        
        test_transaction = {
            "transactionId": "PERF_TEST",
            "amount": 100.00,
            "hour": 14,
            "merchantCategory": "grocery",
            "dayOfWeek": 2,
            "customerAge": 45,
            "daysSinceLastTransaction": 2,
            "isWeekend": 0
        }
        
        def make_request(i):
            transaction = test_transaction.copy()
            transaction["transactionId"] = f"PERF_TEST_{i}"
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.java_api_url}/api/v1/fraud-detection/predict",
                    json=transaction,
                    headers={'Content-Type': 'application/json'}
                )
                end_time = time.time()
                
                return {
                    'success': response.status_code == 200,
                    'response_time': end_time - start_time,
                    'transaction_id': transaction["transactionId"]
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'transaction_id': transaction["transactionId"]
                }
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, range(num_requests)))
        
        end_time = time.time()
        
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        if successful_requests:
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
            max_response_time = max(r['response_time'] for r in successful_requests)
            min_response_time = min(r['response_time'] for r in successful_requests)
            
            print(f"✓ Performance test completed")
            print(f"  Total requests: {num_requests}")
            print(f"  Successful: {len(successful_requests)}")
            print(f"  Failed: {len(failed_requests)}")
            print(f"  Total time: {end_time - start_time:.2f}s")
            print(f"  Average response time: {avg_response_time:.3f}s")
            print(f"  Min response time: {min_response_time:.3f}s")
            print(f"  Max response time: {max_response_time:.3f}s")
            print(f"  Requests per second: {num_requests / (end_time - start_time):.2f}")
            
            return len(failed_requests) == 0
        else:
            print(f"✗ All performance test requests failed")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("=== CREDIT CARD FRAUD DETECTION API TEST SUITE ===\n")
        
        # Test health endpoints
        java_healthy = self.test_health_endpoint(self.java_api_url, "Java API")
        python_healthy = self.test_health_endpoint(self.python_api_url, "Python ML API")
        
        if not java_healthy:
            print("✗ Java API is not healthy. Skipping tests.")
            return False
        
        # Run all tests
        tests = [
            ("Single Prediction", self.test_single_prediction),
            ("Suspicious Prediction", self.test_suspicious_prediction),
            ("Batch Prediction", self.test_batch_prediction),
            ("Model Info", self.test_model_info),
            ("Validation Errors", self.test_validation_errors),
            ("Performance Test", lambda: self.performance_test(10))
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    print(f"✓ {test_name} PASSED")
                else:
                    print(f"✗ {test_name} FAILED")
            except Exception as e:
                print(f"✗ {test_name} ERROR: {e}")
        
        print(f"\n=== TEST SUMMARY ===")
        print(f"Passed: {passed}/{total}")
        print(f"Success rate: {passed/total*100:.1f}%")
        
        if python_healthy:
            print("✓ Python ML API is healthy")
        else:
            print("⚠ Python ML API is not available (using fallback rules)")
        
        return passed == total


def main():
    """Main test execution"""
    tester = FraudDetectionAPITester()
    
    print("Starting API tests...")
    print("Make sure both Java and Python services are running:")
    print("  Java API: http://localhost:8080")
    print("  Python ML API: http://localhost:5000")
    print()
    
    # Wait for services to be ready
    java_ready = tester.wait_for_service("http://localhost:8080", "Java API")
    
    if not java_ready:
        print("Java API is not available. Please start the service and try again.")
        return False
    
    # Python API is optional (fallback rules will be used if not available)
    python_ready = tester.wait_for_service("http://localhost:5000", "Python ML API")
    if not python_ready:
        print("Python ML API is not available. Tests will use fallback rules.")
    
    # Run tests
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)