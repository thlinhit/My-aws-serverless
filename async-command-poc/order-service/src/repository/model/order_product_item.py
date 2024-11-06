from src.domain.custom_type import NumDecimal
from src.domain.order import Order, Product
from src.mapper import generic_mapper
from src.repository.model.item import Item
from src.repository.model.order_item import OrderItem


class OrderProductItem(Item):
    name: str
    price: NumDecimal
    quantity: int

    def to_domain(self) -> Product:
        return generic_mapper.map(
            self,
            Product,
            extra_fields={
                "id": self.sk.replace("PRD#", "")
            }
        )

    @staticmethod
    def from_dto(order: Order, product: Product):
        return generic_mapper.map(
            product,
            OrderProductItem,
            extra_fields={
                "pk": OrderItem.build_pk(order.id),
                "sk": OrderProductItem.build_sk(product.id),
            },
        )

    @staticmethod
    def build_sk(product_id: str):
        return f"PRD#{product_id}"
