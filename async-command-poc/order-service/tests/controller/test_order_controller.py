# tests/test_place_order.py
import pytest
from unittest.mock import patch, MagicMock
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.event_handler.router import APIGatewayHttpRouter
from aws_lambda_powertools.utilities.validation import SchemaValidationError
from src.controller.dto.place_order_dto import PlaceOrderDto
from src.controller.order_controller import place_order
from src.exception.domain_error import DomainError
from src.exception.domain_code import DomainCode
from http import HTTPStatus

from src.util import file_util


@pytest.fixture
def mock_router():
    router = MagicMock(spec=APIGatewayHttpRouter)
    router.current_event = MagicMock()
    return router


# Fixture for mock payload data
@pytest.fixture
def mock_payload():
    return {
        "id": "order123",
        "userId": "user456",
        "products": [{"id": "product1", "quantity": 1}],
        "deliveryPrice": "5.00",
        "address": {
            "name": "John Doe",
            "streetAddress": "123 Main St",
            "city": "Anytown",
            "country": "USA",
            "phoneNumber": "123-456-7890"
        }
    }

@pytest.fixture
def mock_create_order():
    return {
        "userId": "user456",
        "products": [
            {
                "id": "product1",
                "name": "Product 1",
                "price": 19.99,
                "quantity": 2
            },
            {
                "id": "product2",
                "name": "Product 2",
                "price": 5.99
            }
        ],
        "deliveryPrice": 5,
        "address": {
            "name": "John Doe",
            "streetAddress": "123 Main St",
            "city": "Anytown",
            "country": "USA",
            "phoneNumber": "123-456-7890"
        }
    }


def test_place_order_success(mock_payload, mock_order, mock_router, mock_create_order):
    mock_router.current_event.json_body = mock_create_order
    # Mocks for dependencies
    with patch("src.controller.order_controller.router", new=mock_router), \
            patch("src.controller.order_controller.validate") as mock_validate, \
            patch("src.service.order_service.create_order", return_value=mock_order):
        # When
        response = place_order()

        # Then
        mock_validate.assert_called_once_with(event=mock_create_order, schema=file_util.load_json_schema('create_order_request_schema.json'))
        assert isinstance(response, Response)
        assert response.status_code == HTTPStatus.ACCEPTED
        assert response.content_type == "application/json"


def test_place_order_schema_validation_error(mock_payload, mock_router, mock_create_order):
    mock_router.current_event.json_body = mock_create_order
    # Mocks for schema validation error
    with patch("src.controller.order_controller.router", new=mock_router), \
            patch("src.controller.order_controller.validate", side_effect=SchemaValidationError("Invalid")):
        # When / Then
        with pytest.raises(DomainError) as exc_info:
            place_order()

        # Assertions
        assert exc_info.value.domain_code == DomainCode.VALIDATION_ERROR
        assert str(exc_info.value) == "[<EXTERNAL_CODE>001] - Validation Error. errorMessage:Invalid"


def test_place_order_domain_error(mock_payload, mock_router, mock_create_order):
    mock_router.current_event.json_body = mock_create_order
    # Mock for a domain error when calling the order service
    with patch("src.controller.order_controller.router", new=mock_router), \
            patch("src.controller.order_controller.validate"), \
            patch("src.service.order_service.create_order", side_effect=DomainError(DomainCode.INVALID_ORDER_STATUS, "orderId", "userId", "expected", "actual")):
        # When / Then
        with pytest.raises(DomainError) as exc_info:
            place_order()

        # Assertions
        assert exc_info.value.domain_code == DomainCode.INVALID_ORDER_STATUS
