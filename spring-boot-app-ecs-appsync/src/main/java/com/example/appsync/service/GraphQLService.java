package com.example.appsync.service;

import com.example.appsync.dto.GraphQLRequestDto;

/**
 * Service interface for GraphQL operations
 */
public interface GraphQLService {
    
    /**
     * Executes a GraphQL query
     * 
     * @param requestDto The GraphQL request DTO
     * @return The GraphQL response as a String
     */
    String executeGraphQLQuery(GraphQLRequestDto requestDto);
} 