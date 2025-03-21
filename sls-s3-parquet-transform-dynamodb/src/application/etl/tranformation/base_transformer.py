from abc import ABC, abstractmethod
from dataclasses import dataclass

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