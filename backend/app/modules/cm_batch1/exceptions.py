"""CM Batch 1 domain/application exceptions (HTTP-mapped via ApiError)."""

from __future__ import annotations

import logging
from typing import Any

from app.core.errors import ConflictError

_logger = logging.getLogger(__name__)


class ReplayConflict(ConflictError):
    """Idempotency-Key and Channel Message Id claim different ComplaintIds.

    HTTP 409 with code ``REPLAY_CONFLICT``. ComplaintId remains the canonical
    identity; callers must not invent a merged aggregate.

    Cross-org ComplaintIds and other diagnostics stay off the public envelope
    (``details``); they are retained on ``diagnostic_details`` for logs/audit.
    """

    def __init__(
        self,
        message: str = (
            "Idempotency-Key and Channel Message Id map to different complaints"
        ),
        *,
        diagnostic_details: dict[str, Any] | None = None,
    ) -> None:
        self.diagnostic_details = dict(diagnostic_details or {})
        if self.diagnostic_details:
            _logger.warning(
                "replay_conflict diagnostics=%s", self.diagnostic_details
            )
        # Public details: no ComplaintIds / foreign resource identifiers.
        public = {"reason": "idempotency_channel_conflict"}
        # Bypass ConflictError.__init__ so the envelope code is distinct.
        super(ConflictError, self).__init__(
            409, "REPLAY_CONFLICT", message, public
        )
