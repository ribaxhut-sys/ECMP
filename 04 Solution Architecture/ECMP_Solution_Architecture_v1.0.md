# ECMP Solution Architecture v1.0

| Field | Value |
|---|---|
| ID | SA-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Leads, Security, Ops, BA Lead |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Draft awal desain solusi teknis ECMP, diturunkan dari `01 Business Blueprint`, `02 Business Rules`, dan `05 Architecture Decision Records` (ADR-001, ADR-002, ADR-003). Source diagram (context, container, sequence, deployment) tersedia di `23 Assets/mermaid/` dan direferensikan dari §3, §4, §5, dan §9.

## 1. Goals & Constraints

**Goals**
- Mendukung 7 domain bisnis dari Blueprint (Core Platform, CRM, ECMF, KPI & Performance, Dashboard & Analytics, Notification, Administration) sebagai unit desain yang jelas batasnya.
- ECMF tetap responsif terhadap user meski domain konsumen (KPI, Dashboard, Notification) lambat/down — lihat ADR-001.
- Tidak menduplikasi ownership data pelanggan — lihat ADR-002.
- Perubahan proses bisnis rutin tidak memerlukan rilis kode — lihat ADR-003.

**Constraints**
- ECMP wajib terintegrasi dengan Customer Master eksternal yang sudah ada (di luar kendali tim ECMP).
- Keputusan teknologi backend **sudah diambil**: FastAPI + PostgreSQL (ADR-004); message broker **ditunda eksplisit** (ADR-009); frontend masih deferred — status lengkap di bagian "Open Decisions" (setelah §11).
- Audit trail harus immutable secara teknis (BR-CP-03), bukan hanya aturan proses.

## 2. Architecture Principles (Technical)
1. **Domain-oriented boundaries** — 7 domain di Blueprint menjadi batas modul/service, selaras `20 Domain Architecture`.
2. **Event-driven integration by default** antar domain (ADR-001); komunikasi sinkron hanya untuk operasi yang butuh respons langsung ke user (mis. validasi saat input).
3. **Read-only cache untuk data eksternal** (ADR-002) — tidak ada domain yang menjadi SoR untuk data yang dimiliki sistem lain.
4. **Configuration over code** untuk rule yang diklasifikasikan *Configuration* di `02 Business Rules` (ADR-003); rule *Hardcoded* diimplementasikan sebagai invariant di level aplikasi, tidak bisa dimatikan lewat config.
5. **Audit-first** — setiap write operation pada entity signifikan (Case, Config, Role) menghasilkan entri Audit Log yang tidak bisa diubah/dihapus melalui jalur aplikasi manapun.
6. **Idempotent consumers** — semua consumer event harus toleran terhadap duplicate delivery (at-least-once, ADR-001).

## 3. Context Diagram (naratif)
Aktor eksternal utama: Customer Service/Handler/Supervisor/Manager/Executive/Administrator (internal users), Customer Master (sistem eksternal, read-only), gateway email/channel eksternal (opsional, untuk Notification).

Diagram source: `../23 Assets/mermaid/ecmp-context.mmd` (context detail per domain).

```mermaid
graph LR
  User[Internal Users] --> ECMP[ECMP Platform]
  ECMP --> CM[(Customer Master - external, read-only)]
  ECMP --> GW[Email/Channel Gateway - optional]
  ECMP --> Audit[(Audit Log)]
```

## 4. Container / Component View (naratif)
Tujuh domain dipetakan sebagai container/service kandidat (granularity final menunggu ADR teknologi):

| Domain | Peran Utama | Bergantung Pada |
|---|---|---|
| Core Platform | Identity, AuthN/AuthZ, Organization, Config, Audit | — (fondasi, semua domain lain bergantung padanya) |
| CRM | Customer 360 view, cache read-only Customer Master | Core Platform, Customer Master (eksternal) |
| ECMF | Case/Complaint lifecycle: create → **route** → assign → process → review → close; multi-source/target (DEC-018) + Routing (TASK-043) + **Complaint Context** (TASK-044) + **Complaint Events** factory (TASK-045) + **in-process Event Dispatcher** (TASK-046; not a bus) | Core Platform, CRM (konteks), Administration (workflow/SLA config) |
| KPI & Performance | Kalkulasi metrik dari event operasional; **TASK-051:** in-memory `KpiProjection` from Complaint events (no HTTP projection API yet); TASK-026 summary API tetap terpisah | ECMF (event / context), Administration (SLA config) |
| Dashboard & Analytics | Visualisasi operasional/eksekutif; **TASK-050:** in-memory `DashboardProjection` from Complaint events (no HTTP projection API yet) | KPI & Performance, ECMF, CRM, Core Platform (authz) |
| Notification | Routing & delivery notifikasi berbasis event; **TASK-047/048/049:** `Notification` → `NotificationIntent` → `NotificationDelivery` (PLANNED only; no transport send yet) | Semua domain (event source), Core Platform (recipient resolution) |
| Administration | Config, reference data, role-permission | Core Platform |

Event bus (teknologi TBD) menjadi tulang punggung komunikasi ECMF → KPI/Dashboard/Notification/Core Platform, sesuai `08 Event Catalog`.

**TASK-045 (Complaint Event Foundation):** runtime ECMF menstandarkan pembuatan `ComplaintEvent` immutable via `ComplaintEventFactory` (in-memory only). Belum ada bus/broker — selaras ADR-009 (broker deferred). Lihat `../20 Domain Architecture/ECMF/COMPLAINT_EVENTS.md`.

**TASK-046 (In-Process Event Dispatcher):** `ComplaintService` → `ComplaintEventFactory` → `EventDispatcher.dispatch` → registered `EventHandler`s (sync, registration order, failure-isolated `DispatchResult`). Bukan Event Bus / Kafka / RabbitMQ / Event Store. Lihat `../20 Domain Architecture/ECMF/EVENT_DISPATCHER.md`.

**TASK-047 (Notification Domain Foundation):** `NotificationEventHandler` adalah consumer pertama `EventDispatcher`. `NotificationFactory.from_event` membangun `Notification` immutable (in-memory). Transport-independent — **tanpa** email/WhatsApp/SMS/Push/WebSocket. `ComplaintService` tidak mengimpor Notification. Lihat `../20 Domain Architecture/Notification/EVENT_CONSUMER.md`.

**TASK-048 (Notification Intent Foundation):** `NotificationIntentFactory.from_notification` membangun `NotificationIntent` immutable (what to deliver). Channel enum only (`EMAIL`/`WHATSAPP`/`PUSH`/`SMS`/`WEBSOCKET`). Tidak ada transport adapter / send / queue write. Lihat `../20 Domain Architecture/Notification/NOTIFICATION_INTENT.md`.

**TASK-049 (Notification Delivery Foundation):** `NotificationDeliveryFactory.from_intent` membangun `NotificationDelivery` immutable (planned delivery action per preferred channel). Status **PLANNED** only. Bukan transport, bukan sending, bukan queue. Lihat `../20 Domain Architecture/Notification/DELIVERY_FOUNDATION.md`.

**TASK-050 (Dashboard Projection Foundation):** `DashboardProjectionHandler` mengonsumsi Complaint events via `EventDispatcher` dan memperbarui `DashboardProjection` in-memory (read model). Tidak query Complaint aggregate / `ComplaintService` saat update. Belum ada HTTP endpoint projection. Lihat `../20 Domain Architecture/Dashboard/PROJECTION_GUIDE.md`.

**TASK-051 (KPI Projection Foundation):** `KpiProjectionHandler` mengonsumsi Complaint events via `EventDispatcher` dan memperbarui `KpiProjection` in-memory (read model: received/closed/resolved/escalated, current open/in-progress, SLA breached flag, derived closure/resolution rates). Tidak query Complaint aggregate / `ComplaintService` saat update. Belum ada HTTP endpoint projection. Lihat `../20 Domain Architecture/KPI/PROJECTION_GUIDE.md`.

**TASK-052 (Workflow Foundation):** Runtime orchestration **planner** (bukan domain Blueprint ke-8; bukan Administration Workflow Config ADR-008). `WorkflowEventHandler` mengonsumsi Complaint events via `EventDispatcher`. `WorkflowEngine` mencocokkan `WorkflowTrigger` → `WorkflowDefinition`, lalu merekam `WorkflowInstance` (status **CREATED** only) di `WorkflowInstanceStore` in-memory. **Tidak** mengeksekusi action, invoke Notification/Assignment, atau HTTP API. Lihat `../20 Domain Architecture/Workflow/WORKFLOW_ARCHITECTURE.md`.

**TASK-053 (Execution Plan Foundation):** Shared infrastructure `ExecutionPlan` / `ExecutionTask` (status **PLANNED**, `executed=false`). `ExecutionPlanner` memetakan `WorkflowInstance` → `ExecutionPlan` (Workflow = producer pertama; future: Scheduled Jobs / SLA / AI / Manual / Integrations). `ExecutionRegistry` mendaftarkan handler untuk masa depan **tanpa** invoke. Tidak ada execution / send / schedule / HTTP / DB. Lihat `../20 Domain Architecture/Execution/EXECUTION_ARCHITECTURE.md`.

**TASK-054 (Execution Runtime Foundation):** Shared infrastructure `ExecutionRuntime` mengonsumsi `ExecutionPlan` dan menyiapkan `ExecutionRun` / `ExecutionRunTask` (status **CREATED** only) + `ExecutionContext` + `ExecutionResult` (bentuk foundation). `ExecutionRunStore` in-memory. Runtime **tidak** mengetahui Complaint / Workflow / Notification; **tidak** invoke handler / registry / send. Tidak ada HTTP / DB / queue / scheduler. Lihat `../20 Domain Architecture/Execution/EXECUTION_RUNTIME_ARCHITECTURE.md`.

**TASK-055 (Execution Engine Foundation):** Shared infrastructure `ExecutionEngine` mengelola lifecycle `ExecutionRun` via `ExecutionLifecycle` / `ExecutionStateMachine` (CREATED → READY → RUNNING → COMPLETED|FAILED|CANCELLED). Validasi transisi saja — **tidak** execute handler / registry / Notification / externals. `ExecutionEngineResult` (`success`, `previous_state`, `new_state`, `reason`). Tidak ada HTTP / DB / scheduler. Lihat `../20 Domain Architecture/Execution/EXECUTION_ENGINE_ARCHITECTURE.md`.

**TASK-056 (Execution Dispatcher Foundation):** Shared infrastructure `ExecutionDispatcher` menghubungkan `ExecutionRun` + `ExecutionTask` ke `ExecutionRegistry` via `DispatchRequest` / `DispatchResult` + `DispatchValidator` + `DispatchPolicy` (**SEQUENTIAL** only). Validasi kesiapan (status READY|RUNNING, task ada, handler terdaftar) — **tidak** invoke handler. Tidak ada HTTP / DB / queue. Lihat `../20 Domain Architecture/Execution/EXECUTION_DISPATCHER_ARCHITECTURE.md`.

**TASK-057 (Delivery Engine Foundation):** Shared infrastructure `DeliveryEngine` mengonversi `DispatchRequest` → `DeliveryRequest` / `DeliveryResult` + `DeliveryValidator` + `DeliveryPolicy` (**DIRECT** only) + `DeliveryContext`. Validasi recipient / channel / template / payload — **tidak** send, **tidak** call provider/transport (SMTP/WhatsApp/FCM/APNS/SMS/Webhook/AI). Tidak ada HTTP / DB / queue / retry. Lihat `../20 Domain Architecture/Delivery/DELIVERY_ENGINE_ARCHITECTURE.md`.

**TASK-058 (Transport Adapter Foundation):** Shared infrastructure `TransportAdapter` (abstract) + `TransportRegistry` + `TransportSelector` + `TransportCapability` + `TransportResult`. Seleksi adapter by channel dari `DeliveryRequest` — **tidak** call `send()`, **tidak** implementasi provider (SMTP/Twilio/Meta/Firebase/APNS/Slack/Teams/Webhook), **tidak** network I/O. Tidak ada HTTP / DB / queue. Lihat `../20 Domain Architecture/Delivery/TRANSPORT_ARCHITECTURE.md`.

**TASK-059 (Provider Executor Foundation):** Shared infrastructure `ProviderExecutor` + `ProviderExecutionRequest` / `ProviderExecutionResult` + `ProviderExecutionValidator` + `ProviderExecutionPolicy` (**SYNC_PREPARE** only). Menyiapkan execution contract dari `DeliveryRequest` + `TransportAdapter` — **tidak** invoke `send()` / `health()`, **tidak** network I/O (HTTP/SMTP/WhatsApp/Firebase/Webhook/Queue). Tidak ada DB / scheduler / retry / timeout. Lihat `../20 Domain Architecture/Delivery/PROVIDER_EXECUTOR_ARCHITECTURE.md`.

**TASK-060 (Provider Contract Foundation):** Shared contracts `ProviderResponse` + `ProviderStatus` (READY/SUCCESS/FAILED/RETRYABLE/UNSUPPORTED) + `ProviderError` + `ProviderMetadata` + abstract `ProviderException`. Semua future provider harus mengembalikan envelope yang sama — **tidak** implementasi provider, **tidak** network I/O. Tidak ada DB / scheduler / queue. Lihat `../20 Domain Architecture/Delivery/PROVIDER_CONTRACT_ARCHITECTURE.md`.

**TASK-061 (Queue Domain Foundation):** First-class domain `Queue` (aggregate root) + `QueueTicket` (immutable) + `QueueCounter` + `QueuePolicy` (FIFO / PRIORITY_QUEUE) + `QueueStatus` (OPEN/PAUSED/CLOSED) + `QueuePriority` (NORMAL/PRIORITY/VIP). Core model only — **tidak** REST / DB / repository / display / kiosk / calling. Lihat `../20 Domain Architecture/Queue/QUEUE_DOMAIN_ARCHITECTURE.md`.

**TASK-062 (Queue Application Foundation):** Application CQRS layer — `QueueDomainService` + commands (Create/Open/Pause/Close/Issue/CallNext/Complete/Cancel) + queries (GetQueue/GetQueueTickets/GetWaitingTickets) + immutable DTOs + dedicated `QueueTicketStatus` (WAITING/CALLED/SERVING/COMPLETED/CANCELLED/SKIPPED). **Tidak** REST / DB / repository / Redis / display / kiosk / notification. Lihat `../20 Domain Architecture/Queue/QUEUE_APPLICATION_ARCHITECTURE.md`.

Diagram source: `../23 Assets/mermaid/ecmp-container.mmd` (7 domain + event backbone outbox ADR-009 + Customer Master eksternal + gateway opsional; arah dependensi per tabel di atas).

## 5. Runtime & Sequence Views (contoh alur utama)
**Alur: Case dibuat sampai SLA breach terdeteksi**
```mermaid
sequenceDiagram
  actor CS as Customer Service
  participant ECMF
  participant Bus as Event Bus
  participant KPI as KPI & Performance
  participant Notif as Notification
  CS->>ECMF: Create Case
  ECMF->>Bus: publish CaseCreated
  Bus->>KPI: consume CaseCreated (init SLA Clock)
  Note over KPI: SLA Clock berjalan berdasarkan SLA Config
  KPI->>Bus: publish SLABreached (jika due terlampaui)
  Bus->>Notif: consume SLABreached
  Notif-->>CS: alert / escalate ke supervisor
```
Sequence lain (assignment, closure, config change) mengikuti pola yang sama.

Diagram source: `../23 Assets/mermaid/create-case-sequence.mmd` (create case Sprint-01 nyata: `POST /v1/cases` → validasi → stub CM → transaksi tunggal cases + audit_log + outbox EVT-001 → 201, per FR-001c/ADR-009).

## 6. Data Architecture
- Rujuk `06 Data Dictionary` untuk entity list per domain.
- Setiap domain memiliki data store sendiri (data ownership per domain, selaras prinsip #1); tidak ada shared database lintas domain — komunikasi data lintas domain melalui event atau API read, bukan akses database langsung.
- Customer Reference (CRM) adalah cache read-only, disinkronkan dari Customer Master (ADR-002) — mekanisme sinkron (event vs scheduled pull) masih Open Decision.
- Audit Log disarankan append-only store terpisah (mis. write-once log store) agar imutabilitas terjamin secara teknis, bukan hanya lewat permission aplikasi.
- **Complaint Context (TASK-044):** operational read model (`ComplaintContext`) assembled in-process from Complaint + Assignment + SLA + Routing. **No dedicated table and no cache** — see `20 Domain Architecture/ECMF/COMPLAINT_CONTEXT.md`.

## 7. Integration Architecture
- **Internal (antar domain ECMP)**: event-driven melalui message broker (ADR-001), skema di `08 Event Catalog`.
- **Eksternal — Customer Master**: read-only — kontrak terdefinisi di `09 Integration Catalog/ECMP_INT_001_Customer_Master_Read_v0.1.md` (INT-001: mode stub Sprint-01, mode real dengan timeout + fallback); API planned = API-010 (`07 API Catalog`).
- **Eksternal — Email/Channel Gateway**: dipicu dari domain Notification, sifatnya opsional dan dapat ditambah bertahap (`09 Integration Catalog/ECMP_INT_002_Email_Gateway_v0.1.md`).
- Semua integrasi eksternal harus punya fallback behavior yang terdefinisi — untuk Customer Master sudah didefinisikan di INT-001; integrasi baru wajib mendefinisikannya sebelum implementasi.

## 8. Security Architecture (high-level)
- AuthN/AuthZ terpusat di Core Platform (BR-CP-01, BR-CP-02); domain lain tidak boleh implementasi otorisasi sendiri di luar Core Platform.
- Model autentikasi konkret: arah diputuskan di **ADR-007** (Bearer slice → JWT/OIDC sebelum shared UAT); desain fase target di **ADR-012** (**Accepted**) + `10 Security and Access Standards/ECMP_Target_Authentication_Architecture_v1.0.md` (SEC-AUTH-001; design normative under ADR-012, document badge may remain Proposed until Board sync); SSO penuh tetap Future Enhancement / Enterprise Mode (ADR-014 Proposed — Relationship Pending).
- Data sensitif (PII pelanggan, kontak) memerlukan klasifikasi dan masking — rujuk `06 Data Dictionary` bagian PII dan `10 Security and Access Standards` (Security Standards, Role Access Matrix, AuthN Limitations Register).
- Audit trail immutable menjadi kontrol keamanan inti, bukan opsional (prinsip #5).

## 9. Deployment Architecture (high-level, sebagian Open Decision)
DEV sudah diputuskan: docker-compose (Postgres) + GitHub Actions CI (lihat `14 Deployment Standards` dan Open Decisions #5). Platform produksi (cloud provider, container orchestration) masih open. Rekomendasi awal:
- Deploy domain sebagai service terpisah agar sejalan dengan prinsip domain-oriented boundaries dan event-driven decoupling.
- Environment minimal: Development, SIT/UAT, Production — detail di `14 Deployment Standards`.
- Observability (log, metric, trace) harus mencakup event bus (lag, dead-letter queue) mengingat ketergantungan besar pada pola async.

Diagram source: `../23 Assets/mermaid/deployment-dev-ci.mmd` (deployment view DEV: compose Postgres + uvicorn; CI: ruff → contract → alembic → pytest per `backend-ci.yml`).

## 10. Risks & Trade-offs
| Risk | Dampak | Mitigasi Awal |
|---|---|---|
| Broker belum dipilih (ditunda by design) | Async lintas domain belum bisa produksi | ADR-009: outbox lokal untuk Sprint-01; pilih broker sebelum multi-service |
| Eventual consistency Dashboard/KPI membingungkan user | Data terlihat "salah" padahal hanya delay | Tampilkan timestamp "as of" di semua widget agregat (BR-DASH-02) |
| Customer Master down memengaruhi CRM & ECMF | Customer Service tidak bisa melihat konteks pelanggan | Cache read-only (ADR-002) + fallback UI yang jelas |
| Role-Permission Matrix disebut di 2 domain (Core Platform & Administration) | Ambiguitas ownership | **Resolved** — ADR-008: Core Platform = SoT; Administration = konfigurator |

## 11. ADR References
- ADR-001 — Event-Driven Domain Integration (Accepted)
- ADR-002 — ECMP Not System of Record for Customer Data (Accepted)
- ADR-003 — Configuration-First Principle (Accepted)
- ADR-004 — Implementation Stack Sprint-01 (Accepted)
- ADR-005 — Backend Layering, minimal split (Accepted)
- ADR-006 — API Versioning Strategy (Accepted)
- ADR-007 — Authentication Model, slice + target (Accepted)
- ADR-008 — Role-Permission Matrix SoT & Workflow Config Ownership (Accepted)
- ADR-009 — Message Broker Deferral, outbox first (Accepted)
- ADR-012 — Target Authentication Architecture, JWT/OIDC design (**Accepted**)

## Open Decisions (status 2026-07-21)
1. Teknologi message broker — **ditunda secara eksplisit** (ADR-009): outbox lokal dulu, pilih broker sebelum multi-service.
2. Bahasa/framework dan database — **diputuskan** untuk backend (ADR-004); frontend deferred.
3. Mekanisme sinkronisasi Customer Reference — **dibatasi**: Sprint-01 stub read-only (lihat `09 Integration Catalog/INT-001`); event vs scheduled pull diputuskan saat integrasi CM nyata.
4. Model autentikasi — **diputuskan arah** (ADR-007): Bearer slice → JWT/OIDC sebelum shared UAT.
5. Platform deployment & CI/CD — DEV via docker-compose + GitHub Actions (lihat `14 Deployment Standards`); produksi tetap open.
6. Role-Permission Matrix SoT — **diputuskan** (ADR-008): Core Platform sebagai SoT, Administration sebagai konfigurator.

## Related
- `../05 Architecture Decision Records`
- `../06 Data Dictionary`
- `../07 API Catalog`
- `../08 Event Catalog`
- `../09 Integration Catalog`
- `../19 Reference Architecture`
- `../20 Domain Architecture`
- `../23 Assets`
