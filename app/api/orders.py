from __future__ import annotations

import os
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas import (
    CreateOrderRequest,
    CreateOrderResponse,
    OrderResponse,
    OrderHistoryResponse,
    ProcessEventRequest,
    ProcessEventResponse,
)
from app.domain.enums.order_event import OrderEvent
from app.domain.exceptions.domain_exceptions import InvalidEventError
from app.domain.models.order import Order
from app.repositories.dynamodb_order_repository import DynamoDbOrderRepository
from app.repositories.in_memory_order_repository import InMemoryOrderRepository
from app.repositories.order_repository import OrderRepository
from app.rules.runtime.action_dispatcher import ActionDispatcher
from app.rules.repositories.in_memory_rule_repository import InMemoryRuleRepository
from app.rules.services.rule_service import RuleService
from app.services.order_service import OrderService
from app.domain.state_machine import TransitionTableStateMachine
from app.services.ticket_service import InMemoryTicketService


router = APIRouter(prefix="/orders", tags=["orders"])

_order_service: OrderService | None = None


def _create_order_repository() -> OrderRepository:
    if os.getenv("USE_DYNAMODB", "").strip().lower() != "true":
        return InMemoryOrderRepository()

    table_name = os.getenv("ORDERS_TABLE_NAME")
    if table_name is None or not table_name.strip():
        raise RuntimeError(
            "Invalid DynamoDB configuration: set ORDERS_TABLE_NAME when USE_DYNAMODB=true."
        )

    return DynamoDbOrderRepository(table_name=table_name.strip())


def _create_order_service() -> OrderService:
    order_repository = _create_order_repository()
    state_machine = TransitionTableStateMachine()
    ticket_service = InMemoryTicketService()
    rule_service = RuleService(InMemoryRuleRepository())
    action_dispatcher = ActionDispatcher(ticket_service=ticket_service)
    return OrderService(order_repository, state_machine, rule_service, action_dispatcher)


def get_order_service() -> OrderService:
    global _order_service

    if _order_service is None:
        _order_service = _create_order_service()

    return _order_service


def _to_order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        product_ids=order.product_ids,
        amount=order.amount,
        state=order.state.value,
    )


@router.post("")
def create_order(
    request: CreateOrderRequest,
    order_service: Annotated[OrderService, Depends(get_order_service)],
) -> CreateOrderResponse:
    order = order_service.create_order(request.product_ids, request.amount)
    return CreateOrderResponse(order_id=order.id, state=order.state.value)


@router.get("/{order_id}")
def get_order(
    order_id: str,
    order_service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    order = order_service.get_order(order_id)
    return _to_order_response(order)


@router.get(
    "/{order_id}/history",
    response_model=list[OrderHistoryResponse],
)
def get_order_history(
    order_id: str,
    order_service: Annotated[OrderService, Depends(get_order_service)],
) -> list[OrderHistoryResponse]:
    return [
        OrderHistoryResponse.model_validate(entry.model_dump())
        for entry in order_service.get_order_history(order_id)
    ]


@router.post("/{order_id}/events")
def process_event(
    order_id: str,
    request: ProcessEventRequest,
    order_service: Annotated[OrderService, Depends(get_order_service)],
) -> ProcessEventResponse:
    try:
        event_type = OrderEvent(request.event_type)
    except ValueError as exc:
        raise InvalidEventError(request.event_type) from exc

    order = order_service.process_event(order_id, event_type, request.metadata)
    return ProcessEventResponse(id=order.id, state=order.state.value)
