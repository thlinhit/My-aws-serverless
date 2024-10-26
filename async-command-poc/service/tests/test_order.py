from src.controller.dto.place_order_dto import PlaceOrderDto
from src.domain.order import Order
from src.domain.order_status import OrderStatus
from src.service import order_service


def test_okey():
    payload = {
        "userId": "user456",
        "status": "Pending",
        "products": [
            {
                "id": "product1",
                "name": "Product 1",
                "price": "19.99",
                "quantity": 2
            },
            {
                "id": "product2",
                "name": "Product 2",
                "price": "5.99"
            }
        ],
        "deliveryPrice": 5,
        "address": {
            "name": "John Doe",
            "streetAddress": "123 Main St",
            "city": "Anytown",
            "country": "USA",
            "phoneNumber": "123-456-7890"
        }
    }

    place_order_dto = PlaceOrderDto.model_validate(payload)
    order = place_order_dto.to_domain()
    order.status = OrderStatus.FAILED
    order_service.create_order(order)
    print(place_order_dto.to_domain().model_dump_json())