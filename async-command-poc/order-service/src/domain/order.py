from decimal import Decimal
from typing import List, Optional

from pydantic import Field

from src.domain.base import Base
from src.domain.order_status import OrderStatus


class Product(Base):
    id: str
    name: str
    price: Decimal
    quantity: Optional[int] = Field(default=1)

    def get_total_amount(self) -> Decimal:
        return self.price * self.quantity


class Address(Base):
    name: str
    street_address: str = Field(alias="streetAddress")
    city: str
    country: str
    phone_number: str = Field(alias="phoneNumber")


class Order(Base):
    id: str
    user_id: str = Field(alias="userId")
    status: Optional[OrderStatus] = Field(default=OrderStatus.PENDING)
    products: List[Product]
    delivery_price: Decimal = Field(alias="deliveryPrice")
    address: Address

    def get_total_amount(self) -> Decimal:
        total_amount = sum(product.get_total_amount() for product in self.products)
        return total_amount + self.delivery_price

