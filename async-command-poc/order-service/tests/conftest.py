# tests/conftest.py
import pytest
from src.domain.order import Order, Product, Address
from src.domain.order_status import OrderStatus
from src.domain.custom_type import NumDecimal

@pytest.fixture
def mock_product():
    return Product(
        id="prod123",
        name="Test Product",
        price=10.50,
        quantity=2
    )


@pytest.fixture
def mock_address():
    return Address(
        name="John Doe",
        streetAddress="123 Main St",
        city="Anytown",
        country="USA",
        phoneNumber="123-456-7890"
    )


@pytest.fixture
def mock_order(mock_product, mock_address):
    return Order(
        id="order123",
        userId="user456",
        status=OrderStatus.PENDING,
        products=[mock_product],
        deliveryPrice=5.00,
        address=mock_address
    )