package com.jpmc.frauddetection.model;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.time.LocalDateTime;

/**
 * Fraud prediction result model
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class FraudPrediction {
    
    private String transactionId;
    private boolean isFraud;
    private double fraudProbability;
    private String riskLevel;
    private String modelUsed;
    private LocalDateTime predictionTimestamp;
    private String reason;
    private Transaction inputTransaction;
    
    // Default constructor
    public FraudPrediction() {
        this.predictionTimestamp = LocalDateTime.now();
    }
    
    // Constructor
    public FraudPrediction(String transactionId, boolean isFraud, double fraudProbability, 
                          String riskLevel, String modelUsed) {
        this.transactionId = transactionId;
        this.isFraud = isFraud;
        this.fraudProbability = fraudProbability;
        this.riskLevel = riskLevel;
        this.modelUsed = modelUsed;
        this.predictionTimestamp = LocalDateTime.now();
    }
    
    // Getters and Setters
    public String getTransactionId() {
        return transactionId;
    }
    
    public void setTransactionId(String transactionId) {
        this.transactionId = transactionId;
    }
    
    public boolean isFraud() {
        return isFraud;
    }
    
    public void setFraud(boolean fraud) {
        isFraud = fraud;
    }
    
    public double getFraudProbability() {
        return fraudProbability;
    }
    
    public void setFraudProbability(double fraudProbability) {
        this.fraudProbability = fraudProbability;
    }
    
    public String getRiskLevel() {
        return riskLevel;
    }
    
    public void setRiskLevel(String riskLevel) {
        this.riskLevel = riskLevel;
    }
    
    public String getModelUsed() {
        return modelUsed;
    }
    
    public void setModelUsed(String modelUsed) {
        this.modelUsed = modelUsed;
    }
    
    public LocalDateTime getPredictionTimestamp() {
        return predictionTimestamp;
    }
    
    public void setPredictionTimestamp(LocalDateTime predictionTimestamp) {
        this.predictionTimestamp = predictionTimestamp;
    }
    
    public String getReason() {
        return reason;
    }
    
    public void setReason(String reason) {
        this.reason = reason;
    }
    
    public Transaction getInputTransaction() {
        return inputTransaction;
    }
    
    public void setInputTransaction(Transaction inputTransaction) {
        this.inputTransaction = inputTransaction;
    }
    
    @Override
    public String toString() {
        return "FraudPrediction{" +
                "transactionId='" + transactionId + '\'' +
                ", isFraud=" + isFraud +
                ", fraudProbability=" + fraudProbability +
                ", riskLevel='" + riskLevel + '\'' +
                ", modelUsed='" + modelUsed + '\'' +
                ", predictionTimestamp=" + predictionTimestamp +
                ", reason='" + reason + '\'' +
                '}';
    }
}