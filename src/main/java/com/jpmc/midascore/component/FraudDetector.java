package com.jpmc.midascore.component;

import com.jpmc.midascore.foundation.FraudProperties;
import com.jpmc.midascore.foundation.Transaction;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.Map;

@Component
public class FraudDetector {
    private final FraudProperties fraudProperties;

    // Simple in-memory window counters keyed by senderId. For demo only.
    private final Map<Long, Deque<Long>> senderToTimestamps = new HashMap<>();

    public static class FraudScoreResult {
        private final float riskScore;
        private final boolean flagged;
        private final String reason;

        public FraudScoreResult(float riskScore, boolean flagged, String reason) {
            this.riskScore = riskScore;
            this.flagged = flagged;
            this.reason = reason;
        }

        public float getRiskScore() { return riskScore; }
        public boolean isFlagged() { return flagged; }
        public String getReason() { return reason; }
    }

    public FraudDetector(FraudProperties fraudProperties) {
        this.fraudProperties = fraudProperties;
    }

    public synchronized FraudScoreResult score(Transaction txn) {
        float score = 0.0f;
        StringBuilder reasons = new StringBuilder();

        // Rule 1: High amount
        if (txn.getAmount() >= fraudProperties.getHighAmountThreshold()) {
            score += 0.6f;
            reasons.append("high_amount;");
        }

        // Rule 2: Rapid transactions from same sender
        long now = Instant.now().toEpochMilli();
        long windowMillis = (long) (fraudProperties.getRapidTxnWindowMinutes() * 60_000L);
        Deque<Long> q = senderToTimestamps.computeIfAbsent(txn.getSenderId(), k -> new ArrayDeque<>());
        q.addLast(now);
        while (!q.isEmpty() && (now - q.peekFirst()) > windowMillis) {
            q.removeFirst();
        }
        if (q.size() >= fraudProperties.getRapidTxnCountThreshold()) {
            score += 0.5f;
            reasons.append("rapid_txns;");
        }

        // Cap score to [0,1]
        if (score > 1.0f) score = 1.0f;

        boolean flagged = score >= fraudProperties.getRiskScoreThreshold();
        return new FraudScoreResult(score, flagged, reasons.toString());
    }
}