import os
from typing import List, Optional

from src.domain.order import Order
from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.log.logger import logger
from src.repository import dynamodb_repository
from src.repository.dynamodb_repository import DynamoDBTransactionHelper
from src.repository.model.order_address_item import OrderAddressItem
from src.repository.model.order_item import OrderItem
from src.repository.model.order_product_item import OrderProductItem

table_name = os.getenv("ORDER_TABLE", "arb-poc-order-table")


def insert_if_not_exists(order: Order) -> Order:
    try:
        transaction_helper = DynamoDBTransactionHelper(table_name)
        transaction_helper.add_put_item(
            item=OrderItem.from_dto(order),
            condition_expression="attribute_not_exists(pk)",
        )
        transaction_helper.add_put_item(OrderAddressItem.from_dto(order, order.address))
        for product in order.products:
            transaction_helper.add_put_item(OrderProductItem.from_dto(order, product))
        transaction_helper.execute_transaction()
        return order
    except DomainError as e:
        logger.error(
            f"Error was thrown while inserting the order, orderId={order.id}, err={repr(e)}"
        )
        if e.domain_code == DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR:
            raise DomainError(
                DomainCode.ITEM_ALREADY_EXISTS,
                OrderItem.build_pk(order.id),
                OrderItem.build_pk(order.id),
            )
        raise e


def get_order(order_id: str) -> Order:
    items = dynamodb_repository.get_items_by_pk(table_name=table_name, pk=OrderItem.build_pk(order_id))

    def validate_and_get_items(items: List[dict], sk_prefix: str, expected_count: Optional[int] = None) -> List[dict]:
        matched_items = [item for item in items if item["sk"].startswith(sk_prefix)]
        item_count = len(matched_items)

        if item_count == 0 or (expected_count and item_count != expected_count):
            raise DomainError(
                DomainCode.INVALID_ORDER_DATA,
                order_id,
                f"Invalid {sk_prefix} info, number of items: {item_count}"
            )
        return matched_items

    address_dicts = validate_and_get_items(items, 'ADDR', expected_count=1)
    product_dicts = validate_and_get_items(items, 'PRD#')
    order_dicts = validate_and_get_items(items, 'ORDER#', expected_count=1)

    order_item = OrderItem(**order_dicts[0])
    address_item = OrderAddressItem(**address_dicts[0])
    product_items = [OrderProductItem(**product_item) for product_item in product_dicts]

    order = order_item.to_domain(
        address=address_item.to_domain(),
        products=[product_item.to_domain() for product_item in product_items]
    )

    return order
