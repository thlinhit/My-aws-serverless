from typing import List, Optional

from pydantic import Field, BaseModel

from src.domain.custom_type import NumDecimal
from src.domain.order_status import OrderStatus


class Product(BaseModel):
    id: str
    name: str
    price: NumDecimal
    quantity: Optional[int] = Field(default=1)

    def get_total_amount(self) -> NumDecimal:
        return self.price * self.quantity


class Address(BaseModel):
    name: str
    street_address: str = Field(alias="streetAddress")
    city: str
    country: str
    phone_number: str = Field(alias="phoneNumber")


class Order(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    status: Optional[OrderStatus] = Field(default=OrderStatus.PENDING)
    products: List[Product]
    delivery_price: NumDecimal = Field(alias="deliveryPrice")
    address: Address

    def get_total_amount(self) -> NumDecimal:
        total_amount = sum(product.get_total_amount() for product in self.products)
        return total_amount + self.delivery_price

