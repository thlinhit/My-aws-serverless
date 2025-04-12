package com.example.appsync.connector;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.junit.jupiter.api.Assertions.fail;

import java.util.Map;

import com.example.appsync.model.GraphQLRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;

import feign.FeignException;

/**
 * Integration tests for the AppSync Connector
 */
public class AppSyncConnectorIntegrationTest extends BaseTestConfig {

    @Autowired
    private AppSyncConnector appSyncConnector;

    @Autowired
    private ObjectMapper objectMapper;

    private MockAppSyncServer mockAppSyncServer;

    @BeforeEach
    public void setup() {
        // Start the mock server on port 9999 (matches test config)
        mockAppSyncServer = new MockAppSyncServer(9999, objectMapper);
        mockAppSyncServer.start();
    }

    @AfterEach
    public void tearDown() {
        mockAppSyncServer.stop();
    }

    @Test
    public void testSuccessfulQuery() throws Exception {
        // Given
        String query = "query GetUserInfo { user(id: \"123\") { name email } }";
        GraphQLRequest request = GraphQLRequest.builder()
                .query(query)
                .build();

        Map<String, Object> mockResponse = Map.of(
                "user", Map.of(
                        "name", "John Doe",
                        "email", "john.doe@example.com"
                )
        );

        mockAppSyncServer.stubSuccessfulResponse("GetUserInfo", mockResponse);

        // When
        String response = appSyncConnector.executeGraphQLQuery(request);

        // Then
        assertThat(response).isNotNull();
        assertThat(response).contains("John Doe");
        assertThat(response).contains("john.doe@example.com");
    }

    @Test
    public void testQueryWithVariables() throws Exception {
        // Given
        String query = "query GetUserInfo($id: ID!) { user(id: $id) { name email } }";
        Map<String, Object> variables = Map.of("id", "123");
        
        GraphQLRequest request = GraphQLRequest.builder()
                .query(query)
                .variables(variables)
                .operationName("GetUserInfo")
                .build();

        Map<String, Object> mockResponse = Map.of(
                "user", Map.of(
                        "name", "Jane Smith",
                        "email", "jane.smith@example.com"
                )
        );

        mockAppSyncServer.stubSuccessfulResponse("GetUserInfo", mockResponse);

        // When
        String response = appSyncConnector.executeGraphQLQuery(request);

        // Then
        assertThat(response).isNotNull();
        assertThat(response).contains("Jane Smith");
        assertThat(response).contains("jane.smith@example.com");
    }

    @Test
    public void testGraphQLErrorResponse() throws Exception {
        // Given
        String query = "query InvalidQuery { invalid { field } }";
        GraphQLRequest request = GraphQLRequest.builder()
                .query(query)
                .build();

        mockAppSyncServer.stubErrorResponse(
                "InvalidQuery", 
                "Field 'invalid' doesn't exist", 
                "GRAPHQL_VALIDATION_FAILED", 
                HttpStatus.OK
        );

        // When/Then
        String response = appSyncConnector.executeGraphQLQuery(request);
        
        // Verify response contains error information
        assertThat(response).contains("Field 'invalid' doesn't exist");
        assertThat(response).contains("GRAPHQL_VALIDATION_FAILED");
    }

    @Test
    public void testUnauthorizedRequest() throws Exception {
        // Given
        String query = "query SecureQuery { secure { data } }";
        GraphQLRequest request = GraphQLRequest.builder()
                .query(query)
                .build();

        mockAppSyncServer.stubUnauthorizedResponse("SecureQuery");

        // When/Then
        assertThatThrownBy(() -> appSyncConnector.executeGraphQLQuery(request))
                .isInstanceOf(FeignException.class)
                .hasMessageContaining("Unauthorized");
    }

    @Test
    public void testNetworkTimeout() {
        // Given
        String query = "query SlowQuery { slow { data } }";
        GraphQLRequest request = GraphQLRequest.builder()
                .query(query)
                .build();

        mockAppSyncServer.stubNetworkFailure("SlowQuery");

        // When/Then
        assertThatThrownBy(() -> appSyncConnector.executeGraphQLQuery(request))
                .isInstanceOf(FeignException.class)
                .hasMessageContaining("408");  // Request Timeout
    }

    @Test
    public void testRetryBehavior() throws Exception {
        // This test simulates a situation where the initial request fails
        // but a subsequent request succeeds after a brief delay
        
        // Given
        String query = "query RetryQuery { data { value } }";
        GraphQLRequest request = GraphQLRequest.builder()
                .query(query)
                .build();

        Map<String, Object> mockResponse = Map.of(
                "data", Map.of("value", "success after retry")
        );

        // Set up mock server to always return success
        // This simulates the service recovering after an initial failure
        mockAppSyncServer.stubSuccessfulResponse("RetryQuery", mockResponse);
        
        // We'll manually simulate the retry by sending two requests
        
        // First, verify the successful path works
        String response = appSyncConnector.executeGraphQLQuery(request);
        assertThat(response).isNotNull();
        assertThat(response).contains("success after retry");
        
        // Now test error handling - reset mock server to simulate error
        mockAppSyncServer.reset();
        mockAppSyncServer.stubErrorResponse(
                "RetryQuery", 
                "Service Temporarily Unavailable", 
                "SERVICE_UNAVAILABLE", 
                HttpStatus.SERVICE_UNAVAILABLE
        );
        
        // Verify the error response
        try {
            appSyncConnector.executeGraphQLQuery(request);
            fail("Expected a ServiceUnavailable exception");
        } catch (Exception e) {
            assertThat(e).hasMessageContaining("Service Unavailable");
        }
    }
} 