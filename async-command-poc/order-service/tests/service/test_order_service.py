# tests/test_order_service.py
from unittest.mock import patch

import pytest

from src.domain.order import Order
from src.domain.order_status import OrderStatus
from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.service.order_service import create_order, get_order


def test_create_order_success(mock_order):
    # Given
    with patch("src.repository.order_repository.insert_if_not_exists") as mock_insert:
        mock_insert.return_value = mock_order

        # When
        result = create_order(mock_order)

        # Then
        mock_insert.assert_called_once_with(mock_order)
        assert result == mock_order


def test_create_order_invalid_status(mock_order):
    # Given
    invalid_order: Order = Order(**mock_order.model_dump())
    invalid_order.status = OrderStatus.FAILED

    # When / Then
    with pytest.raises(DomainError) as exc_info:
        create_order(invalid_order)

    # Verify the exception details
    assert exc_info.value.domain_code == DomainCode.INVALID_ORDER_STATUS
    assert exc_info.value.internal_message == ("Order status is invalid, orderId:order123, userId:user456, "
                                               "expected:OrderStatus.PENDING, actual:OrderStatus.FAILED")


def test_get_order_success(mock_order):
    # Given
    with patch("src.repository.order_repository.get_order") as mock_get_order, \
         patch("src.log.logger") as mock_logger:
        mock_get_order.return_value = mock_order

        # When
        result = get_order(mock_order.id)

        # Then
        mock_get_order.assert_called_once_with(mock_order.id)
        assert result == mock_order


def test_get_order_validation_error():
    # When / Then
    with patch("src.log.logger") as mock_logger:
        with pytest.raises(DomainError) as exc_info:
            get_order("")  # Empty order_id

        # Verify the exception details
        assert exc_info.value.domain_code == DomainCode.VALIDATION_ERROR
        assert exc_info.value.internal_message == "Validation Error. errorMessage:order_id can not be empty"
        mock_logger.info.assert_not_called()


def test_get_order_not_found():
    # Given
    order_id = "nonexistent_order"
    with patch("src.repository.order_repository.get_order", side_effect=DomainError(DomainCode.ITEM_NOT_FOUND, "test", "pk", "sk")):
        # When / Then
        with pytest.raises(DomainError) as exc_info:
            get_order(order_id)

        # Verify the exception details
        assert exc_info.value.domain_code == DomainCode.ORDER_NOT_FOUND
        assert exc_info.value.internal_message == "Order not found, orderId:nonexistent_order"
