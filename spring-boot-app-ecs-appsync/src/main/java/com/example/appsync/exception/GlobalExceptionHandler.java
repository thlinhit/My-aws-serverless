package com.example.appsync.exception;

import com.example.appsync.exception.domain.DomainCode;
import com.example.appsync.exception.domain.DomainException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Map<DomainCode, HttpStatus> STATUS_MAPPING = new HashMap<>();
    
    static {
        // Map domain codes to HTTP status codes
        // General errors
        STATUS_MAPPING.put(DomainCode.UNKNOWN_ERROR, HttpStatus.INTERNAL_SERVER_ERROR);
        
        // GraphQL errors
        STATUS_MAPPING.put(DomainCode.GRAPHQL_NULL_REQUEST, HttpStatus.BAD_REQUEST);
        STATUS_MAPPING.put(DomainCode.GRAPHQL_EMPTY_QUERY, HttpStatus.BAD_REQUEST);
        STATUS_MAPPING.put(DomainCode.GRAPHQL_EXECUTION_ERROR, HttpStatus.BAD_REQUEST);
        STATUS_MAPPING.put(DomainCode.GRAPHQL_INVALID_OPERATION, HttpStatus.BAD_REQUEST);
        
        // API errors
        STATUS_MAPPING.put(DomainCode.API_BAD_REQUEST, HttpStatus.BAD_REQUEST);
        STATUS_MAPPING.put(DomainCode.API_UNAUTHORIZED, HttpStatus.UNAUTHORIZED);
        STATUS_MAPPING.put(DomainCode.API_FORBIDDEN, HttpStatus.FORBIDDEN);
        STATUS_MAPPING.put(DomainCode.API_NOT_FOUND, HttpStatus.NOT_FOUND);
        STATUS_MAPPING.put(DomainCode.API_METHOD_NOT_ALLOWED, HttpStatus.METHOD_NOT_ALLOWED);
        STATUS_MAPPING.put(DomainCode.API_CONFLICT, HttpStatus.CONFLICT);
        
        // AppSync Integration errors
        STATUS_MAPPING.put(DomainCode.APPSYNC_CONNECTION_ERROR, HttpStatus.SERVICE_UNAVAILABLE);
        STATUS_MAPPING.put(DomainCode.APPSYNC_AUTHENTICATION_ERROR, HttpStatus.UNAUTHORIZED);
        STATUS_MAPPING.put(DomainCode.APPSYNC_RATE_LIMIT_EXCEEDED, HttpStatus.TOO_MANY_REQUESTS);
        
        // Validation errors
        STATUS_MAPPING.put(DomainCode.VALIDATION_ERROR, HttpStatus.BAD_REQUEST);
        STATUS_MAPPING.put(DomainCode.INVALID_INPUT_FORMAT, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(DomainException.class)
    public ResponseEntity<ApiResponse<?>> handleDomainException(DomainException ex) {
        DomainCode code = ex.getDomainCode();
        String errorCode = code.getFullCode();
        String message = ex.getMessage();
        
        log.error("Domain error [{}]: {}", errorCode, message, ex);
        
        HttpStatus status = STATUS_MAPPING.getOrDefault(code, HttpStatus.INTERNAL_SERVER_ERROR);
        ApiResponse<?> response = ApiResponse.error(message, errorCode);
        
        return new ResponseEntity<>(response, status);
    }

    @ExceptionHandler(GraphQLExecutionException.class)
    public ResponseEntity<ApiResponse<?>> handleGraphQLExecutionException(GraphQLExecutionException ex) {
        log.error("GraphQL execution error: {}", ex.getMessage(), ex);
        
        ApiResponse<?> response = ApiResponse.error(ex.getMessage(), "LEGACY-ERROR");
        return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ApiResponse<?>> handleIllegalArgumentException(IllegalArgumentException ex) {
        log.error("Invalid argument: {}", ex.getMessage(), ex);
        
        ApiResponse<?> response = ApiResponse.error(ex.getMessage(), "INVALID-ARGUMENT");
        return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<?>> handleGenericException(Exception ex) {
        log.error("Unexpected error: {}", ex.getMessage(), ex);
        
        ApiResponse<?> response = ApiResponse.error("An unexpected error occurred", "SYSTEM-ERROR");
        return new ResponseEntity<>(response, HttpStatus.INTERNAL_SERVER_ERROR);
    }
} 