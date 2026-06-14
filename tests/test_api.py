from __future__ import annotations

from app.domain.enums.order_event import OrderEvent


def test_post_orders_creates_order(client) -> None:
    # Arrange
    payload = {"productIds": ["P1", "P2"], "amount": 1200}

    # Act
    response = client.post("/orders", json=payload)

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["orderId"]
    assert body["state"] == "Pending"


def test_get_orders_returns_created_order(client) -> None:
    # Arrange
    create_response = client.post(
        "/orders",
        json={"productIds": ["P1", "P2"], "amount": 1200},
    )
    order_id = create_response.json()["orderId"]

    # Act
    response = client.get(f"/orders/{order_id}")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == order_id
    assert body["productIds"] == ["P1", "P2"]
    assert body["amount"] == 1200
    assert body["state"] == "Pending"


def test_process_event_updates_state(client) -> None:
    # Arrange
    create_response = client.post(
        "/orders",
        json={"productIds": ["P1", "P2"], "amount": 1200},
    )
    order_id = create_response.json()["orderId"]

    client.post(
        f"/orders/{order_id}/events",
        json={"eventType": OrderEvent.NO_VERIFICATION_NEEDED.value, "metadata": {}},
    )

    # Act
    response = client.post(
        f"/orders/{order_id}/events",
        json={"eventType": OrderEvent.PAYMENT_SUCCESSFUL.value, "metadata": {}},
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == order_id
    assert body["state"] == "Confirmed"


def test_process_event_invalid_event_returns_bad_request(client) -> None:
    # Arrange
    create_response = client.post(
        "/orders",
        json={"productIds": ["P1", "P2"], "amount": 1200},
    )
    order_id = create_response.json()["orderId"]

    # Act
    response = client.post(
        f"/orders/{order_id}/events",
        json={"eventType": "notARealEvent", "metadata": {}},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid event 'notARealEvent'."}


def test_process_event_invalid_transition_returns_bad_request(client) -> None:
    # Arrange
    create_response = client.post(
        "/orders",
        json={"productIds": ["P1", "P2"], "amount": 1200},
    )
    order_id = create_response.json()["orderId"]

    # Act
    response = client.post(
        f"/orders/{order_id}/events",
        json={"eventType": OrderEvent.ITEM_DISPATCHED.value, "metadata": {}},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid transition from 'Pending' using event 'itemDispatched'."
    }


def test_get_order_not_found_returns_not_found(client) -> None:
    # Act
    response = client.get("/orders/missing-order-id")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Order 'missing-order-id' was not found."}


def test_get_order_history_returns_state_transitions(client) -> None:
    # Arrange
    create_response = client.post(
        "/orders",
        json={"productIds": ["P1", "P2"], "amount": 1200},
    )
    order_id = create_response.json()["orderId"]

    client.post(
        f"/orders/{order_id}/events",
        json={"eventType": OrderEvent.NO_VERIFICATION_NEEDED.value, "metadata": {}},
    )
    client.post(
        f"/orders/{order_id}/events",
        json={"eventType": OrderEvent.PAYMENT_SUCCESSFUL.value, "metadata": {}},
    )

    # Act
    response = client.get(f"/orders/{order_id}/history")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert [entry["eventType"] for entry in body] == [
        OrderEvent.NO_VERIFICATION_NEEDED.value,
        OrderEvent.PAYMENT_SUCCESSFUL.value,
    ]
    assert [entry["previousState"] for entry in body] == ["Pending", "PendingPayment"]
    assert [entry["newState"] for entry in body] == ["PendingPayment", "Confirmed"]
    assert all(entry["timestamp"].endswith("Z") for entry in body)
