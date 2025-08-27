package com.jpmc.frauddetection.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jpmc.frauddetection.model.FraudPrediction;
import com.jpmc.frauddetection.model.Transaction;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.math.BigDecimal;
import java.util.*;

/**
 * Service for fraud detection operations
 * Communicates with Python ML model API
 */
@Service
public class FraudDetectionService {
    
    private static final Logger logger = LoggerFactory.getLogger(FraudDetectionService.class);
    
    @Value("${fraud.detection.api.url:http://localhost:5000}")
    private String fraudDetectionApiUrl;
    
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    
    public FraudDetectionService() {
        this.httpClient = HttpClients.createDefault();
        this.objectMapper = new ObjectMapper();
    }
    
    /**
     * Predict if a single transaction is fraudulent
     */
    public FraudPrediction predictFraud(Transaction transaction) {
        try {
            // Prepare request payload
            Map<String, Object> payload = createPayload(transaction);
            String jsonPayload = objectMapper.writeValueAsString(payload);
            
            // Make HTTP request to Python API
            HttpPost request = new HttpPost(fraudDetectionApiUrl + "/predict");
            request.setHeader("Content-Type", "application/json");
            request.setEntity(new StringEntity(jsonPayload));
            
            HttpResponse response = httpClient.execute(request);
            HttpEntity entity = response.getEntity();
            String responseBody = EntityUtils.toString(entity);
            
            if (response.getStatusLine().getStatusCode() == 200) {
                return parsePredictionResponse(responseBody, transaction);
            } else {
                logger.error("Error from fraud detection API: {}", responseBody);
                return createFallbackPrediction(transaction, "API Error: " + responseBody);
            }
            
        } catch (Exception e) {
            logger.error("Error calling fraud detection API", e);
            return createFallbackPrediction(transaction, "Service unavailable: " + e.getMessage());
        }
    }
    
    /**
     * Predict fraud for multiple transactions
     */
    public List<FraudPrediction> predictFraudBatch(List<Transaction> transactions) {
        List<FraudPrediction> results = new ArrayList<>();
        
        try {
            // Prepare batch request payload
            Map<String, Object> batchPayload = new HashMap<>();
            List<Map<String, Object>> transactionPayloads = new ArrayList<>();
            
            for (Transaction transaction : transactions) {
                transactionPayloads.add(createPayload(transaction));
            }
            batchPayload.put("transactions", transactionPayloads);
            
            String jsonPayload = objectMapper.writeValueAsString(batchPayload);
            
            // Make HTTP request to Python API
            HttpPost request = new HttpPost(fraudDetectionApiUrl + "/batch_predict");
            request.setHeader("Content-Type", "application/json");
            request.setEntity(new StringEntity(jsonPayload));
            
            HttpResponse response = httpClient.execute(request);
            HttpEntity entity = response.getEntity();
            String responseBody = EntityUtils.toString(entity);
            
            if (response.getStatusLine().getStatusCode() == 200) {
                return parseBatchPredictionResponse(responseBody, transactions);
            } else {
                logger.error("Error from fraud detection API: {}", responseBody);
                // Create fallback predictions for all transactions
                for (Transaction transaction : transactions) {
                    results.add(createFallbackPrediction(transaction, "API Error"));
                }
            }
            
        } catch (Exception e) {
            logger.error("Error calling fraud detection API for batch prediction", e);
            // Create fallback predictions for all transactions
            for (Transaction transaction : transactions) {
                results.add(createFallbackPrediction(transaction, "Service unavailable"));
            }
        }
        
        return results;
    }
    
    /**
     * Check if the fraud detection API is healthy
     */
    public boolean isApiHealthy() {
        try {
            HttpGet request = new HttpGet(fraudDetectionApiUrl + "/health");
            HttpResponse response = httpClient.execute(request);
            return response.getStatusLine().getStatusCode() == 200;
        } catch (Exception e) {
            logger.error("Health check failed for fraud detection API", e);
            return false;
        }
    }
    
    /**
     * Get model information from the API
     */
    public Map<String, Object> getModelInfo() {
        try {
            HttpGet request = new HttpGet(fraudDetectionApiUrl + "/model_info");
            HttpResponse response = httpClient.execute(request);
            HttpEntity entity = response.getEntity();
            String responseBody = EntityUtils.toString(entity);
            
            if (response.getStatusLine().getStatusCode() == 200) {
                return objectMapper.readValue(responseBody, Map.class);
            }
        } catch (Exception e) {
            logger.error("Error getting model info", e);
        }
        
        return Map.of("error", "Unable to retrieve model information");
    }
    
    /**
     * Create payload for API request
     */
    private Map<String, Object> createPayload(Transaction transaction) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("transaction_id", transaction.getTransactionId());
        payload.put("amount", transaction.getAmount().doubleValue());
        payload.put("hour", transaction.getHour());
        payload.put("merchant_category", transaction.getMerchantCategory());
        payload.put("day_of_week", transaction.getDayOfWeek());
        payload.put("customer_age", transaction.getCustomerAge());
        payload.put("days_since_last_transaction", transaction.getDaysSinceLastTransaction());
        payload.put("is_weekend", transaction.getIsWeekend());
        
        return payload;
    }
    
    /**
     * Parse single prediction response from API
     */
    private FraudPrediction parsePredictionResponse(String responseBody, Transaction transaction) 
            throws JsonProcessingException {
        JsonNode responseJson = objectMapper.readTree(responseBody);
        JsonNode prediction = responseJson.get("prediction");
        
        FraudPrediction result = new FraudPrediction();
        result.setTransactionId(transaction.getTransactionId());
        result.setFraud(prediction.get("is_fraud").asBoolean());
        result.setFraudProbability(prediction.get("fraud_probability").asDouble());
        result.setRiskLevel(prediction.get("risk_level").asText());
        result.setModelUsed(prediction.get("model_used").asText());
        result.setInputTransaction(transaction);
        
        return result;
    }
    
    /**
     * Parse batch prediction response from API
     */
    private List<FraudPrediction> parseBatchPredictionResponse(String responseBody, 
                                                              List<Transaction> transactions) 
            throws JsonProcessingException {
        List<FraudPrediction> results = new ArrayList<>();
        JsonNode responseJson = objectMapper.readTree(responseBody);
        JsonNode resultsList = responseJson.get("results");
        
        for (JsonNode resultNode : resultsList) {
            int transactionIndex = resultNode.get("transaction_index").asInt();
            Transaction transaction = transactions.get(transactionIndex);
            
            if (resultNode.has("error")) {
                results.add(createFallbackPrediction(transaction, 
                    resultNode.get("error").asText()));
            } else {
                JsonNode prediction = resultNode.get("prediction");
                FraudPrediction result = new FraudPrediction();
                result.setTransactionId(transaction.getTransactionId());
                result.setFraud(prediction.get("is_fraud").asBoolean());
                result.setFraudProbability(prediction.get("fraud_probability").asDouble());
                result.setRiskLevel(prediction.get("risk_level").asText());
                result.setModelUsed(prediction.get("model_used").asText());
                result.setInputTransaction(transaction);
                results.add(result);
            }
        }
        
        return results;
    }
    
    /**
     * Create fallback prediction when API is unavailable
     */
    private FraudPrediction createFallbackPrediction(Transaction transaction, String reason) {
        FraudPrediction fallback = new FraudPrediction();
        fallback.setTransactionId(transaction.getTransactionId());
        
        // Simple rule-based fallback logic
        boolean suspiciousByRules = isSuspiciousByRules(transaction);
        
        fallback.setFraud(suspiciousByRules);
        fallback.setFraudProbability(suspiciousByRules ? 0.8 : 0.2);
        fallback.setRiskLevel(suspiciousByRules ? "High" : "Low");
        fallback.setModelUsed("fallback-rules");
        fallback.setReason(reason);
        fallback.setInputTransaction(transaction);
        
        return fallback;
    }
    
    /**
     * Simple rule-based fraud detection fallback
     */
    private boolean isSuspiciousByRules(Transaction transaction) {
        // High amount transactions
        if (transaction.getAmount().compareTo(new BigDecimal("1000")) > 0) {
            return true;
        }
        
        // Night time transactions
        if (transaction.getHour() >= 23 || transaction.getHour() <= 5) {
            return true;
        }
        
        // Online transactions with high amounts
        if ("online".equals(transaction.getMerchantCategory()) && 
            transaction.getAmount().compareTo(new BigDecimal("500")) > 0) {
            return true;
        }
        
        // Multiple transactions in short time (same day)
        if (transaction.getDaysSinceLastTransaction() == 0 && 
            transaction.getAmount().compareTo(new BigDecimal("200")) > 0) {
            return true;
        }
        
        return false;
    }
}