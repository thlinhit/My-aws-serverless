"""
Base transformer module defining the transformation strategy interface
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from pyspark.sql import DataFrame


@dataclass
class TransformationResult:
    """Container for transformation results"""
    valid_items: DataFrame
    error_items: DataFrame
    total_count: int
    valid_count: int
    error_count: int


class DataTransformer(ABC):
    """Base class for data transformation strategies"""

    @abstractmethod
    def transform(self, df: DataFrame) -> TransformationResult:
        """
        Transform the DataFrame according to the strategy.

        Args:
            df: Input DataFrame to transform

        Returns:
            TransformationResult containing valid and error items
        """
        pass

    def _partition_dataframe(
        self,
        df: DataFrame,
        error_column: str = "error_info"
    ) -> tuple[DataFrame, DataFrame]:
        """
        Split DataFrame into valid and error partitions.

        Args:
            df: DataFrame to split
            error_column: Column name containing error information

        Returns:
            Tuple of (valid_items_df, error_items_df)
        """
        from pyspark.sql.functions import col

        valid_items_df = df.filter(col(error_column).isNull())
        error_items_df = df.filter(col(error_column).isNotNull())

        return valid_items_df, error_items_df