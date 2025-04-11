package com.example.appsync.connector;

import com.example.appsync.model.GraphQLRequest;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

/**
 * Feign client for AWS AppSync GraphQL API
 * This client is used to send GraphQL requests to the AppSync endpoint
 */
@FeignClient(name = "appSyncConnector", url = "${aws.appsync.endpoint}")
public interface AppSyncConnector {

    /**
     * Executes a GraphQL query against the AppSync API
     * 
     * @param request The GraphQL request object
     * @return The GraphQL response as a String
     */
    @PostMapping
    String executeGraphQLQuery(@RequestBody GraphQLRequest request);
} 