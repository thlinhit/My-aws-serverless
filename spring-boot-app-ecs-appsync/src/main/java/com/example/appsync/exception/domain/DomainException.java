package com.example.appsync.exception.domain;

import lombok.Getter;

/**
 * Domain-specific exception with error codes and formatted messages
 */
@Getter
public class DomainException extends RuntimeException {
    private final DomainCode domainCode;
    private final transient Object[] args;
    
    /**
     * Creates a new DomainException with the given domain code and arguments
     * 
     * @param domainCode The domain-specific error code
     * @param args Arguments to substitute placeholders in message template
     */
    public DomainException(DomainCode domainCode, Object... args) {
        this(domainCode, true, args);
    }
    
    /**
     * Private constructor that allows controlling whether to include stack trace
     * 
     * @param domainCode The domain-specific error code
     * @param includeStackTrace Whether to include stack trace
     * @param args Arguments to substitute placeholders in message template
     */
    private DomainException(DomainCode domainCode, boolean includeStackTrace, Object... args) {
        super(StringPlaceholderUtils.format(domainCode.getMessageTemplate(), args), 
              null, 
              false, 
              includeStackTrace);
        this.domainCode = domainCode;
        this.args = args;
    }
    
    /**
     * Creates a DomainException without stack trace for performance reasons
     * 
     * @param domainCode The domain-specific error code
     * @param args Arguments to substitute placeholders in message template
     * @return A DomainException without stack trace
     */
    public static DomainException withoutStackTrace(DomainCode domainCode, Object... args) {
        return new DomainException(domainCode, false, args);
    }
    
    /**
     * Gets the value of a specific placeholder from the formatted message
     * 
     * @param placeholder The placeholder name to get the value for
     * @return The value that replaced the placeholder, or the full message if not found
     */
    public Object getValue(String placeholder) {
        var placeholders = StringPlaceholderUtils.getPlaceholders(domainCode.getMessageTemplate());
        if (placeholders.isEmpty() || !placeholders.contains(placeholder)) {
            return getMessage();
        }
        return args[placeholders.indexOf(placeholder)];
    }
} 