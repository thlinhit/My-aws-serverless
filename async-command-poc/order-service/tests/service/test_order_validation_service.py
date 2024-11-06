# tests/test_order_validation_service.py
from unittest.mock import patch, AsyncMock

import pytest

from src.service.order_validation_service import validate_order, _validate_order


@pytest.mark.asyncio
async def test_validate_order_success(mock_order):
    # Given
    with patch("src.connector.payment_connector.validate", return_value=True) as mock_payment_validate, \
         patch("src.connector.product_connector.validate", return_value=True) as mock_product_validate:

        # When
        validation_results = await _validate_order(mock_order)

        # Then
        mock_payment_validate.assert_called_once_with(mock_order)
        mock_product_validate.assert_called_once_with(mock_order)
        assert validation_results == []


@pytest.mark.asyncio
async def test_validate_order_payment_error(mock_order):
    # Given
    with patch("src.connector.payment_connector.validate", return_value=False) as mock_payment_validate, \
         patch("src.connector.product_connector.validate", return_value=True) as mock_product_validate:

        # When
        validation_results = await _validate_order(mock_order)

        # Then
        mock_payment_validate.assert_called_once_with(mock_order)
        mock_product_validate.assert_called_once_with(mock_order)
        assert validation_results == ["Validate Payment Error"]


@pytest.mark.asyncio
async def test_validate_order_product_error(mock_order):
    # Given
    with patch("src.connector.payment_connector.validate", return_value=True) as mock_payment_validate, \
         patch("src.connector.product_connector.validate", return_value=False) as mock_product_validate:

        # When
        validation_results = await _validate_order(mock_order)

        # Then
        mock_payment_validate.assert_called_once_with(mock_order)
        mock_product_validate.assert_called_once_with(mock_order)
        assert validation_results == ["Validate Product Error"]


@pytest.mark.asyncio
async def test_validate_order_both_errors(mock_order):
    # Given
    with patch("src.connector.payment_connector.validate", return_value=False) as mock_payment_validate, \
         patch("src.connector.product_connector.validate", return_value=False) as mock_product_validate:

        # When
        validation_results = await _validate_order(mock_order)

        # Then
        mock_payment_validate.assert_called_once_with(mock_order)
        mock_product_validate.assert_called_once_with(mock_order)
        assert validation_results == ["Validate Payment Error", "Validate Product Error"]


def test_validate_order_sync_wrapper(mock_order):
    # Given
    with patch("src.service.order_validation_service._validate_order", new_callable=AsyncMock) as mock_async_validate:
        mock_async_validate.return_value = []

        # When
        result = validate_order(mock_order)

        # Then
        mock_async_validate.assert_called_once_with(mock_order)
        assert result == []
