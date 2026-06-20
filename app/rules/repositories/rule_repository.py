from __future__ import annotations

from typing import Protocol

from app.rules.models.rule import Rule


class RuleRepository(Protocol):
    def get_all_enabled(self) -> list[Rule]:
        """Return all enabled rules, ordered by the repository's storage semantics."""

    def save(self, rule: Rule) -> Rule:
        """Persist the rule and return the saved instance."""

    def get_by_id(self, rule_id: str) -> Rule | None:
        """Return a rule for the given identifier, or None if it does not exist."""
