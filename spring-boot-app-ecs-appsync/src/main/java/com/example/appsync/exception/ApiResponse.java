package com.example.appsync.exception;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Standardized API response format
 * @param <T> Type of data being returned
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {
    /**
     * Response status: SUCCESS or ERROR
     */
    private String status;
    
    /**
     * Response message
     */
    private String message;
    
    /**
     * Response data payload
     */
    private T data;
    
    /**
     * Error code (only present for error responses)
     */
    private String errorCode;
    
    /**
     * Creates a successful response
     * 
     * @param message Success message
     * @param data Response data
     */
    public ApiResponse(String message, T data) {
        this.status = "SUCCESS";
        this.message = message;
        this.data = data;
    }
    
    /**
     * Creates an error response
     * 
     * @param message Error message
     * @param errorCode Error code
     */
    public static <T> ApiResponse<T> error(String message, String errorCode) {
        ApiResponse<T> response = new ApiResponse<>();
        response.setStatus("ERROR");
        response.setMessage(message);
        response.setErrorCode(errorCode);
        return response;
    }
    
    /**
     * Creates a success response
     * 
     * @param message Success message
     * @param data Response data
     * @return Success response
     */
    public static <T> ApiResponse<T> success(String message, T data) {
        return new ApiResponse<>("SUCCESS", message, data, null);
    }
} 