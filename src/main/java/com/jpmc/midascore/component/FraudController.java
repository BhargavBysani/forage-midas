package com.jpmc.midascore.component;

import com.jpmc.midascore.foundation.Transaction;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/fraud")
public class FraudController {
    private final FraudDetector fraudDetector;

    public FraudController(FraudDetector fraudDetector) {
        this.fraudDetector = fraudDetector;
    }

    @PostMapping("/score")
    public ResponseEntity<?> score(@RequestBody Transaction transaction) {
        FraudDetector.FraudScoreResult result = fraudDetector.score(transaction);
        return ResponseEntity.ok(result);
    }
}