package com.jpmc.midascore.foundation;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "fraud")
public class FraudProperties {
    private float highAmountThreshold = 1000.0f;
    private float rapidTxnWindowMinutes = 5.0f;
    private int rapidTxnCountThreshold = 3;
    private float riskScoreThreshold = 0.7f;

    public float getHighAmountThreshold() { return highAmountThreshold; }
    public void setHighAmountThreshold(float highAmountThreshold) { this.highAmountThreshold = highAmountThreshold; }

    public float getRapidTxnWindowMinutes() { return rapidTxnWindowMinutes; }
    public void setRapidTxnWindowMinutes(float rapidTxnWindowMinutes) { this.rapidTxnWindowMinutes = rapidTxnWindowMinutes; }

    public int getRapidTxnCountThreshold() { return rapidTxnCountThreshold; }
    public void setRapidTxnCountThreshold(int rapidTxnCountThreshold) { this.rapidTxnCountThreshold = rapidTxnCountThreshold; }

    public float getRiskScoreThreshold() { return riskScoreThreshold; }
    public void setRiskScoreThreshold(float riskScoreThreshold) { this.riskScoreThreshold = riskScoreThreshold; }
}
