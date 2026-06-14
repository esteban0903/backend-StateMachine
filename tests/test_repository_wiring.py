from __future__ import annotations

import pytest

import app.api.orders as orders_module
from app.repositories.in_memory_order_repository import InMemoryOrderRepository


def test_create_order_repository_uses_in_memory_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.delenv("USE_DYNAMODB", raising=False)

    # Act
    repository = orders_module._create_order_repository()

    # Assert
    assert isinstance(repository, InMemoryOrderRepository)


def test_create_order_repository_uses_dynamodb_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("USE_DYNAMODB", "true")
    monkeypatch.setenv("ORDERS_TABLE_NAME", "orders-table")

    created: dict[str, str] = {}

    class FakeRepository:
        def __init__(self, table_name: str) -> None:
            created["table_name"] = table_name

    monkeypatch.setattr(orders_module, "DynamoDbOrderRepository", FakeRepository)

    # Act
    repository = orders_module._create_order_repository()

    # Assert
    assert isinstance(repository, FakeRepository)
    assert created["table_name"] == "orders-table"


def test_create_order_repository_fails_fast_when_dynamodb_table_name_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.setenv("USE_DYNAMODB", "true")
    monkeypatch.delenv("ORDERS_TABLE_NAME", raising=False)

    # Act / Assert
    with pytest.raises(RuntimeError, match="Invalid DynamoDB configuration"):
        orders_module._create_order_repository()