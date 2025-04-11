package com.example.appsync.exception;

import com.example.appsync.exception.domain.DomainCode;
import com.example.appsync.exception.domain.DomainException;

/**
 * @deprecated Use {@link DomainException} with appropriate {@link DomainCode} instead
 */
@Deprecated
public class GraphQLExecutionException extends RuntimeException {
    public GraphQLExecutionException(String message) {
        super(message);
    }

    public GraphQLExecutionException(String message, Throwable cause) {
        super(message, cause);
    }
} 