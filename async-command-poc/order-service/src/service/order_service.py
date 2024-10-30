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
