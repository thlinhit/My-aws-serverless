package com.example.appsync.controller;

import com.example.appsync.dto.GraphQLRequestDto;
import com.example.appsync.exception.ApiResponse;
import com.example.appsync.exception.domain.DomainCode;
import com.example.appsync.exception.domain.DomainException;
import com.example.appsync.service.GraphQLService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class AppSyncController {

    private final GraphQLService graphQLService;

    /**
     * Executes a GraphQL query and returns the response
     * 
     * @param requestDto The GraphQL request DTO
     * @return ResponseEntity containing the GraphQL response
     */
    @PostMapping("/graphql")
    public ResponseEntity<ApiResponse<String>> executeGraphQLQuery(@RequestBody GraphQLRequestDto requestDto) {
        log.info("Received GraphQL request: {}", requestDto);
        
        try {
            String response = graphQLService.executeGraphQLQuery(requestDto);
            return ResponseEntity.ok(ApiResponse.success("GraphQL query executed successfully", response));
        } catch (Exception e) {
            // Let the GlobalExceptionHandler handle this
            if (e instanceof DomainException) {
                throw e;
            } else {
                throw new DomainException(DomainCode.UNKNOWN_ERROR);
            }
        }
    }
} 