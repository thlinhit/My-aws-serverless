# AppSync Integration Tests

This directory contains integration tests for the Spring Boot AppSync Integration project, with a particular focus on testing the AppSync Connector.

## Overview

The integration tests verify:

1. The connector can successfully send GraphQL queries to AppSync
2. Variable substitution in GraphQL queries works correctly
3. Error responses from AppSync are handled properly
4. Authentication failures are properly reported
5. Network timeouts are handled correctly
6. Retry mechanism works for transient server errors

## Test Implementation

### Mock AppSync Server

Tests use WireMock to create a mock AppSync server that:

- Receives GraphQL requests
- Validates headers including the API key
- Returns appropriate responses based on test scenarios
- Simulates error conditions and network failures

The mock server starts before each test on port 9999 (configured in `application-test.yml`).

### Test Classes

- **BaseTestConfig** - Common configuration for all integration tests
- **MockAppSyncServer** - Utility to create a mock AppSync server
- **AppSyncConnectorIntegrationTest** - Tests for the AppSync connector

## Running the Tests

To run all integration tests:

```bash
mvn test
```

To run a specific test class:

```bash
mvn -Dtest=AppSyncConnectorIntegrationTest test
```

To run a specific test method:

```bash
mvn -Dtest=AppSyncConnectorIntegrationTest#testSuccessfulQuery test
```

## Test Configuration

The test environment uses:

- Custom application-test.yml with test-specific configuration
- WireMock for simulating the AppSync API
- Spring's test framework for integration testing
- AssertJ for fluent assertions

## Coverage

These tests focus on the integration with AWS AppSync and verify:

1. **Functional Requirements**
   - Correct GraphQL query execution
   - Proper handling of variables and operation names
   - Error handling for various failure scenarios

2. **Non-Functional Requirements**
   - Timeout behavior
   - Retry mechanism for transient errors
   - Authentication handling 