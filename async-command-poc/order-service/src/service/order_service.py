from src.domain.order import Order
from src.domain.order_status import OrderStatus
from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.log.logger import logger
from src.repository import order_repository


def create_order(order: Order) -> Order:
    logger.info(f"Create the order, userId={order.userId}, " f"orderId={order.id}")
    if order.status is not OrderStatus.PENDING:
        raise DomainError(
            DomainCode.INVALID_ORDER_STATUS,
            order.id,
            order.userId,
            OrderStatus.PENDING,
            order.status,
        )
    return order_repository.insert_if_not_exists(order)


def get_order(order_id: str) -> Order:
    if not order_id:
        raise DomainError(DomainCode.VALIDATION_ERROR, "order_id can not be empty")
    logger.info(f"Get order, order_id={order_id}")
    try:
        order = order_repository.get_order(order_id)
        logger.info(f"Order found, order_id={order_id}")
        return order
    except DomainError as domain_error:
        if domain_error.domain_code == DomainCode.ITEM_NOT_FOUND:
            raise DomainError(DomainCode.ORDER_NOT_FOUND, order_id)
