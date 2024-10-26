from pydantic import Field

from src.dto.order import Order
from src.mapper import generic_mapper
from src.repository.model.item import Item


class OrderItem(Item):
    name: str = Field(alias="name")
    total_quantity: int = Field(default=0, alias="totalQuantity")

    def to_dto(self) -> Order:
        return generic_mapper.map(self, Order)

    @staticmethod
    def from_dto(order: Order):
        result = generic_mapper.map(
            order,
            OrderItem,
            extra_fields={
                "pk": OrderItem.build_pk(order.id),
                "sk": OrderItem.build_sk(order.id),
            },
        )

        result.total_quantity = sum(
            product.quantity for product in order.order_products or []
        )

        return result

    @staticmethod
    def build_pk(order_id: str):
        return f"ORDER#{order_id}"

    @staticmethod
    def build_sk(order_id: str):
        return OrderItem.build_pk(order_id)
