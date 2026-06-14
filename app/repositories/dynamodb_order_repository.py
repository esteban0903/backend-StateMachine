from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

import boto3

from app.domain.enums.order_state import OrderState
from app.domain.models.order import Order
from app.domain.models.order_history_entry import OrderHistoryEntry
from app.repositories.order_repository import OrderRepository


class DynamoDbOrderRepository(OrderRepository):
    """Persist orders as single DynamoDB items.

    Schema decisions:
    - `order_id` is the partition key because each order is retrieved by its unique id.
    - `product_ids` is stored as a DynamoDB list to keep the domain shape intact.
    - `amount` is stored as a DynamoDB number using `Decimal`, which is the boto3-safe
      representation for monetary values.
    - `state` is stored as a string so it maps directly to the domain enum value.
    - No sort key is needed because the repository only supports point lookups by order id.
    """

    def __init__(
        self,
        table_name: str | None = None,
        dynamodb_resource: Any | None = None,
    ) -> None:
        resolved_table_name = table_name or os.getenv("ORDERS_TABLE_NAME")
        if resolved_table_name is None or not resolved_table_name.strip():
            raise ValueError(
                "Invalid DynamoDB configuration: set ORDERS_TABLE_NAME when USE_DYNAMODB=true."
            )

        self._table_name = resolved_table_name.strip()
        self._dynamodb = dynamodb_resource or self._create_resource()
        self._table = self._dynamodb.Table(self._table_name)

    @staticmethod
    def _create_resource() -> Any:
        region_name = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
        endpoint_url = os.getenv("DYNAMODB_ENDPOINT_URL")
        return boto3.resource("dynamodb", region_name=region_name, endpoint_url=endpoint_url)

    @staticmethod
    def _to_item(order: Order) -> dict[str, Any]:
        return {
            "order_id": order.id,
            "product_ids": list(order.product_ids),
            "amount": Decimal(str(order.amount)),
            "state": order.state.value,
            "history": [entry.model_dump() for entry in order.history],
        }

    @staticmethod
    def _from_item(item: dict[str, Any]) -> Order:
        return Order(
            id=item["order_id"],
            product_ids=list(item.get("product_ids", [])),
            amount=float(item["amount"]),
            state=OrderState(item["state"]),
            history=[OrderHistoryEntry(**entry) for entry in item.get("history", [])],
        )

    def get_by_id(self, order_id: str) -> Order | None:
        response = self._table.get_item(Key={"order_id": order_id})
        item = response.get("Item")

        if item is None:
            return None

        return self._from_item(item)

    def save(self, order: Order) -> Order:
        self._table.put_item(Item=self._to_item(order))
        return order