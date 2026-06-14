# AI_CONTEXT.md

## Project

Bridge Backend Engineering Technical Assessment

Implement an MVP backend for an order processing system driven by a State Machine.

The goal is to demonstrate software engineering fundamentals, clean architecture, extensibility, and maintainability.

---

# Core Principles

## KISS

Prefer the simplest solution that satisfies the requirements.

Avoid:

* CQRS
* Event Sourcing
* Microservices
* Message brokers
* Dependency injection frameworks
* Complex design patterns that do not provide clear value

## SOLID

Apply SOLID principles where they improve maintainability and testability.

Prioritize readability and simplicity over theoretical purity.

## Clean Architecture

Separate responsibilities clearly:

* Domain
* Application Services
* Infrastructure
* API

The domain layer must not depend on FastAPI or infrastructure concerns.

---

# Tech Stack

## Backend

* Python 3.13
* FastAPI
* Pydantic
* Pytest

## Storage

* In-memory repository using a Python dictionary

## Frontend (Optional Bonus)

* React
* Vite

---

# Required Architecture

app/
├── api/
├── domain/
│   ├── models/
│   ├── enums/
│   └── exceptions/
├── services/
│   ├── state_machine.py
│   ├── order_service.py
│   └── event_handlers/
├── repositories/
├── integrations/
└── main.py

---

# Domain Model

## Order

Fields:

* id: str
* product_ids: list[str]
* amount: float
* state: OrderState

Optional:

* event_history: list[EventLog]

---

# MVP States

* Pending
* OnHold
* PendingPayment
* Confirmed
* Processing
* Shipped
* Delivered

---

# Supported Events

* pendingBiometricalVerification
* noVerificationNeeded
* paymentFailed
* orderCancelled
* biometricalVerificationSuccessful
* verificationFailed
* orderCancelledByUser
* paymentSuccessful
* preparingShipment
* itemDispatched
* itemReceivedByCustomer
* deliveryIssue

---

# State Machine Requirements

Use a transition table.

Example concept:

TRANSITIONS[current_state][event_type] -> next_state

Do not use large nested if/else chains.

Expose:

get_next_state(current_state, event_type)

Raise a domain exception for invalid transitions.

---

# State Transitions

Pending:

* pendingBiometricalVerification -> OnHold
* noVerificationNeeded -> PendingPayment
* paymentFailed -> Cancelled
* orderCancelled -> Cancelled

OnHold:

* biometricalVerificationSuccessful -> PendingPayment
* verificationFailed -> Cancelled
* orderCancelledByUser -> Cancelled

PendingPayment:

* paymentSuccessful -> Confirmed

Confirmed:

* preparingShipment -> Processing

Processing:

* itemDispatched -> Shipped

Shipped:

* itemReceivedByCustomer -> Delivered
* deliveryIssue -> OnHold

---

# Business Rules

## paymentFailed

When a paymentFailed event is received:

If:

amount > 1000

Then:

Create a support review ticket.

Important:

This rule must be isolated from the StateMachine.

Do not embed business logic inside transition definitions.

Business rules must be easy to extend.

---

# Repository Pattern

All persistence must happen through repositories.

Example responsibilities:

* get_by_id(...)
* save(...)
* update(...)

Use Protocol abstractions before concrete implementations.

Services must depend on abstractions, not implementations.

---

# Error Handling

Provide meaningful domain errors.

Examples:

* OrderNotFoundError
* InvalidTransitionError
* InvalidEventError
* ValidationError

---

# Testing Requirements

Minimum coverage:

## State Machine

* Valid transition
* Invalid transition

## Order Service

* Create order
* Process event
* paymentFailed business rule

---

# Non Goals

Do not implement:

* Authentication
* Authorization
* Databases
* Redis
* Kafka
* AWS services
* Event sourcing
* Distributed systems concerns

Keep the solution intentionally simple.

---

# Definition of Done

* Create Order endpoint
* Get Order endpoint
* Process Event endpoint
* Repository Pattern
* State Machine abstraction
* paymentFailed business rule
* Unit tests
* Documentation

---

# AI Instructions

When generating code:

* Follow KISS first.
* Apply SOLID pragmatically.
* Avoid unnecessary abstractions.
* Prefer composition over inheritance.
* Use type hints everywhere.
* Keep files small and focused.
* Explain architectural decisions.
* Explain tradeoffs.
* Suggest improvements only if they provide clear value.

Assume the code will be reviewed by senior backend engineers.
