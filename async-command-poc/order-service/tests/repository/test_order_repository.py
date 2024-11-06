# tests/test_order_repository.py
from unittest.mock import patch, MagicMock

import pytest

from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.repository.model.order_item import OrderItem
from src.repository.order_repository import insert_if_not_exists, get_order


@pytest.fixture
def mock_dynamo_transaction():
    with patch("src.repository.order_repository.DynamoDBTransactionHelper") as MockTransactionHelper:
        yield MockTransactionHelper.return_value


@pytest.fixture
def mock_dynamodb_repository():
    with patch("src.repository.dynamodb_repository.get_items_by_pk") as mock_repo:
        yield mock_repo


def test_insert_if_not_exists_success(mock_order, mock_dynamo_transaction):
    # Given
    mock_dynamo_transaction.execute_transaction = MagicMock()

    # When
    result = insert_if_not_exists(mock_order)

    # Then
    mock_dynamo_transaction.add_put_item.assert_any_call(
        item=OrderItem.from_dto(mock_order),
        condition_expression="attribute_not_exists(pk)"
    )
    assert result == mock_order
    mock_dynamo_transaction.execute_transaction.assert_called_once()


def test_insert_if_not_exists_item_exists_error(mock_order, mock_dynamo_transaction):
    # Given
    mock_dynamo_transaction.execute_transaction.side_effect = DomainError(
        DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR,
        "table_name"
    )

    # When / Then
    with pytest.raises(DomainError) as exc_info:
        insert_if_not_exists(mock_order)

    assert exc_info.value.domain_code == DomainCode.ITEM_ALREADY_EXISTS
    mock_dynamo_transaction.execute_transaction.assert_called_once()


def test_insert_if_not_exists_other_error(mock_order, mock_dynamo_transaction):
    # Given
    mock_dynamo_transaction.execute_transaction.side_effect = DomainError(
        DomainCode.UNKNOWN, "Unexpected error"
    )

    # When / Then
    with pytest.raises(DomainError) as exc_info:
        insert_if_not_exists(mock_order)

    assert exc_info.value.domain_code == DomainCode.UNKNOWN
    mock_dynamo_transaction.execute_transaction.assert_called_once()


def test_get_order_success(mock_order, mock_dynamodb_repository):
    # Given
    mock_dynamodb_repository.return_value = [
        {"pk": "ORDER#order123", "sk": "ORDER#order123", "userId": "user456", "status": "Pending", "deliveryPrice": 5.00, "orderId": "order123"},
        {"pk": "ORDER#order123", "sk": "ADDR", "name": "John Doe", "city": "Anytown", "country": "USA", "phoneNumber": "123-456-7890", "streetAddress": "123 Main St"},
        {"pk": "ORDER#order123", "sk": "PRD#prod123", "name": "Test Product", "price": 10.50, "quantity": 2},
    ]

    # When
    result = get_order(mock_order.id)

    # Then
    assert result == mock_order
    mock_dynamodb_repository.assert_called_once_with(
        table_name="arb-poc-order-table", pk="ORDER#order123"
    )


def test_get_order_missing_order_item(mock_dynamodb_repository):
    # Given
    mock_dynamodb_repository.return_value = [
        {"pk": "ORDER#order123", "sk": "ADDR#"},
        {"pk": "ORDER#order123", "sk": "PRD#prod1"}
    ]  # Missing order item

    # When / Then
    with pytest.raises(DomainError) as exc_info:
        get_order("order123")

    assert exc_info.value.domain_code == DomainCode.INVALID_ORDER_DATA


def test_get_order_missing_address_item(mock_dynamodb_repository):
    # Given
    mock_dynamodb_repository.return_value = [
        {"pk": "ORDER#order123", "sk": "ORDER#order123"},
        {"pk": "ORDER#order123", "sk": "PRD#prod1"}
    ]  # Missing address item

    # When / Then
    with pytest.raises(DomainError) as exc_info:
        get_order("order123")

    assert exc_info.value.domain_code == DomainCode.INVALID_ORDER_DATA


def test_get_order_invalid_product_items(mock_dynamodb_repository):
    # Given
    mock_dynamodb_repository.return_value = [
        {"pk": "ORDER#order123", "sk": "ORDER#order123"},
        {"pk": "ORDER#order123", "sk": "ADDR#"},
    ]  # No product items

    # When / Then
    with pytest.raises(DomainError) as exc_info:
        get_order("order123")

    assert exc_info.value.domain_code == DomainCode.INVALID_ORDER_DATA
