from enum import Enum


class OrderStatus(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELED = "Canceled"
    RETURNED = "Returned"
    FAILED = "Failed"
