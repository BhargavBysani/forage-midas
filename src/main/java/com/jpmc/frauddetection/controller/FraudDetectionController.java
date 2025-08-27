package com.jpmc.frauddetection.controller;

import com.jpmc.frauddetection.model.*;
import com.jpmc.frauddetection.service.FraudDetectionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * REST Controller for Credit Card Fraud Detection API
 * JPMC Advanced Software Engineering Program
 */
@RestController
@RequestMapping("/api/v1/fraud-detection")
@Validated
@Tag(name = "Fraud Detection", description = "Credit Card Fraud Detection API")
@CrossOrigin(origins = "*")
public class FraudDetectionController {
    
    private static final Logger logger = LoggerFactory.getLogger(FraudDetectionController.class);
    
    @Autowired
    private FraudDetectionService fraudDetectionService;
    
    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    @Operation(summary = "Health check", description = "Check if the fraud detection service is healthy")
    @ApiResponse(responseCode = "200", description = "Service is healthy")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("service", "fraud-detection-api");
        health.put("timestamp", LocalDateTime.now());
        health.put("ml_api_healthy", fraudDetectionService.isApiHealthy());
        
        return ResponseEntity.ok(health);
    }
    
    /**
     * Predict fraud for a single transaction
     */
    @PostMapping("/predict")
    @Operation(summary = "Predict fraud for single transaction", 
               description = "Analyze a single transaction for fraud detection")
    @ApiResponse(responseCode = "200", description = "Fraud prediction completed successfully")
    @ApiResponse(responseCode = "400", description = "Invalid transaction data")
    public ResponseEntity<FraudPrediction> predictFraud(@Valid @RequestBody Transaction transaction) {
        try {
            logger.info("Received fraud prediction request for transaction: {}", 
                       transaction.getTransactionId());
            
            long startTime = System.currentTimeMillis();
            FraudPrediction prediction = fraudDetectionService.predictFraud(transaction);
            long processingTime = System.currentTimeMillis() - startTime;
            
            logger.info("Fraud prediction completed for transaction {} in {}ms. Result: fraud={}, probability={}", 
                       transaction.getTransactionId(), processingTime, 
                       prediction.isFraud(), prediction.getFraudProbability());
            
            return ResponseEntity.ok(prediction);
            
        } catch (Exception e) {
            logger.error("Error processing fraud prediction for transaction: " + 
                        transaction.getTransactionId(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorPrediction(transaction, e.getMessage()));
        }
    }
    
    /**
     * Predict fraud for multiple transactions
     */
    @PostMapping("/predict/batch")
    @Operation(summary = "Predict fraud for multiple transactions", 
               description = "Analyze multiple transactions for fraud detection")
    @ApiResponse(responseCode = "200", description = "Batch fraud prediction completed successfully")
    @ApiResponse(responseCode = "400", description = "Invalid batch request data")
    public ResponseEntity<BatchPredictionResponse> predictFraudBatch(
            @Valid @RequestBody BatchPredictionRequest request) {
        try {
            logger.info("Received batch fraud prediction request for {} transactions", 
                       request.getTransactions().size());
            
            long startTime = System.currentTimeMillis();
            List<FraudPrediction> predictions = fraudDetectionService
                    .predictFraudBatch(request.getTransactions());
            long processingTime = System.currentTimeMillis() - startTime;
            
            BatchPredictionResponse response = new BatchPredictionResponse(predictions);
            response.setProcessingTimeMs(processingTime);
            
            logger.info("Batch fraud prediction completed for {} transactions in {}ms. " +
                       "Fraudulent: {}/{}", 
                       response.getTotalTransactions(), processingTime,
                       response.getFraudulentTransactions(), response.getTotalTransactions());
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Error processing batch fraud prediction", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorBatchResponse(e.getMessage()));
        }
    }
    
    /**
     * Get model information
     */
    @GetMapping("/model/info")
    @Operation(summary = "Get model information", 
               description = "Get information about the fraud detection model")
    @ApiResponse(responseCode = "200", description = "Model information retrieved successfully")
    public ResponseEntity<Map<String, Object>> getModelInfo() {
        try {
            Map<String, Object> modelInfo = fraudDetectionService.getModelInfo();
            modelInfo.put("service_version", "1.0.0");
            modelInfo.put("timestamp", LocalDateTime.now());
            
            return ResponseEntity.ok(modelInfo);
            
        } catch (Exception e) {
            logger.error("Error retrieving model information", e);
            Map<String, Object> errorInfo = new HashMap<>();
            errorInfo.put("error", "Unable to retrieve model information");
            errorInfo.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorInfo);
        }
    }
    
    /**
     * Get fraud detection statistics
     */
    @GetMapping("/stats")
    @Operation(summary = "Get fraud detection statistics", 
               description = "Get service statistics and metrics")
    @ApiResponse(responseCode = "200", description = "Statistics retrieved successfully")
    public ResponseEntity<Map<String, Object>> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("service_name", "JPMC Fraud Detection Service");
        stats.put("version", "1.0.0");
        stats.put("uptime_since", LocalDateTime.now().minusHours(1)); // Mock uptime
        stats.put("ml_api_status", fraudDetectionService.isApiHealthy() ? "ONLINE" : "OFFLINE");
        stats.put("supported_features", List.of(
            "Single transaction prediction",
            "Batch transaction prediction", 
            "Real-time analysis",
            "Rule-based fallback",
            "Risk level classification"
        ));
        
        return ResponseEntity.ok(stats);
    }
    
    /**
     * Exception handler for validation errors
     */
    @ExceptionHandler(org.springframework.web.bind.MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidationExceptions(
            org.springframework.web.bind.MethodArgumentNotValidException ex) {
        Map<String, Object> errors = new HashMap<>();
        errors.put("error", "Validation failed");
        errors.put("timestamp", LocalDateTime.now());
        
        Map<String, String> fieldErrors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error -> 
            fieldErrors.put(error.getField(), error.getDefaultMessage()));
        
        errors.put("field_errors", fieldErrors);
        
        return ResponseEntity.badRequest().body(errors);
    }
    
    /**
     * Create error prediction for exception cases
     */
    private FraudPrediction createErrorPrediction(Transaction transaction, String errorMessage) {
        FraudPrediction errorPrediction = new FraudPrediction();
        errorPrediction.setTransactionId(transaction.getTransactionId());
        errorPrediction.setFraud(false);
        errorPrediction.setFraudProbability(0.0);
        errorPrediction.setRiskLevel("Unknown");
        errorPrediction.setModelUsed("error-fallback");
        errorPrediction.setReason("Error: " + errorMessage);
        errorPrediction.setInputTransaction(transaction);
        
        return errorPrediction;
    }
    
    /**
     * Create error batch response for exception cases
     */
    private BatchPredictionResponse createErrorBatchResponse(String errorMessage) {
        BatchPredictionResponse errorResponse = new BatchPredictionResponse();
        errorResponse.setTotalTransactions(0);
        errorResponse.setFraudulentTransactions(0);
        errorResponse.setProcessingTimeMs(0);
        
        return errorResponse;
    }
}