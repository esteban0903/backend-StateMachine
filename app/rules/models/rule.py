from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.rules.models.action import RuleAction
from app.rules.models.condition import RuleCondition


class Rule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    enabled: bool = True
    priority: int = 0
    condition: RuleCondition
    actions: list[RuleAction] = Field(default_factory=list)
    description: str | None = None
