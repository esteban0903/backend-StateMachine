from __future__ import annotations

from enum import Enum


class OrderState(str, Enum):
    PENDING = "Pending"
    ON_HOLD = "OnHold"
    PENDING_PAYMENT = "PendingPayment"
    CONFIRMED = "Confirmed"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"
