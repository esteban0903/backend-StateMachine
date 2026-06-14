from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OrderHistoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: str
    previous_state: str
    new_state: str
    timestamp: str