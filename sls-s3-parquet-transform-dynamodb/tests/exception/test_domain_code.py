"""
Tests for the domain code enumeration
"""
import pytest

from exception.domain_code import DomainCode, convert_pattern


class TestDomainCode:
    """Test suite for the domain code enumeration"""

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

    def test_domain_code_properties(self):
        """Test domain code properties"""
        # Test the UNKNOWN code
        code = DomainCode.UNKNOWN

        # Test string representation
        assert str(code) == code.value

        # Test properties
        assert code.code == code.value
        assert code.external_code == code.value
        assert code.internal_msg is not None

    def test_domain_code_message_formatting(self):
        """Test domain code message formatting"""
        # Test with the NO_DATA_TRANSFORMER_FOUND code
        code = DomainCode.NO_DATA_TRANSFORMER_FOUND

        # Verify the internal message format
        assert "data_type='{data_type}'" in code.internal_msg

        # Test with the DYNAMODB_WRITE_FAILURE code
        code = DomainCode.DYNAMODB_WRITE_FAILURE

        # Verify the internal message format
        assert "failed_count='{failed_count}'" in code.internal_msg
        assert "total_count='{total_count}'" in code.internal_msg
        assert "table_name='{table_name}'" in code.internal_msg
        assert "data_type='{data_type}'" in code.internal_msg