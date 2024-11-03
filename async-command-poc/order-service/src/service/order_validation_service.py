import asyncio
from typing import List, Tuple

from src.connector import payment_connector, product_connector
from src.domain.order import Order


def validate_order(order: Order) -> list[str]:
    return asyncio.run(_validate_order(order))


async def _validate_order(order: Order) -> List[str]:
    validation_results = await asyncio.gather(
        _validate_payment(order),
        _validate_product(order)
    )
    return [msg for valid, msg in validation_results if not valid]


async def _validate_payment(order: Order) -> Tuple[bool, str]:
    is_valid = payment_connector.validate(order)
    return is_valid, "Validate Payment Error" if is_valid is False else None


async def _validate_product(order: Order) -> Tuple[bool, str]:
    is_valid = product_connector.validate(order)
    return is_valid, "Validate Product Error" if is_valid is False else None
