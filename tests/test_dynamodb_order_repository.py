from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest
from pytest import approx

from app.domain.enums.order_state import OrderState
from app.domain.models.order import Order
from app.repositories.dynamodb_order_repository import DynamoDbOrderRepository


class FakeTable:
    def __init__(self) -> None:
        self.items: dict[str, dict[str, object]] = {}

    def get_item(self, **kwargs: dict[str, str]) -> dict[str, object]:
        item = self.items.get(kwargs["Key"]["order_id"])
        return {"Item": item} if item is not None else {}

    def put_item(self, **kwargs: dict[str, object]) -> dict[str, object]:
        item = kwargs["Item"]
        self.items[str(item["order_id"])] = item
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}


class FakeDynamoResource:
    def __init__(self, table: FakeTable) -> None:
        self._table = table

    def table(self, _: str) -> FakeTable:
        return self._table


def test_save_serializes_order_into_dynamodb_item() -> None:
    # Arrange
    table = FakeTable()
    repository = DynamoDbOrderRepository(table_name="orders", dynamodb_resource=SimpleNamespace(Table=FakeDynamoResource(table).table))
    order = Order(
        id="order-1",
        product_ids=["p1", "p2"],
        amount=12.5,
        state=OrderState.CONFIRMED,
        history=[
            {
                "event_type": "noVerificationNeeded",
                "previous_state": "Pending",
                "new_state": "PendingPayment",
                "timestamp": "2026-06-12T18:00:00Z",
            }
        ],
    )

    # Act
    saved_order = repository.save(order)

    # Assert
    assert saved_order == order
    assert table.items["order-1"] == {
        "order_id": "order-1",
        "product_ids": ["p1", "p2"],
        "amount": Decimal("12.5"),
        "state": "Confirmed",
        "history": [
            {
                "event_type": "noVerificationNeeded",
                "previous_state": "Pending",
                "new_state": "PendingPayment",
                "timestamp": "2026-06-12T18:00:00Z",
            }
        ],
    }


def test_get_by_id_deserializes_dynamodb_item_into_order() -> None:
    # Arrange
    table = FakeTable()
    table.items["order-2"] = {
        "order_id": "order-2",
        "product_ids": ["p3"],
        "amount": Decimal("99.9"),
        "state": "PendingPayment",
    }
    repository = DynamoDbOrderRepository(table_name="orders", dynamodb_resource=SimpleNamespace(Table=FakeDynamoResource(table).table))

    # Act
    order = repository.get_by_id("order-2")

    # Assert
    assert order is not None
    assert order.id == "order-2"
    assert order.product_ids == ["p3"]
    assert order.amount == approx(99.9)
    assert order.state is OrderState.PENDING_PAYMENT


def test_get_by_id_returns_none_when_item_is_missing() -> None:
    # Arrange
    table = FakeTable()
    repository = DynamoDbOrderRepository(table_name="orders", dynamodb_resource=SimpleNamespace(Table=FakeDynamoResource(table).table))

    # Act
    order = repository.get_by_id("missing")

    # Assert
    assert order is None


def test_get_by_id_defaults_history_when_item_has_no_history_field() -> None:
    # Arrange
    table = FakeTable()
    table.items["order-3"] = {
        "order_id": "order-3",
        "product_ids": ["p4"],
        "amount": Decimal("10"),
        "state": "Pending",
    }
    repository = DynamoDbOrderRepository(table_name="orders", dynamodb_resource=SimpleNamespace(Table=FakeDynamoResource(table).table))

    # Act
    order = repository.get_by_id("order-3")

    # Assert
    assert order is not None
    assert order.history == []


def test_constructor_requires_table_name_when_dynamodb_is_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.delenv("ORDERS_TABLE_NAME", raising=False)

    # Act / Assert
    with pytest.raises(ValueError, match="Invalid DynamoDB configuration"):
        DynamoDbOrderRepository(dynamodb_resource=SimpleNamespace(Table=FakeDynamoResource(FakeTable()).table))