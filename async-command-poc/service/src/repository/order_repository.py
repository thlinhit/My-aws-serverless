from src.domain.order import Order
from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.log.logger import logger


def insert_if_not_exists(order: Order) -> Order:
    try:
        return order
    except DomainError as e:
        logger.error(f"Error was thrown while inserting the order, orderId={order.id}, err={repr(e)}")
        if (
                e.domain_code
                == DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR
        ):
            raise DomainError(DomainCode.ITEM_ALREADY_EXISTS, "pk", "sk")
        raise e
