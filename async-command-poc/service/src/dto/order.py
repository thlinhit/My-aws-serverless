from decimal import Decimal

from pydantic import BaseModel, Field

class OrderProduct(BaseModel):
    id: str = Field(alias="productId")
    price: Decimal = Field(alias="productPrice")
    quantity: int = Field(alias="productQuantity")


class Order(BaseModel):
    id: str = Field(alias="orderId")
    name: str = Field(alias="orderName")
    order_products: list[OrderProduct] = Field(alias="orderProducts")



