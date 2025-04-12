package com.example.appsync.connector;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.tomakehurst.wiremock.WireMockServer;
import com.github.tomakehurst.wiremock.client.WireMock;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;

import java.util.Map;

import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static com.github.tomakehurst.wiremock.core.WireMockConfiguration.options;

/**
 * Mock server for AppSync API to use in integration tests
 */
public class MockAppSyncServer {
    private final WireMockServer wireMockServer;
    private final ObjectMapper objectMapper;
    private static final String API_KEY = "test-api-key";

    public MockAppSyncServer(int port, ObjectMapper objectMapper) {
        this.wireMockServer = new WireMockServer(options().port(port));
        this.objectMapper = objectMapper;
    }

    /**
     * Start the mock server
     */
    public void start() {
        wireMockServer.start();
        WireMock.configureFor("localhost", wireMockServer.port());
    }

    /**
     * Stop the mock server
     */
    public void stop() {
        wireMockServer.stop();
    }

    /**
     * Reset the mock server state
     */
    public void reset() {
        wireMockServer.resetAll();
    }

    /**
     * Stub successful response for a GraphQL query
     * 
     * @param queryContains    Substring contained in the query
     * @param responseData     Response data to return
     */
    public void stubSuccessfulResponse(String queryContains, Map<String, Object> responseData) throws Exception {
        Map<String, Object> response = Map.of("data", responseData);
        
        wireMockServer.stubFor(post(urlEqualTo("/"))
                .withHeader("Content-Type", containing("application/json"))
                .withHeader("x-api-key", equalTo(API_KEY))
                .withRequestBody(containing(queryContains))
                .willReturn(aResponse()
                        .withStatus(HttpStatus.OK.value())
                        .withHeader("Content-Type", MediaType.APPLICATION_JSON_VALUE)
                        .withBody(objectMapper.writeValueAsString(response))));
    }

    /**
     * Stub error response for a GraphQL query
     * 
     * @param queryContains    Substring contained in the query
     * @param errorMessage     Error message to return
     * @param errorCode        Error code to return
     * @param httpStatus       HTTP status code to return
     */
    public void stubErrorResponse(String queryContains, String errorMessage, String errorCode, HttpStatus httpStatus) throws Exception {
        Map<String, Object> error = Map.of(
                "message", errorMessage,
                "errorType", "GraphQLError",
                "errorCode", errorCode
        );
        
        Map<String, Object> response = Map.of("errors", new Object[] { error });
        
        wireMockServer.stubFor(post(urlEqualTo("/"))
                .withHeader("Content-Type", containing("application/json"))
                .withHeader("x-api-key", equalTo(API_KEY))
                .withRequestBody(containing(queryContains))
                .willReturn(aResponse()
                        .withStatus(httpStatus.value())
                        .withHeader("Content-Type", MediaType.APPLICATION_JSON_VALUE)
                        .withBody(objectMapper.writeValueAsString(response))));
    }

    /**
     * Stub network failure
     * 
     * @param queryContains    Substring contained in the query
     */
    public void stubNetworkFailure(String queryContains) {
        wireMockServer.stubFor(post(urlEqualTo("/"))
                .withHeader("Content-Type", containing("application/json"))
                .withRequestBody(containing(queryContains))
                .willReturn(aResponse().withStatus(HttpStatus.REQUEST_TIMEOUT.value())));
    }

    /**
     * Stub unauthorized response
     * 
     * @param queryContains    Substring contained in the query
     */
    public void stubUnauthorizedResponse(String queryContains) throws Exception {
        Map<String, Object> error = Map.of(
                "message", "Unauthorized: Invalid API key",
                "errorType", "UnauthorizedException"
        );
        
        wireMockServer.stubFor(post(urlEqualTo("/"))
                .withRequestBody(containing(queryContains))
                .willReturn(aResponse()
                        .withStatus(HttpStatus.UNAUTHORIZED.value())
                        .withHeader("Content-Type", MediaType.APPLICATION_JSON_VALUE)
                        .withBody(objectMapper.writeValueAsString(error))));
    }
} 