package com.jpmc.frauddetection.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Configuration class for Fraud Detection Service
 */
@Configuration
public class FraudDetectionConfig implements WebMvcConfigurer {
    
    /**
     * Configure CORS for cross-origin requests
     */
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOriginPatterns("*")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true);
    }
    
    /**
     * Configure OpenAPI documentation
     */
    @Bean
    public OpenAPI fraudDetectionOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Credit Card Fraud Detection API")
                        .description("Advanced machine learning-based fraud detection system for credit card transactions. " +
                                   "Built for the JPMC Advanced Software Engineering Program.")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("JPMC Engineering Team")
                                .email("engineering@jpmc.com"))
                        .license(new License()
                                .name("MIT License")
                                .url("https://opensource.org/licenses/MIT")));
    }
}