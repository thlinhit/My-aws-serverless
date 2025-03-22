"""
Tests for the local Parquet reader
"""
import pytest
from pathlib import Path
from unittest.mock import patch

from infrastructure.local_parquet_reader import LocalParquetReader


class TestLocalParquetReader:
    """Test suite for the local Parquet reader"""

    @pytest.fixture
    def reader(self, spark):
        """Create a local Parquet reader with a test Spark session"""
        return LocalParquetReader(spark=spark)

    def test_get_project_root(self):
        """Test getting the project root directory"""
        # Get the project root
        root = LocalParquetReader._get_project_root()

        # Verify it's a Path object
        assert isinstance(root, Path)

        # Verify it exists
        assert root.exists()

    def test_read_parquet(self, reader, sample_parquet_file):
        """Test reading a Parquet file"""
        # Read the Parquet file
        df = reader.read_parquet(str(sample_parquet_file))

        # Verify the DataFrame
        assert df is not None
        assert not df.isEmpty()
        assert df.count() == 2
        assert "customer_id" in df.columns
        assert "application_id" in df.columns

    def test_read_parquet_file_not_found(self, reader):
        """Test reading a non-existent Parquet file"""
        # Try to read a non-existent file
        with pytest.raises(FileNotFoundError) as excinfo:
            reader.read_parquet("non_existent_file.parquet")

        # Verify the exception message
        assert "not found" in str(excinfo.value)
