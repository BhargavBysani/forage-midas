package com.jpmc.frauddetection.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Transaction model representing a credit card transaction
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class Transaction {
    
    @NotNull(message = "Transaction ID is required")
    private String transactionId;
    
    @NotNull(message = "Amount is required")
    @DecimalMin(value = "0.01", message = "Amount must be greater than 0")
    private BigDecimal amount;
    
    @NotNull(message = "Hour is required")
    @Min(value = 0, message = "Hour must be between 0 and 23")
    @Max(value = 23, message = "Hour must be between 0 and 23")
    private Integer hour;
    
    @NotNull(message = "Merchant category is required")
    @Pattern(regexp = "grocery|gas|restaurant|retail|online", 
             message = "Merchant category must be one of: grocery, gas, restaurant, retail, online")
    private String merchantCategory;
    
    @NotNull(message = "Day of week is required")
    @Min(value = 0, message = "Day of week must be between 0 and 6")
    @Max(value = 6, message = "Day of week must be between 0 and 6")
    private Integer dayOfWeek;
    
    @NotNull(message = "Customer age is required")
    @Min(value = 18, message = "Customer age must be at least 18")
    @Max(value = 120, message = "Customer age must be less than 120")
    private Integer customerAge;
    
    @NotNull(message = "Days since last transaction is required")
    @Min(value = 0, message = "Days since last transaction must be non-negative")
    private Integer daysSinceLastTransaction;
    
    @NotNull(message = "Weekend flag is required")
    @Min(value = 0, message = "Weekend flag must be 0 or 1")
    @Max(value = 1, message = "Weekend flag must be 0 or 1")
    private Integer isWeekend;
    
    private String customerId;
    private String merchantId;
    private LocalDateTime timestamp;
    
    // Default constructor
    public Transaction() {}
    
    // Constructor with required fields
    public Transaction(String transactionId, BigDecimal amount, Integer hour, 
                      String merchantCategory, Integer dayOfWeek, Integer customerAge,
                      Integer daysSinceLastTransaction, Integer isWeekend) {
        this.transactionId = transactionId;
        this.amount = amount;
        this.hour = hour;
        this.merchantCategory = merchantCategory;
        this.dayOfWeek = dayOfWeek;
        this.customerAge = customerAge;
        this.daysSinceLastTransaction = daysSinceLastTransaction;
        this.isWeekend = isWeekend;
        this.timestamp = LocalDateTime.now();
    }
    
    // Getters and Setters
    public String getTransactionId() {
        return transactionId;
    }
    
    public void setTransactionId(String transactionId) {
        this.transactionId = transactionId;
    }
    
    public BigDecimal getAmount() {
        return amount;
    }
    
    public void setAmount(BigDecimal amount) {
        this.amount = amount;
    }
    
    public Integer getHour() {
        return hour;
    }
    
    public void setHour(Integer hour) {
        this.hour = hour;
    }
    
    public String getMerchantCategory() {
        return merchantCategory;
    }
    
    public void setMerchantCategory(String merchantCategory) {
        this.merchantCategory = merchantCategory;
    }
    
    public Integer getDayOfWeek() {
        return dayOfWeek;
    }
    
    public void setDayOfWeek(Integer dayOfWeek) {
        this.dayOfWeek = dayOfWeek;
    }
    
    public Integer getCustomerAge() {
        return customerAge;
    }
    
    public void setCustomerAge(Integer customerAge) {
        this.customerAge = customerAge;
    }
    
    public Integer getDaysSinceLastTransaction() {
        return daysSinceLastTransaction;
    }
    
    public void setDaysSinceLastTransaction(Integer daysSinceLastTransaction) {
        this.daysSinceLastTransaction = daysSinceLastTransaction;
    }
    
    public Integer getIsWeekend() {
        return isWeekend;
    }
    
    public void setIsWeekend(Integer isWeekend) {
        this.isWeekend = isWeekend;
    }
    
    public String getCustomerId() {
        return customerId;
    }
    
    public void setCustomerId(String customerId) {
        this.customerId = customerId;
    }
    
    public String getMerchantId() {
        return merchantId;
    }
    
    public void setMerchantId(String merchantId) {
        this.merchantId = merchantId;
    }
    
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
    
    @Override
    public String toString() {
        return "Transaction{" +
                "transactionId='" + transactionId + '\'' +
                ", amount=" + amount +
                ", hour=" + hour +
                ", merchantCategory='" + merchantCategory + '\'' +
                ", dayOfWeek=" + dayOfWeek +
                ", customerAge=" + customerAge +
                ", daysSinceLastTransaction=" + daysSinceLastTransaction +
                ", isWeekend=" + isWeekend +
                ", customerId='" + customerId + '\'' +
                ", merchantId='" + merchantId + '\'' +
                ", timestamp=" + timestamp +
                '}';
    }
}