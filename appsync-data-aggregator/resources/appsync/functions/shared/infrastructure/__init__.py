# """
# Infrastructure Layer

# This layer contains all the implementation details that interact with external systems,
# frameworks, and libraries. It implements the interfaces defined in the domain layer
# and provides concrete implementations for repositories, clients, and services.

# The infrastructure layer is responsible for:
# - Database connections and operations
# - External API clients
# - File system operations
# - Logging mechanisms
# - Framework-specific configurations

# This separation ensures that the domain logic remains pure and
# free from infrastructure concerns, following DDD principles.
# """

# from infrastructure.dynamodb_client import DynamoDBClient, DynamoDBWriteResult
# from infrastructure.local_parquet_reader import LocalParquetReader
# from infrastructure.logger import logger

# __all__ = [
#     'DynamoDBClient',
#     'DynamoDBWriteResult',
#     'LocalParquetReader',
#     'logger',
# ]