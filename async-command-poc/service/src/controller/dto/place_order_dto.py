from typing import List

from pydantic import BaseModel

from src.domain.order import Product, Address, Order
from src.mapper import generic_mapper
from src.util import uuid_util


class PlaceOrderDto(BaseModel):
    userId: str
    products: List[Product]
    deliveryPrice: int
    address: Address

    def to_domain(self) -> Order:
        return generic_mapper.map(self, Order, extra_fields={"id": str(uuid_util.generate_uuid_from_json(self.model_dump()))})
