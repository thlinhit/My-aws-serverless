"""
Tests for the domain error exception
"""

from exception.domain_code import DomainCode, convert_pattern
from exception.domain_error import DomainError


class TestDomainError:
    """Test suite for the domain error exception"""

    def test_convert_pattern(self):
        """Test converting a pattern with placeholders"""
        # Test with a simple pattern
        pattern = "Error with {key}"
        result = convert_pattern(pattern)
        assert result == "Error with key='{key}'"

        # Test with multiple placeholders
        pattern = "Error with {key1} and {key2}"
        result = convert_pattern(pattern)
        assert result == "Error with key1='{key1}' and key2='{key2}'"

        # Test with no placeholders
        pattern = "Error with no placeholders"
        result = convert_pattern(pattern)
        assert result == pattern

    def test_domain_error_creation(self):
        """Test creating a domain error"""
        # Create a domain error
        error = DomainError(
            DomainCode.DYNAMODB_WRITE_FAILURE,
            failed_count=5,
            total_count=100,
            table_name="test_table",
            data_type="LOAN_APPLICATION"
        )

        # Verify the error properties
        assert error.domain_code == DomainCode.DYNAMODB_WRITE_FAILURE
        assert error.values["failed_count"] == 5
        assert error.values["total_count"] == 100
        assert error.values["table_name"] == "test_table"
        assert error.values["data_type"] == "LOAN_APPLICATION"

        # Verify the error message
        assert str(error.domain_code) in error.message
        assert "5" in error.message
        assert "100" in error.message
        assert "test_table" in error.message
        assert "LOAN_APPLICATION" in error.message

    def test_get_value(self):
        """Test getting a value from the error values"""
        # Create a domain error
        error = DomainError(
            DomainCode.DYNAMODB_WRITE_FAILURE,
            data_type="LOAN_APPLICATION",
            table_name="test",
            failed_count=5,
            total_count=100
        )

        # Get existing values
        assert error.get_value("failed_count") == 5
        assert error.get_value("total_count") == 100

        # Get non-existent value with default
        assert error.get_value("non_existent", "default") == "default"

        # Get non-existent value without default
        assert error.get_value("non_existent") is None

    def test_to_dict(self):
        """Test converting the error to a dictionary"""
        # Create a domain error
        error = DomainError(
            DomainCode.DYNAMODB_WRITE_FAILURE,
            data_type="LOAN_APPLICATION",
            table_name="test",
            failed_count=5,
            total_count=100
        )

        # Convert to dictionary
        result = error.to_dict()

        # Verify the dictionary
        assert isinstance(result, dict)
        assert result["code"] == error.domain_code.code
        assert result["message"] == error.message
        assert result["values"] == error.values
        assert result["values"]["failed_count"] == 5
        assert result["values"]["total_count"] == 100