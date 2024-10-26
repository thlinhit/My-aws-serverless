from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from src.domain.order_status import OrderStatus


class Product(BaseModel):
    id: str
    name: str
    price: Decimal
    quantity: Optional[int] = Field(default=1)


class Address(BaseModel):
    name: str
    streetAddress: str
    city: str
    country: str
    phoneNumber: str


class Order(BaseModel):
    id: str
    userId: str
    status: Optional[OrderStatus] = Field(default=OrderStatus.PENDING)
    products: List[Product]
    deliveryPrice: int
    address: Address
