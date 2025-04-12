# Technical Documentation

## Development Environment

### Prerequisites
- Java 17 or later
- Maven 3.8.x or later
- IDE with Spring Boot support (IntelliJ IDEA, Eclipse, VS Code)
- AWS Account with AppSync configured
- Git for version control

### Local Setup
1. Clone the repository
2. Configure `application.yml` with your AppSync details
3. Run `mvn clean install` to build the project
4. Start the application with `mvn spring-boot:run`

## Technology Stack

### Core Technologies
- **Java 17**: Programming language
- **Spring Boot 3.3.2**: Application framework
- **Spring Cloud OpenFeign**: HTTP client for external API calls
- **Maven**: Build and dependency management

### Frameworks and Libraries
- **Spring Web**: REST API support
- **Spring Cloud Stream**: Event streaming (Kafka integration)
- **OpenFeign**: Declarative REST client
- **OkHttp**: HTTP client used by Feign
- **Jackson**: JSON processing
- **Lombok**: Boilerplate code reduction
- **SLF4J/Logback**: Logging framework

### AWS Services
- **AWS AppSync**: Managed GraphQL service
- **AWS IAM**: Identity and access management (for API key)
- **AWS CloudWatch**: Monitoring and logging (if deployed to AWS)

## Key Technical Decisions

### 1. Clean Architecture
- Separation of concerns with distinct layers
- Dependency inversion through interfaces
- Clear boundaries between components

### 2. Feign Client for AppSync
- Declarative client implementation with annotations
- Automatic error handling and retry mechanism
- Simplified HTTP communication

### 3. Domain-Specific Error Codes
- Structured error codes with prefixes and categories
- Message templates with placeholders
- Mapping to appropriate HTTP status codes

### 4. Request/Response DTOs vs Internal Models
- Clear separation between external and internal representations
- Explicit mapping between layers
- Protection against internal model changes

### 5. Global Exception Handling
- Centralized error processing
- Consistent error response format
- Appropriate status code mapping

## Design Patterns

### 1. Dependency Injection
- Constructor injection via Spring
- Facilitates testing and loose coupling

### 2. Builder Pattern
- Used for creating complex objects like GraphQLRequest
- Implemented via Lombok

### 3. Factory Method
- Static factory methods for creating ApiResponse objects

### 4. Strategy Pattern
- Different implementations of GraphQLService interface possible

### 5. Template Method
- Error handling flow in GlobalExceptionHandler

## Configuration Properties

| Property | Description | Default |
|----------|-------------|---------|
| `aws.appsync.endpoint` | AWS AppSync API endpoint URL | - |
| `aws.appsync.region` | AWS region for AppSync | us-east-1 |
| `aws.appsync.api-key` | Authentication API key | - |
| `feign.client.config.default.connect-timeout` | Connection timeout (ms) | 10000 |
| `feign.client.config.default.read-timeout` | Read timeout (ms) | 60000 |
| `feign.compression.request.enabled` | Enable request compression | true |
| `feign.compression.response.enabled` | Enable response compression | true |

## Technical Constraints

1. **AppSync API Key Authentication**
   - Limited to API key authentication method
   - No support for other authentication methods like IAM or Cognito

2. **Error Handling**
   - Error responses depend on AppSync error format
   - Limited ability to parse detailed GraphQL errors

3. **Timeouts and Performance**
   - Response time depends on AppSync performance
   - Limited by configured timeouts

4. **Limited GraphQL Features**
   - No built-in GraphQL schema validation
   - No direct support for GraphQL subscriptions

5. **Spring Boot Version**
   - Requires Spring Boot 3.x
   - Java 17 minimum requirement 