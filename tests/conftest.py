from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.orders import get_order_service
from app.main import app
from app.domain.state_machine import TransitionTableStateMachine
from app.repositories.in_memory_order_repository import InMemoryOrderRepository
from app.services.order_service import OrderService
from app.services.ticket_service import InMemoryTicketService


@pytest.fixture()
def order_repository() -> InMemoryOrderRepository:
    return InMemoryOrderRepository()


@pytest.fixture()
def ticket_service() -> InMemoryTicketService:
    return InMemoryTicketService()


@pytest.fixture()
def state_machine() -> TransitionTableStateMachine:
    return TransitionTableStateMachine()


@pytest.fixture()
def order_service(
    order_repository: InMemoryOrderRepository,
    state_machine: TransitionTableStateMachine,
    ticket_service: InMemoryTicketService,
) -> OrderService:
    return OrderService(order_repository, state_machine, ticket_service)


@pytest.fixture()
def client(order_service: OrderService) -> Iterator[TestClient]:
    app.dependency_overrides[get_order_service] = lambda: order_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
