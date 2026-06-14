from __future__ import annotations

from enum import Enum


class OrderEvent(str, Enum):
    PENDING_BIOMETRICAL_VERIFICATION = "pendingBiometricalVerification"
    NO_VERIFICATION_NEEDED = "noVerificationNeeded"
    PAYMENT_FAILED = "paymentFailed"
    ORDER_CANCELLED = "orderCancelled"
    BIOMETRICAL_VERIFICATION_SUCCESSFUL = "biometricalVerificationSuccessful"
    VERIFICATION_FAILED = "verificationFailed"
    ORDER_CANCELLED_BY_USER = "orderCancelledByUser"
    PAYMENT_SUCCESSFUL = "paymentSuccessful"
    PREPARING_SHIPMENT = "preparingShipment"
    ITEM_DISPATCHED = "itemDispatched"
    ITEM_RECEIVED_BY_CUSTOMER = "itemReceivedByCustomer"
    DELIVERY_ISSUE = "deliveryIssue"
