package com.example.appsync.config;

import feign.Logger;
import feign.Request;
import feign.RequestInterceptor;
import feign.Retryer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

@Configuration
@EnableFeignClients(basePackages = "com.example.appsync.connector")
public class AppSyncConfig {
    @Value("${aws.appsync.api-key}")
    private String apiKey;
    
    @Value("${feign.client.config.default.connect-timeout:10000}")
    private int connectTimeout;
    
    @Value("${feign.client.config.default.read-timeout:60000}")
    private int readTimeout;

    /**
     * Request interceptor for AppSync API calls
     * Adds required headers to every request
     */
    @Bean
    public RequestInterceptor appSyncRequestInterceptor() {
        return requestTemplate -> {
            requestTemplate.header("Content-Type", "application/json");
            requestTemplate.header("x-api-key", apiKey);
        };
    }

    /**
     * Configures retry behavior for Feign client
     */
    @Bean
    public Retryer retryer() {
        // Retry 3 times with 1s initial backoff and max 2s between retries
        return new Retryer.Default(1000, 2000, 3);
    }
    
    /**
     * Configures timeout options for Feign client
     */
    @Bean 
    public Request.Options options() {
        return new Request.Options(
                connectTimeout, TimeUnit.MILLISECONDS,
                readTimeout, TimeUnit.MILLISECONDS,
                true); // Follow redirects
    }
    
    /**
     * Configures logging level for Feign client
     */
    @Bean
    Logger.Level feignLoggerLevel() {
        // BASIC logs only the request method and URL and the response status code and execution time
        return Logger.Level.BASIC;
    }
} 