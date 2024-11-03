import os

from aws_lambda_powertools.utilities.parser import parse

from src.domain.order import Order
from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.log.logger import logger
from src.repository import dynamodb_repository
from src.repository.dynamodb_repository import DynamoDBTransactionHelper
from src.repository.model.key import Key
from src.repository.model.order_address_item import OrderAddressItem
from src.repository.model.order_item import OrderItem
from src.repository.model.order_product_item import OrderProductItem

table_name = os.environ["ORDER_TABLE"]


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
    item = dynamodb_repository.get_item(
        table_name=table_name,
        key=Key(
            pk=OrderItem.build_pk(order_id),
            sk=OrderItem.build_sk(order_id)
        )
    )
    return parse(model=OrderItem, event=item).to_domain()
