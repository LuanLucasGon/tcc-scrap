from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class UpsertResult:
    """Quantas questões foram inseridas x atualizadas em um upsert."""

    inserted: int
    updated: int

    @classmethod
    def from_ids(
        cls, incoming_ids: Iterable[str], existing_ids: Iterable[str]
    ) -> UpsertResult:
        existing = set(existing_ids)
        seen: set[str] = set()
        inserted = 0
        updated = 0
        for question_id in incoming_ids:
            if question_id in seen:
                continue
            seen.add(question_id)
            if question_id in existing:
                updated += 1
            else:
                inserted += 1
        return cls(inserted=inserted, updated=updated)
