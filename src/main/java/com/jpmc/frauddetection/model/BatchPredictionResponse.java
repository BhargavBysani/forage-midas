package com.jpmc.frauddetection.model;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Response model for batch fraud prediction
 */
public class BatchPredictionResponse {
    
    private List<FraudPrediction> results;
    private int totalTransactions;
    private int fraudulentTransactions;
    private LocalDateTime processingTimestamp;
    private long processingTimeMs;
    
    // Default constructor
    public BatchPredictionResponse() {
        this.processingTimestamp = LocalDateTime.now();
    }
    
    // Constructor
    public BatchPredictionResponse(List<FraudPrediction> results) {
        this.results = results;
        this.totalTransactions = results.size();
        this.fraudulentTransactions = (int) results.stream().mapToLong(r -> r.isFraud() ? 1 : 0).sum();
        this.processingTimestamp = LocalDateTime.now();
    }
    
    // Getters and Setters
    public List<FraudPrediction> getResults() {
        return results;
    }
    
    public void setResults(List<FraudPrediction> results) {
        this.results = results;
        this.totalTransactions = results != null ? results.size() : 0;
        this.fraudulentTransactions = results != null ? 
            (int) results.stream().mapToLong(r -> r.isFraud() ? 1 : 0).sum() : 0;
    }
    
    public int getTotalTransactions() {
        return totalTransactions;
    }
    
    public void setTotalTransactions(int totalTransactions) {
        this.totalTransactions = totalTransactions;
    }
    
    public int getFraudulentTransactions() {
        return fraudulentTransactions;
    }
    
    public void setFraudulentTransactions(int fraudulentTransactions) {
        this.fraudulentTransactions = fraudulentTransactions;
    }
    
    public LocalDateTime getProcessingTimestamp() {
        return processingTimestamp;
    }
    
    public void setProcessingTimestamp(LocalDateTime processingTimestamp) {
        this.processingTimestamp = processingTimestamp;
    }
    
    public long getProcessingTimeMs() {
        return processingTimeMs;
    }
    
    public void setProcessingTimeMs(long processingTimeMs) {
        this.processingTimeMs = processingTimeMs;
    }
    
    @Override
    public String toString() {
        return "BatchPredictionResponse{" +
                "totalTransactions=" + totalTransactions +
                ", fraudulentTransactions=" + fraudulentTransactions +
                ", processingTimestamp=" + processingTimestamp +
                ", processingTimeMs=" + processingTimeMs +
                '}';
    }
}