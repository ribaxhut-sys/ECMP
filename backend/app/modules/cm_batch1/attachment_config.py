"""Batch 1 attachment policy via AttachmentConfigProvider (FR-004 / BR-012)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class AttachmentConfig:
    max_file_size_bytes: int = 10 * 1024 * 1024
    allowed_mime_types: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/webp",
                "video/mp4",
                "text/plain",
            }
        )
    )
    allowed_classifications: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "customer_evidence",
                "internal_evidence",
                "official_letter",
            }
        )
    )
    checksum_algorithm: str = "SHA-256"
    staging_ttl_hours: int = 24
    abandoned_staging_action: str = "VOID"
    duplicate_checksum_policy: str = "REJECT_WITH_EXISTING_REFERENCE"
    antivirus_mode: str = "STUB_ONLY"
    # Temporary CAP-011 aggregate for pre-create staging sessions.
    staging_aggregate_type: str = "Queue"


class AttachmentConfigProvider(Protocol):
    def get(self) -> AttachmentConfig: ...


@dataclass
class DefaultAttachmentConfigProvider:
    """Default values; replace with ops-backed provider later."""

    _config: AttachmentConfig = field(default_factory=AttachmentConfig)

    def get(self) -> AttachmentConfig:
        return self._config


DEFAULT_ATTACHMENT_CONFIG_PROVIDER = DefaultAttachmentConfigProvider()
