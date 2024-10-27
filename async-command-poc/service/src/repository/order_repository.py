import os
from typing import List

from src.domain.order import Order
from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.log.logger import logger
from src.repository import dynamodb_repository
from src.repository.model.order_address_item import OrderAddressItem
from src.repository.model.order_item import OrderItem
from src.repository.model.order_product_item import OrderProductItem

table_name = os.environ["ORDER_TABLE"]


def insert_if_not_exists(order: Order) -> Order:
    try:
        order_item = OrderItem.from_dto(order)
        product_items: List[OrderProductItem] = [
            OrderProductItem.from_dto(order, product) for product in order.products
        ]
        address_item = OrderAddressItem.from_dto(order, order.address)
        dynamodb_repository.transaction_put_items(table_name, [order_item, *product_items, address_item])
        return order
    except DomainError as e:
        logger.error(f"Error was thrown while inserting the order, orderId={order.id}, err={repr(e)}")
        if (
                e.domain_code
                == DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR
        ):
            raise DomainError(DomainCode.ITEM_ALREADY_EXISTS, "pk", "sk")
        raise e
