from typing import List

from pydantic import BaseModel, Field

from src.domain.custom_type import NumDecimal
from src.domain.order import Address, Order, Product
from src.mapper import generic_mapper
from src.util import uuid_util


class PlaceOrderDto(BaseModel):
    userId: str
    products: List[Product]
    delivery_price: NumDecimal = Field(alias="deliveryPrice")
    address: Address

    def to_domain(self) -> Order:
        return generic_mapper.map(
            self, Order, extra_fields={"id": self.compute_hashed_id()}
        )

    def compute_hashed_id(self) -> str:
        return str(uuid_util.generate_uuid_from_json(self.model_dump()))
