from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from app.api.orders import get_order_service
from app.main import app
from app.domain.state_machine import TransitionTableStateMachine
from app.repositories.in_memory_order_repository import InMemoryOrderRepository
from app.rules.runtime.action_dispatcher import ActionDispatcher
from app.rules.repositories.in_memory_rule_repository import InMemoryRuleRepository
from app.rules.services.rule_service import RuleService
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
    rule_service = RuleService(InMemoryRuleRepository())
    action_dispatcher = ActionDispatcher(ticket_service=ticket_service)
    return OrderService(order_repository, state_machine, rule_service, action_dispatcher)


@pytest.fixture()
def client(order_service: OrderService) -> Iterator[TestClient]:
    app.dependency_overrides[get_order_service] = lambda: order_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
