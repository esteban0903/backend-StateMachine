from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RuleActionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str
    payload: dict[str, Any] = Field(default_factory=dict)


class RuleEvaluationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    matched_rule_ids: list[str] = Field(default_factory=list)
    action_results: list[RuleActionResult] = Field(default_factory=list)
    surcharge_value: float | None = None
