"""Deterministic duplicate scoring engine (FR-003 / BR-014) — no AI / ML."""



from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from app.modules.cm_batch1.duplicate_config import DuplicateConfig
from app.modules.cm_batch1.entities import ComplaintAggregate

_TOKEN_RE = re.compile(r"[a-z0-9]+")





def tokenize(text: str) -> frozenset[str]:

    return frozenset(t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 1)





def subject_similarity(left: str, right: str) -> float:

    """Jaccard token overlap in [0.0, 1.0]."""

    a, b = tokenize(left or ""), tokenize(right or "")

    if not a or not b:

        return 0.0

    return len(a & b) / len(a | b)





@dataclass(frozen=True)

class ScoredCandidate:

    complaint: ComplaintAggregate

    score: int

    recommendation: str

    hard_block: bool



    def as_dict(self) -> dict:

        return {

            "complaintId": self.complaint.complaint_id,

            "complaintNumber": self.complaint.complaint_number,

            "customerId": self.complaint.customer_id,

            "category": self.complaint.category,

            "channel": self.complaint.channel,

            "subject": self.complaint.subject,

            "status": self.complaint.status,

            "score": self.score,

            "recommendation": self.recommendation,

            "hardBlock": self.hard_block,

            "open": self.complaint.status != "CLOSED",

            "createdAt": self.complaint.created_at.isoformat(),

        }





def score_candidate(

    *,

    intake_category: str | None,

    intake_subject: str | None,

    intake_channel: str | None,

    existing: ComplaintAggregate,

    config: DuplicateConfig,

) -> int:

    """Deterministic 0–100 score: CustomerId + category + subject similarity + channel."""

    score = config.score_customer  # candidates are same-customer within window

    if (

        intake_category

        and intake_category.strip().upper() == existing.category.strip().upper()

    ):

        score += config.score_category

    sim = subject_similarity(intake_subject or "", existing.subject)

    score += int(round(sim * config.score_subject_max))

    if (

        intake_channel

        and intake_channel.strip().upper() == existing.channel.strip().upper()

    ):

        score += config.score_channel

    return min(100, max(0, score))





def recommendation_for(

    *,

    score: int,

    intake_category: str | None,

    config: DuplicateConfig,

) -> tuple[str, bool]:

    """Return (recommendation, hard_block)."""

    if score < config.threshold:

        return "none", False

    hard = config.is_hard_block_category(intake_category)

    if hard:

        return "hard_block", True

    if score >= 90:

        return "link_existing", False

    return "override_allowed", False





def evaluate_candidates(

    *,

    intake_category: str | None,

    intake_subject: str | None,

    intake_channel: str | None,

    candidates: list[ComplaintAggregate],

    config: DuplicateConfig,

    as_of: datetime | None = None,

) -> list[ScoredCandidate]:

    _ = as_of

    scored: list[ScoredCandidate] = []

    for row in candidates:

        score = score_candidate(

            intake_category=intake_category,

            intake_subject=intake_subject,

            intake_channel=intake_channel,

            existing=row,

            config=config,

        )

        rec, hard = recommendation_for(

            score=score, intake_category=intake_category, config=config

        )

        if score >= config.threshold:

            scored.append(

                ScoredCandidate(

                    complaint=row,

                    score=score,

                    recommendation=rec,

                    hard_block=hard,

                )

            )

    scored.sort(key=lambda c: (-c.score, c.complaint.created_at))

    return scored[: config.candidate_limit]


