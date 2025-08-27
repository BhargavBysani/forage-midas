#!/usr/bin/env python3
"""
Sample Data Generator for Credit Card Fraud Detection Testing
Generates realistic test data for API testing
"""

import json
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class SampleDataGenerator:
    """Generate sample credit card transaction data for testing"""
    
    def __init__(self):
        self.merchant_categories = ['grocery', 'gas', 'restaurant', 'retail', 'online']
        self.customer_ages = list(range(18, 80))
        
    def generate_normal_transaction(self):
        """Generate a normal (non-fraudulent) transaction"""
        return {
            "transactionId": f"TXN_{uuid.uuid4().hex[:8].upper()}",
            "amount": round(random.lognormal(3, 1), 2),  # Typically smaller amounts
            "hour": random.choices(range(24), weights=[
                2, 1, 1, 1, 2, 3, 5, 7, 8, 9, 8, 7, 6, 5, 4, 4,
                5, 6, 7, 8, 6, 5, 4, 3
            ])[0],  # More activity during business hours
            "merchantCategory": random.choices(self.merchant_categories, 
                                             weights=[25, 15, 20, 25, 15])[0],
            "dayOfWeek": random.randint(0, 6),
            "customerAge": random.choice(self.customer_ages),
            "daysSinceLastTransaction": max(0, int(random.expovariate(0.5))),
            "isWeekend": random.choices([0, 1], weights=[5, 2])[0],
            "customerId": f"CUST_{random.randint(10000, 99999)}",
            "merchantId": f"MERCH_{random.randint(1000, 9999)}"
        }
    
    def generate_fraudulent_transaction(self):
        """Generate a fraudulent transaction"""
        return {
            "transactionId": f"TXN_{uuid.uuid4().hex[:8].upper()}",
            "amount": round(random.choice([
                random.lognormal(2, 0.5),    # Small amounts
                random.lognormal(8, 0.5)     # Large amounts
            ]), 2),
            "hour": random.choices(range(24), weights=[
                8, 9, 8, 7, 6, 4, 2, 2, 3, 4, 4, 4, 4, 4, 4, 4,
                4, 4, 5, 6, 7, 8, 9, 8
            ])[0],  # More night activity
            "merchantCategory": random.choices(self.merchant_categories,
                                             weights=[10, 10, 15, 15, 50])[0],  # More online
            "dayOfWeek": random.randint(0, 6),
            "customerAge": random.choice(self.customer_ages),
            "daysSinceLastTransaction": random.choices([0, 1], weights=[8, 2])[0],  # Quick succession
            "isWeekend": random.choices([0, 1], weights=[4, 6])[0],  # More weekend activity
            "customerId": f"CUST_{random.randint(10000, 99999)}",
            "merchantId": f"MERCH_{random.randint(1000, 9999)}"
        }
    
    def generate_test_dataset(self, total_transactions=100, fraud_rate=0.02):
        """Generate a complete test dataset"""
        fraud_count = int(total_transactions * fraud_rate)
        normal_count = total_transactions - fraud_count
        
        transactions = []
        
        # Generate normal transactions
        for _ in range(normal_count):
            transactions.append(self.generate_normal_transaction())
        
        # Generate fraudulent transactions
        for _ in range(fraud_count):
            transactions.append(self.generate_fraudulent_transaction())
        
        # Shuffle the transactions
        random.shuffle(transactions)
        
        return transactions
    
    def save_to_json(self, transactions, filename):
        """Save transactions to JSON file"""
        with open(filename, 'w') as f:
            json.dump(transactions, f, indent=2)
        print(f"Saved {len(transactions)} transactions to {filename}")
    
    def save_to_csv(self, transactions, filename):
        """Save transactions to CSV file"""
        df = pd.DataFrame(transactions)
        df.to_csv(filename, index=False)
        print(f"Saved {len(transactions)} transactions to {filename}")
    
    def create_api_test_cases(self):
        """Create specific test cases for API testing"""
        test_cases = {
            "normal_transaction": {
                "transactionId": "TEST_NORMAL_001",
                "amount": 85.50,
                "hour": 14,
                "merchantCategory": "grocery",
                "dayOfWeek": 2,
                "customerAge": 45,
                "daysSinceLastTransaction": 2,
                "isWeekend": 0,
                "customerId": "CUST_12345",
                "merchantId": "MERCH_5678"
            },
            "suspicious_high_amount": {
                "transactionId": "TEST_FRAUD_001",
                "amount": 2500.00,
                "hour": 3,
                "merchantCategory": "online",
                "dayOfWeek": 6,
                "customerAge": 25,
                "daysSinceLastTransaction": 0,
                "isWeekend": 1,
                "customerId": "CUST_99999",
                "merchantId": "MERCH_9999"
            },
            "night_transaction": {
                "transactionId": "TEST_FRAUD_002",
                "amount": 150.00,
                "hour": 2,
                "merchantCategory": "gas",
                "dayOfWeek": 1,
                "customerAge": 30,
                "daysSinceLastTransaction": 0,
                "isWeekend": 0,
                "customerId": "CUST_88888",
                "merchantId": "MERCH_8888"
            },
            "multiple_quick_transactions": [
                {
                    "transactionId": "TEST_BATCH_001",
                    "amount": 200.00,
                    "hour": 10,
                    "merchantCategory": "retail",
                    "dayOfWeek": 3,
                    "customerAge": 35,
                    "daysSinceLastTransaction": 0,
                    "isWeekend": 0,
                    "customerId": "CUST_77777",
                    "merchantId": "MERCH_7777"
                },
                {
                    "transactionId": "TEST_BATCH_002",
                    "amount": 300.00,
                    "hour": 10,
                    "merchantCategory": "online",
                    "dayOfWeek": 3,
                    "customerAge": 35,
                    "daysSinceLastTransaction": 0,
                    "isWeekend": 0,
                    "customerId": "CUST_77777",
                    "merchantId": "MERCH_6666"
                }
            ]
        }
        
        return test_cases


def main():
    """Generate sample data files"""
    print("Generating sample credit card transaction data...")
    
    generator = SampleDataGenerator()
    
    # Generate test datasets of different sizes
    datasets = [
        (100, 0.02, "small"),
        (1000, 0.02, "medium"), 
        (10000, 0.02, "large")
    ]
    
    for size, fraud_rate, label in datasets:
        transactions = generator.generate_test_dataset(size, fraud_rate)
        
        # Save as JSON
        generator.save_to_json(transactions, f"/workspace/sample_data_{label}.json")
        
        # Save as CSV
        generator.save_to_csv(transactions, f"/workspace/sample_data_{label}.csv")
        
        fraud_count = sum(1 for t in transactions if 'fraud' in str(t).lower())
        print(f"Generated {label} dataset: {size} transactions, ~{fraud_rate*100}% fraud rate")
    
    # Generate API test cases
    test_cases = generator.create_api_test_cases()
    with open("/workspace/api_test_cases.json", 'w') as f:
        json.dump(test_cases, f, indent=2)
    print("Generated API test cases")
    
    print("\nSample data generation complete!")
    print("Files created:")
    print("- sample_data_small.json/csv (100 transactions)")
    print("- sample_data_medium.json/csv (1,000 transactions)")
    print("- sample_data_large.json/csv (10,000 transactions)")
    print("- api_test_cases.json (specific test cases)")


if __name__ == "__main__":
    main()