from pydantic import Field

from src.domain.order import Address, Order
from src.mapper import generic_mapper
from src.repository.model.item import Item
from src.repository.model.order_item import OrderItem


class OrderAddressItem(Item):
    name: str
    street_address: str = Field(alias="streetAddress")
    city: str
    country: str
    phone_number: str = Field(alias="phoneNumber")

    def to_domain(self) -> Address:
        return generic_mapper.map(self, Address)

    @staticmethod
    def from_dto(order: Order, address: Address):
        return generic_mapper.map(
            address,
            OrderAddressItem,
            extra_fields={
                "pk": OrderItem.build_pk(order.id),
                "sk": OrderAddressItem.build_sk(),
            },
        )

    @staticmethod
    def build_sk():
        return "ADDR"
