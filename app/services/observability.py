from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit


SERVICE_NAME = "bridge-order-api"
METRICS_NAMESPACE = "BridgeOrderAPI"


logger = Logger(service=SERVICE_NAME)
metrics = Metrics(namespace=METRICS_NAMESPACE, service=SERVICE_NAME)
tracer = Tracer(service=SERVICE_NAME)


@contextmanager
def order_logging_context(
    *,
    order_id: str,
    event_type: str | None,
    current_state: str | None,
    next_state: str | None,
) -> Iterator[None]:
    logger.append_keys(
        order_id=order_id,
        event_type=event_type,
        current_state=current_state,
        next_state=next_state,
    )
    try:
        yield
    finally:
        logger.clear_state()


def increment_metric(metric_name: str) -> None:
    metrics.add_metric(name=metric_name, unit=MetricUnit.Count, value=1)