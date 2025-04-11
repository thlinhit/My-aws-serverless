# Spring Boot AppSync Integration with Feign

This project demonstrates integration between a Spring Boot application and AWS AppSync GraphQL API using OpenFeign.

## Prerequisites

- Java 17
- Maven
- AWS Account with AppSync configured

## Configuration

Edit the `application.yaml` file to update the following properties:

```properties
aws.appsync.endpoint=YOUR_APPSYNC_ENDPOINT
aws.appsync.region=YOUR_AWS_REGION
aws.appsync.api-key=YOUR_API_KEY
```

## Architecture

The application follows clean architecture principles with the following components:

- **API Layer**: REST controllers that handle HTTP requests and responses
- **Service Layer**: Business logic with interfaces and implementations 
- **Connetor Layer**: Feign clients for external API communication
- **DTO Layer**: Data Transfer Objects for API requests and responses
- **Model Layer**: Internal data models
- **Exception Layer**: Custom exceptions and global error handling

## Key Components

- **AppSyncClient**: Feign client interface that sends GraphQL requests to AppSync
- **GraphQLService**: Service interface for GraphQL operations
- **AppSyncService**: Implementation of GraphQLService that uses the Feign client
- **AppSyncController**: REST controller with POST endpoint to receive client requests
- **GlobalExceptionHandler**: Handles exceptions and provides consistent error responses

## Build

```bash
mvn clean install
```

## Run

```bash
mvn spring-boot:run
```

## API Usage
``` 


# Curl Example [Do not replace]
```bash
curl --location 'http://localhost:8080/api/graphql' \
--header 'Content-Type: application/json' \
--data '{"query":"query GetCustomerData($customerId: ID!) { \n  getEarliestLoanApplication(customerId: $customerId) {\n    accepted_amount\n    application_id\n  }\n}","variables":{"customerId":"12345678"}}'
```