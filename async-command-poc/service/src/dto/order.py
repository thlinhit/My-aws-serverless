from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


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
    products: List[Product]
    deliveryPrice: int
    address: Address
