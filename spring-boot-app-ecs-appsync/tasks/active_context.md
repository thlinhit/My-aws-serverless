# Active Context

## Current Development Focus

### Current Sprint Goals
1. ✓ Complete integration testing for AppSync connector
2. Add API documentation with Swagger/OpenAPI
3. Improve error handling for network issues
4. Address code review feedback

### Active Tasks
1. ✓ Writing integration tests for the AppSync connector
2. ✓ Setting up a mock AppSync server for testing
3. Implementing OpenAPI documentation
4. ✓ Adding detailed error handling for network errors

## Recent Changes

### Last Completed Milestone
Basic functionality of the AppSync integration with error handling is complete. The application can:
- Accept GraphQL requests via REST endpoint
- Transform and forward requests to AWS AppSync
- Handle and report errors with domain-specific codes
- Configure timeout and retry behavior

### Latest Code Changes
1. Added integration tests for the AppSync connector
2. Created mock AppSync server using WireMock for testing
3. Implemented tests for various scenarios (successful queries, errors, timeouts, retries)
4. Fixed dependency issues for WireMock by using standalone version
5. Improved test reliability by making them more deterministic
6. Added test configuration with separate application-test.yml
7. Added GlobalExceptionHandler for centralized error handling
8. Implemented DomainException with error code mapping
9. Created standardized ApiResponse format
10. Added validation for GraphQL requests
11. Configured logging for requests and responses

## Ongoing Discussions

### Technical Decisions
- **Decision Needed**: Whether to implement a caching layer for frequently used queries
- **Decision Needed**: How to handle GraphQL schema validation
- **Decision Needed**: Whether to support additional AWS authentication methods

### Known Limitations
- Only supports API key authentication for AppSync
- Limited GraphQL error parsing
- No subscription support

## Next Steps

### Immediate Actions
1. ✓ Finish the integration tests for the AppSync connector
2. ✓ Implement proper error handling for network issues
3. Add OpenAPI documentation for the REST endpoint
4. ✓ Create a mock server for testing

### Blocking Issues
- ✓ Need AWS AppSync test environment for integration testing (addressed by using WireMock)
- Waiting for decision on additional authentication methods

## Environment Setup

### Development Environment
- Spring Boot 3.3.2
- Java 17
- Maven 3.8+
- Local AWS configuration for testing

### Testing Resources
- Mock GraphQL server being set up
- Test cases defined for positive and negative scenarios
- Need to configure test AWS credentials 