package com.jpmc.frauddetection.model;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import java.util.List;

/**
 * Request model for batch fraud prediction
 */
public class BatchPredictionRequest {
    
    @NotEmpty(message = "Transactions list cannot be empty")
    @Valid
    private List<Transaction> transactions;
    
    // Default constructor
    public BatchPredictionRequest() {}
    
    // Constructor
    public BatchPredictionRequest(List<Transaction> transactions) {
        this.transactions = transactions;
    }
    
    // Getters and Setters
    public List<Transaction> getTransactions() {
        return transactions;
    }
    
    public void setTransactions(List<Transaction> transactions) {
        this.transactions = transactions;
    }
    
    @Override
    public String toString() {
        return "BatchPredictionRequest{" +
                "transactions=" + transactions +
                '}';
    }
}