package com.example.appsync.exception.domain;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

/**
 * Enum of domain-specific error codes and message templates
 */
@Getter
@RequiredArgsConstructor
public enum DomainCode {
    // General errors - 000-099
    UNKNOWN_ERROR("000", "An unexpected error occurred"),
    
    // GraphQL errors - 100-199
    GRAPHQL_NULL_REQUEST("100", "GraphQL request cannot be null"),
    GRAPHQL_EMPTY_QUERY("101", "GraphQL query cannot be empty"),
    GRAPHQL_EXECUTION_ERROR("102", "Failed to execute GraphQL query: ${message}"),
    GRAPHQL_INVALID_OPERATION("103", "Invalid GraphQL operation: ${operationName}"),
    
    // API errors - 200-299
    API_BAD_REQUEST("200", "Bad request: ${message}"),
    API_UNAUTHORIZED("201", "Unauthorized access: ${message}"),
    API_FORBIDDEN("202", "Access forbidden: ${message}"),
    API_NOT_FOUND("203", "Resource not found: ${resourceType}, ${resourceId}"),
    API_METHOD_NOT_ALLOWED("204", "Method not allowed: ${method}"),
    API_CONFLICT("205", "Resource conflict: ${message}"),
    
    // AppSync Integration errors - 300-399
    APPSYNC_CONNECTION_ERROR("300", "Failed to connect to AppSync: ${endpoint}"),
    APPSYNC_AUTHENTICATION_ERROR("301", "Failed to authenticate with AppSync: ${message}"),
    APPSYNC_RATE_LIMIT_EXCEEDED("302", "AppSync rate limit exceeded"),
    
    // Data validation errors - 400-499
    VALIDATION_ERROR("400", "Validation error, ${message}"),
    INVALID_INPUT_FORMAT("401", "Invalid input format: ${field}, ${expected}, ${actual}");
    
    private final String code;
    private final String messageTemplate;
    
    private static final String PREFIX = "APS";
    
    /**
     * Gets the full error code with prefix
     * @return The prefixed error code
     */
    public String getFullCode() {
        return PREFIX + code;
    }
} 