"""Duplicate detection policy config (FR-003 / BR-014) — OQ defaults until ops config lands."""



from __future__ import annotations



from dataclasses import dataclass, field





@dataclass(frozen=True)

class DuplicateConfig:

    """Replaceable operational policy; all FR-003 logic must read from this object."""



    threshold: int = 70

    time_window_days: int = 30

    candidate_limit: int = 20

    minimum_justification_length: int = 20

    hard_block_categories: frozenset[str] = field(

        default_factory=lambda: frozenset({"FRAUD", "REGULATORY"})

    )

    policy_version: str = "cm-batch1-dup-v1"

    # Weight budget totals 100 for deterministic scoring (no AI).

    score_customer: int = 40

    score_category: int = 30

    score_subject_max: int = 25

    score_channel: int = 5

    enforce_on_create: bool = True



    def is_hard_block_category(self, category: str | None) -> bool:

        if not category:

            return False

        return category.strip().upper() in {

            c.upper() for c in self.hard_block_categories

        }





DEFAULT_DUPLICATE_CONFIG = DuplicateConfig()


