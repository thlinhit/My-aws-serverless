package com.example.appsync.service;

import com.example.appsync.connector.AppSyncConnector;
import com.example.appsync.dto.GraphQLRequestDto;
import com.example.appsync.exception.domain.DomainCode;
import com.example.appsync.exception.domain.DomainException;
import com.example.appsync.model.GraphQLRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class AppSyncService implements GraphQLService {

    private final AppSyncConnector appSyncConnector;

    /**
     * Executes a GraphQL query using the AppSync client
     * 
     * @param requestDto The GraphQL request DTO
     * @return The GraphQL response as a String
     */
    @Override
    public String executeGraphQLQuery(GraphQLRequestDto requestDto) {
        log.info("Executing GraphQL query using Feign client");
        validateRequest(requestDto);
        
        try {
            GraphQLRequest graphQLRequest = mapToGraphQLRequest(requestDto);
            return appSyncConnector.executeGraphQLQuery(graphQLRequest);
        } catch (Exception e) {
            log.error("Error executing GraphQL query: {}", e.getMessage(), e);
            throw new DomainException(DomainCode.GRAPHQL_EXECUTION_ERROR, e.getMessage());
        }
    }
    
    /**
     * Validates the GraphQL request
     * 
     * @param requestDto The GraphQL request DTO to validate
     */
    private void validateRequest(GraphQLRequestDto requestDto) {
        if (requestDto == null) {
            throw new DomainException(DomainCode.VALIDATION_ERROR, "graphQL, the request must not null");
        }
        
        if (requestDto.getQuery() == null || requestDto.getQuery().trim().isEmpty()) {
            throw new DomainException(DomainCode.VALIDATION_ERROR, "graphQL, the request must not empty");
        }
        
        if (requestDto.getOperationName() != null && requestDto.getOperationName().trim().isEmpty()) {
            throw new DomainException(DomainCode.GRAPHQL_INVALID_OPERATION, requestDto.getOperationName());
        }
    }
    
    /**
     * Maps the DTO to the model object
     * 
     * @param requestDto The GraphQL request DTO
     * @return The GraphQLRequest model object
     */
    private GraphQLRequest mapToGraphQLRequest(GraphQLRequestDto requestDto) {
        return GraphQLRequest.builder()
                .query(requestDto.getQuery())
                .variables(requestDto.getVariables())
                .operationName(requestDto.getOperationName())
                .build();
    }
} 