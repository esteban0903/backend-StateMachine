from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
import uvicorn

from app.api.orders import router as orders_router
from app.api.orders import get_order_service
from app.domain.exceptions.domain_exceptions import (
    DomainError,
    InvalidEventError,
    InvalidTransitionError,
    OrderNotFoundError,
)

app = FastAPI(
    title="Bridge Order API",
    root_path="/Prod",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://main.d32hexwtvl9soy.amplifyapp.com",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders_router)
get_order_service()

handler = Mangum(app)


@app.exception_handler(OrderNotFoundError)
async def handle_order_not_found(_: Request, exc: OrderNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidTransitionError)
async def handle_invalid_transition(_: Request, exc: InvalidTransitionError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(InvalidEventError)
async def handle_invalid_event(_: Request, exc: InvalidEventError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(DomainError)
async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def handle_unexpected_error(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
