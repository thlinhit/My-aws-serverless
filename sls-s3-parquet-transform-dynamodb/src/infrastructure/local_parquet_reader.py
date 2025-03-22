"""
Parquet file reader service in the infrastructure layer.
This service handles the technical details of reading Parquet files using PySpark.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from pyspark.sql import SparkSession, DataFrame

from infrastructure.logger import logger


class LocalParquetReader:
    """Service for reading Parquet files with proper error handling and logging."""

    def __init__(self, project_root: Optional[Path] = None, spark: Optional[SparkSession] = None):
        """
        Initialize the ParquetReader.

        Args:
            project_root: Optional project root path. If not provided, will be determined automatically.
            spark: Optional existing SparkSession. If not provided, a new one will be created.
        """
        self.project_root = project_root or self._get_project_root()
        self.spark = spark or self._create_spark_session()

    @staticmethod
    def _get_project_root() -> Path:
        """
        Get the project root directory (2 levels up from this file).

        Returns:
            Path: The project root directory path
        """
        current_file = Path(__file__).resolve()
        return current_file.parent.parent.parent

    @staticmethod
    def _create_spark_session() -> SparkSession:
        """
        Create a SparkSession for DataFrame operations with optimized configuration.

        Returns:
            SparkSession: Configured SparkSession instance
        """
        return (SparkSession.builder
                .appName("ParquetReader")
                .config("spark.driver.host", "localhost")
                .config("spark.driver.bindAddress", "localhost")
                # Performance optimizations
                .config("spark.sql.shuffle.partitions", "2")
                .config("spark.default.parallelism", "2")
                .config("spark.sql.files.maxPartitionBytes", "128MB")
                .config("spark.sql.adaptive.enabled", "true")
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
                .config("spark.sql.adaptive.skewJoin.enabled", "true")
                .getOrCreate())

    def read_parquet(self, file_path: str) -> DataFrame:
        """
        Read a Parquet file from the project root directory.

        Args:
            file_path: Path to the Parquet file to read (relative to project root)

        Returns:
            DataFrame: The loaded Parquet data as a Spark DataFrame

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If there's an error reading the file
        """
        input_file = self.project_root / file_path

        if not input_file.exists():
            logger.error(f"Input file not found at: {input_file}")
            logger.info(f"Current working directory: {Path.cwd()}")
            logger.info(f"Project root directory: {self.project_root}")
            raise FileNotFoundError(f"Parquet file not found at: {input_file}")

        try:
            logger.info(f"Reading Parquet file from: {input_file}")

            # Use dataframe hints for better partition handling
            df = (self.spark.read
                  .option("mergeSchema", "true")  # Handle schema evolution
                  .parquet(str(input_file)))

            # Log basic information about the data
            # Note: df.count() is an expensive operation, so we capture it once
            row_count = df.count()
            logger.info(
                f"Successfully read Parquet file",
                extra={
                    "file_path": str(input_file),
                    "row_count": row_count,
                    "columns": df.columns,
                    "schema": str(df.schema)
                }
            )

            return df

        except Exception as e:
            logger.error(
                f"Error reading Parquet file",
                extra={
                    "file_path": str(input_file),
                    "error": str(e)
                }
            )
            raise ValueError(f"Failed to read Parquet file: {str(e)}")

    def get_data_info(self, df: DataFrame) -> Dict[str, Any]:
        """
        Get basic information about the Spark DataFrame using pure PySpark methods.

        Args:
            df: The Spark DataFrame to analyze

        Returns:
            dict: Dictionary containing basic information about the data
        """
        # Get row count
        row_count = df.count()

        # Get column information
        columns = df.columns
        column_count = len(columns)

        # Get schema information
        schema = str(df.schema)

        # Get sample data (first 5 rows)
        sample_data = df.limit(5).collect()
        sample_dict = {
            str(i): {col_name: str(row[col_name]) for col_name in columns}
            for i, row in enumerate(sample_data)
        }

        # Get basic statistics for numeric columns
        stats_dict = {}
        if df.count() > 0:
            # Get summary statistics for numeric columns using a more efficient approach
            numeric_cols = [field.name for field in df.schema if field.dataType.simpleString() in ['int', 'double', 'float', 'decimal']]
            if numeric_cols:
                # Use describe() which is more efficient than summary() for basic stats
                stats_df = df.select(numeric_cols).describe()
                stats_dict = {
                    row['summary']: {col: row[col] for col in numeric_cols}
                    for row in stats_df.collect()
                }

        # Return comprehensive dictionary with data information
        return {
            "row_count": row_count,
            "column_count": column_count,
            "columns": columns,
            "schema": schema,
            "sample": sample_dict,
            "statistics": stats_dict
        }

    def __del__(self):
        """Clean up Spark session when the reader is destroyed."""
        if hasattr(self, 'spark') and self.spark is not None:
            self.spark.stop()