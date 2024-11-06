import json
import os
import random

from src.domain.order import Order
from src.domain.order_status import OrderStatus
from src.log.logger import logger
from src.service import order_service

os.environ["REGION"] = "us-east-1"
os.environ["ORDER_TABLE"] = "order_table"
from src.controller.dto.place_order_dto import PlaceOrderDto
from src.repository import order_repository


def test_okay():
    payload = {
        "userId": "user" + str(random.randint(1000, 9999)),
        "status": "Pending",
        "products": [
            {"id": "product1", "name": "Product 1", "price": 19.99, "quantity": 2},
            {"id": "product2", "name": "Product 2", "price": 5.99},
        ],
        "deliveryPrice": 5,
        "address": {
            "name": "John Doe",
            "streetAddress": "123 Main St",
            "city": "Anytown",
            "country": "USA",
            "phoneNumber": "123-456-7890",
        },
    }

    place_order_dto = PlaceOrderDto.model_validate(payload)
    order = place_order_dto.to_domain()
    # new_order: Order = order_repository.insert_if_not_exists(order)
    # logger.info(new_order.model_dump_json(by_alias=True))


# def test_get_order():
#     order: Order = order_service.get_order("65e64530-693d-bded-4b63-f817265aa38a")
#     assert order.status == OrderStatus.PENDING
