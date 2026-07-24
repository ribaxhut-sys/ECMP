# Provider Response Guide (TASK-060)

| Field | Value |
|---|---|
| ID | ARCH-PROVIDER-RESPONSE-GUIDE-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-060) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## ProviderResponse

Immutable envelope returned by every future provider.

| Field | Type | Notes |
|---|---|---|
| `provider_name` | str | Required, non-empty |
| `status` | `ProviderStatus` | READY / SUCCESS / FAILED / RETRYABLE / UNSUPPORTED |
| `correlation_id` | str | Required, non-empty |
| `provider_reference` | str \| None | External provider id when available |
| `error` | `ProviderError` \| None | Present on failure paths |
| `metadata` | `ProviderMetadata` | Frozen tags; optional latency / version / region |

## ProviderStatus

| Status | Meaning |
|---|---|
| `READY` | Provider / contract prepared; not yet sent |
| `SUCCESS` | Provider accepted / delivered (future) |
| `FAILED` | Non-retryable failure |
| `RETRYABLE` | Transient failure; may retry (future policy) |
| `UNSUPPORTED` | Channel / capability not supported |

## ProviderError

| Field | Notes |
|---|---|
| `code` | Stable machine code |
| `message` | Human-readable |
| `retryable` | bool |
| `category` | Validation / auth / rate-limit / timeout / provider / … |

## ProviderMetadata

| Field | Notes |
|---|---|
| `latency_ms` | >= 0 or None |
| `provider_version` | Optional |
| `region` | Optional |
| `tags` | Frozen `Mapping[str, str]` |

## Out of scope

Provider implementations, network I/O, DB, queue, scheduler, TASK-061+.
