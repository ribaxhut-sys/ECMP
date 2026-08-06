/**
 * Mock complaint repository — WF-001-R1 Batches B1–B6 + WF-001-R2 Batch R2-B1.
 * In-memory only. No API / DB.
 *
 * B1: REGISTERED → ASSIGNED (Supervisor Assign)
 * B2: ASSIGNED → IN_PROGRESS + progress notes (Officer Handle)
 * B3: New Intake (register / hold) + Follow-up notes (no duplicate create)
 * B4: IN_PROGRESS → PENDING_REVIEW (Submit for Review)
 * B5: PENDING_REVIEW → CLOSED (Approve) or IN_PROGRESS (Reject status-only)
 * B6: SCR-Q-02 priority — escalation (display) → SLA at-risk → unassigned
 * R2B1: Reject continuity — Decision History (SCR-HX-01) + SCR-WS-06 resubmit
 * R2B2: Reopen chain — SCR-WS-03 → SCR-WS-12 (+ HX-02) → SCR-WS-07 (+ HX-01)
 * R2B3: Escalation continuity — SCR-WS-11 (+ HX-02) → optional SCR-WS-08 handover
 */

export type MockComplaintStatus =
  | "REGISTERED"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "PENDING_REVIEW"
  | "CLOSED"
  | "REOPENED";

export type MockPriority = "LOW" | "MEDIUM" | "HIGH";

export type MockCategory =
  | "Billing"
  | "Service"
  | "Product"
  | "Network"
  | "Other";

export type MockChannel =
  | "Phone"
  | "Walk-in"
  | "Email"
  | "Chat"
  | "Branch"
  | "App";

export interface MockProgressNote {
  id: string;
  text: string;
  recordedAt: string;
}

export interface MockFollowUpNote {
  id: string;
  text: string;
  recordedAt: string;
}

/** C-EVID-MIN — filename + attach status only (not formal Evidence Supporting Views). */
export type MockEvidenceStatus = "ATTACHED" | "PENDING";

export interface MockEvidenceItem {
  id: string;
  fileName: string;
  status: MockEvidenceStatus;
}

/** SCR-HX-01 — Decision History entry (Officer continuity). */
export type MockDecisionHistoryType =
  | "REJECT"
  | "SUBMIT"
  | "APPROVE"
  | "PROGRESS"
  | "REOPEN_REQUEST"
  | "REOPEN_APPROVE"
  | "REOPEN_REJECT"
  | "ESCALATION_OPEN"
  | "ESCALATION_CONTEXT_REQUEST"
  | "ESCALATION_CONTEXT_PROVIDED"
  | "ESCALATION_HANDLE"
  | "ESCALATION_FORWARD";

export interface MockDecisionHistoryEntry {
  id: string;
  type: MockDecisionHistoryType;
  at: string;
  actorId: string;
  actorName: string;
  /** Required for REJECT; optional otherwise. */
  reason?: string;
  fromStatus?: MockComplaintStatus;
  toStatus?: MockComplaintStatus;
}

export interface MockComplaint {
  id: string;
  reference: string;
  subject: string;
  description: string;
  category: MockCategory;
  customerRef: string;
  customerName: string;
  channel: MockChannel | string;
  priority: MockPriority;
  status: MockComplaintStatus;
  registeredAt: string;
  assignedUnitId: string | null;
  assignedUnitName: string | null;
  /** Mock officer user id (matches mockAuth officer). */
  assigneeOfficerId: string | null;
  /** ISO due timestamp for SLA remaining sort (SCR-Q-01). */
  slaDueAt: string | null;
  progressNotes: MockProgressNote[];
  followUpNotes: MockFollowUpNote[];
  /** Resolution text captured at submit (SCR-WS-05). */
  resolutionSummary: string | null;
  /** Minimal evidence list (C-EVID-MIN). */
  evidenceItems: MockEvidenceItem[];
  /** When submitted for review (SCR-WS-05 / B5 context). */
  submittedAt: string | null;
  /** Latest reject reason mirror (SCR-WS-10); cleared on resubmit/approve. */
  rejectReason: string | null;
  /** B6/R2-B3 — new escalation flag (SCR-Q-02 segment / SCR-WS-11). */
  escalationNew: boolean;
  /** Short reason shown in escalation segment + HX-02. */
  escalationNote: string | null;
  /** Supervisor requested officer escalation context (SCR-WS-08 entry). */
  escalationContextRequested: boolean;
  /** Officer context package for Supervisor (SCR-WS-08 → SCR-WS-11 / HX-02). */
  escalationContextPackage: string | null;
  /** SCR-HX-01 Decision History — persists across reject/resubmit. */
  decisionHistory: MockDecisionHistoryEntry[];
  /** When case was closed (SCR-HX-02 closure portion). */
  closedAt: string | null;
  /** Reopen request pending Supervisor decision (status remains CLOSED). */
  reopenPending: boolean;
  /** Reason routed from SCR-WS-03. */
  reopenReason: string | null;
  /** When reopen was requested. */
  reopenRequestedAt: string | null;
}

export interface MockCustomer {
  ref: string;
  name: string;
  phone: string;
  /** Cache/reference only — ECMP is not Customer Master SoR. */
  email: string;
}

export interface MockHeldDraft {
  id: string;
  customerRef: string;
  customerName: string;
  subject: string;
  description: string;
  category: MockCategory | "";
  channel: MockChannel | "";
  priority: MockPriority | "";
  heldAt: string;
}

export interface MockUnit {
  id: string;
  name: string;
  openWorkload: number;
}

export interface IntakeFormInput {
  customerRef: string;
  customerName: string;
  subject: string;
  description: string;
  category: MockCategory;
  channel: MockChannel;
  priority: MockPriority;
}

export const MOCK_CATEGORIES: readonly MockCategory[] = [
  "Billing",
  "Service",
  "Product",
  "Network",
  "Other",
] as const;

export const MOCK_CHANNELS: readonly MockChannel[] = [
  "Phone",
  "Walk-in",
  "Email",
  "Chat",
  "Branch",
  "App",
] as const;

export const MOCK_PRIORITIES: readonly MockPriority[] = [
  "LOW",
  "MEDIUM",
  "HIGH",
] as const;

/** Demo Complaint Officer id — aligned with `mockAuth` officer account. */
export const MOCK_OFFICER_ID = "mock-officer";

/** Demo Supervisor id — aligned with `mockAuth` supervisor account. */
export const MOCK_SUPERVISOR_ID = "mock-supervisor";
export const MOCK_SUPERVISOR_NAME = "Demo Supervisor";

export const MOCK_UNITS: readonly MockUnit[] = [
  { id: "unit-cs-north", name: "CS North Desk", openWorkload: 4 },
  { id: "unit-cs-south", name: "CS South Desk", openWorkload: 7 },
  { id: "unit-ops-billing", name: "Ops Billing", openWorkload: 2 },
  { id: "unit-ops-network", name: "Ops Network", openWorkload: 11 },
] as const;

/** Customer reference cache (read-only). Not Customer Master write. */
export const MOCK_CUSTOMERS: readonly MockCustomer[] = [
  {
    ref: "CUST-1001",
    name: "Ayu Pratama",
    phone: "+62-811-1001",
    email: "ayu.pratama@example.local",
  },
  {
    ref: "CUST-1002",
    name: "Budi Santoso",
    phone: "+62-811-1002",
    email: "budi.santoso@example.local",
  },
  {
    ref: "CUST-1003",
    name: "Citra Lestari",
    phone: "+62-811-1003",
    email: "citra.lestari@example.local",
  },
  {
    ref: "CUST-1004",
    name: "Dewi Anggraini",
    phone: "+62-811-1004",
    email: "dewi.anggraini@example.local",
  },
  {
    ref: "CUST-1005",
    name: "Eko Nugroho",
    phone: "+62-811-1005",
    email: "eko.nugroho@example.local",
  },
  {
    ref: "CUST-1006",
    name: "Farah Putri",
    phone: "+62-811-1006",
    email: "farah.putri@example.local",
  },
  {
    ref: "CUST-1007",
    name: "Gilang Saputra",
    phone: "+62-811-1007",
    email: "gilang.saputra@example.local",
  },
  {
    ref: "CUST-2099",
    name: "Hana Wijaya",
    phone: "+62-811-2099",
    email: "hana.wijaya@example.local",
  },
  {
    ref: "CUST-2100",
    name: "Indra Kusuma",
    phone: "+62-811-2100",
    email: "indra.kusuma@example.local",
  },
  {
    ref: "CUST-3001",
    name: "Joko Raharjo",
    phone: "+62-811-3001",
    email: "joko.raharjo@example.local",
  },
  {
    ref: "CUST-3002",
    name: "Kartika Sari",
    phone: "+62-811-3002",
    email: "kartika.sari@example.local",
  },
] as const;

function hoursFrom(iso: string, hours: number): string {
  return new Date(new Date(iso).getTime() + hours * 3600_000).toISOString();
}

const SEED: readonly MockComplaint[] = [
  {
    id: "cmp-b1-001",
    reference: "CMP-2026-0805-001",
    subject: "Billing discrepancy on last invoice",
    description: "Customer reports incorrect charges on the July invoice.",
    category: "Billing",
    customerRef: "CUST-1001",
    customerName: "Ayu Pratama",
    channel: "Phone",
    priority: "HIGH",
    status: "REGISTERED",
    registeredAt: "2026-08-05T01:12:00.000Z",
    assignedUnitId: null,
    assignedUnitName: null,
    assigneeOfficerId: null,
    slaDueAt: null,
    progressNotes: [],
    followUpNotes: [],
    resolutionSummary: null,
    evidenceItems: [],
    submittedAt: null,
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-b1-002",
    reference: "CMP-2026-0805-002",
    subject: "Service outage at branch counter",
    description: "Counter system unavailable during peak hours.",
    category: "Service",
    customerRef: "CUST-1002",
    customerName: "Budi Santoso",
    channel: "Walk-in",
    priority: "MEDIUM",
    status: "REGISTERED",
    registeredAt: "2026-08-05T02:40:00.000Z",
    assignedUnitId: null,
    assignedUnitName: null,
    assigneeOfficerId: null,
    slaDueAt: null,
    progressNotes: [],
    followUpNotes: [],
    resolutionSummary: null,
    evidenceItems: [],
    submittedAt: null,
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-b1-003",
    reference: "CMP-2026-0804-018",
    subject: "Wrong product activation",
    description: "Activated package does not match the order form.",
    category: "Product",
    customerRef: "CUST-1003",
    customerName: "Citra Lestari",
    channel: "Email",
    priority: "LOW",
    status: "REGISTERED",
    registeredAt: "2026-08-04T09:05:00.000Z",
    assignedUnitId: null,
    assignedUnitName: null,
    assigneeOfficerId: null,
    slaDueAt: null,
    progressNotes: [],
    followUpNotes: [],
    resolutionSummary: null,
    evidenceItems: [],
    submittedAt: null,
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-b1-004",
    reference: "CMP-2026-0803-044",
    subject: "Follow-up on refund request",
    description: "Customer asks status of an earlier refund request.",
    category: "Billing",
    customerRef: "CUST-1004",
    customerName: "Dewi Anggraini",
    channel: "Chat",
    priority: "MEDIUM",
    status: "REGISTERED",
    registeredAt: "2026-08-03T14:22:00.000Z",
    assignedUnitId: null,
    assignedUnitName: null,
    assigneeOfficerId: null,
    slaDueAt: null,
    progressNotes: [],
    followUpNotes: [],
    resolutionSummary: null,
    evidenceItems: [],
    submittedAt: null,
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-b2-001",
    reference: "CMP-2026-0802-011",
    subject: "SIM card replacement delay",
    description: "Replacement SIM not ready after three business days.",
    category: "Service",
    customerRef: "CUST-1005",
    customerName: "Eko Nugroho",
    channel: "Branch",
    priority: "HIGH",
    status: "ASSIGNED",
    registeredAt: "2026-08-02T08:00:00.000Z",
    assignedUnitId: "unit-cs-north",
    assignedUnitName: "CS North Desk",
    assigneeOfficerId: MOCK_OFFICER_ID,
    slaDueAt: hoursFrom("2026-08-05T03:00:00.000Z", 6),
    progressNotes: [],
    followUpNotes: [],
    resolutionSummary: null,
    evidenceItems: [],
    submittedAt: null,
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-b2-002",
    reference: "CMP-2026-0801-027",
    subject: "Incorrect package migration",
    description: "Migration applied wrong tier; customer requests correction.",
    category: "Product",
    customerRef: "CUST-1006",
    customerName: "Farah Putri",
    channel: "App",
    priority: "MEDIUM",
    status: "ASSIGNED",
    registeredAt: "2026-08-01T11:30:00.000Z",
    assignedUnitId: "unit-ops-billing",
    assignedUnitName: "Ops Billing",
    assigneeOfficerId: MOCK_OFFICER_ID,
    slaDueAt: hoursFrom("2026-08-05T03:00:00.000Z", 18),
    progressNotes: [],
    followUpNotes: [],
    resolutionSummary: null,
    evidenceItems: [],
    submittedAt: null,
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-b2-003",
    reference: "CMP-2026-0731-009",
    subject: "Slow network at customer site",
    description: "Intermittent drops reported after 18:00 local time.",
    category: "Network",
    customerRef: "CUST-1007",
    customerName: "Gilang Saputra",
    channel: "Phone",
    priority: "LOW",
    status: "IN_PROGRESS",
    registeredAt: "2026-07-31T07:15:00.000Z",
    assignedUnitId: "unit-ops-network",
    assignedUnitName: "Ops Network",
    assigneeOfficerId: MOCK_OFFICER_ID,
    slaDueAt: hoursFrom("2026-08-05T03:00:00.000Z", 30),
    progressNotes: [
      {
        id: "note-seed-1",
        text: "Customer confirmed intermittent drops after 18:00.",
        recordedAt: "2026-08-04T10:00:00.000Z",
      },
    ],
    followUpNotes: [
      {
        id: "fu-seed-1",
        text: "Customer called for status update on network ticket.",
        recordedAt: "2026-08-03T09:30:00.000Z",
      },
    ],
    resolutionSummary: null,
    evidenceItems: [
      {
        id: "evid-seed-1",
        fileName: "speedtest-2026-08-04.pdf",
        status: "ATTACHED",
      },
    ],
    submittedAt: null,
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-b5-001",
    reference: "CMP-2026-0805-101",
    subject: "Package downgrade not reflected",
    description: "Customer still billed at previous tier after approved downgrade.",
    category: "Billing",
    customerRef: "CUST-2100",
    customerName: "Indra Kusuma",
    channel: "App",
    priority: "HIGH",
    status: "PENDING_REVIEW",
    registeredAt: "2026-08-04T06:00:00.000Z",
    assignedUnitId: "unit-ops-billing",
    assignedUnitName: "Ops Billing",
    assigneeOfficerId: MOCK_OFFICER_ID,
    slaDueAt: hoursFrom("2026-08-05T03:00:00.000Z", 12),
    progressNotes: [
      {
        id: "note-b5-1",
        text: "Billing adjustment prepared; awaiting Supervisor close.",
        recordedAt: "2026-08-05T01:00:00.000Z",
      },
    ],
    followUpNotes: [],
    resolutionSummary:
      "Applied corrective credit and confirmed next invoice shows the downgraded package.",
    evidenceItems: [
      {
        id: "evid-b5-1",
        fileName: "billing-adjustment-note.pdf",
        status: "ATTACHED",
      },
    ],
    submittedAt: "2026-08-05T02:15:00.000Z",
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [
      {
        id: "hist-b5-submit-1",
        type: "SUBMIT",
        at: "2026-08-05T02:15:00.000Z",
        actorId: MOCK_OFFICER_ID,
        actorName: "Demo Officer",
        fromStatus: "IN_PROGRESS",
        toStatus: "PENDING_REVIEW",
      },
    ],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-b6-esc-001",
    reference: "CMP-2026-0805-201",
    subject: "Escalated billing dispute after failed resolve",
    description: "Customer demanded Supervisor escalation after repeated billing errors.",
    category: "Billing",
    customerRef: "CUST-2100",
    customerName: "Indra Kusuma",
    channel: "Phone",
    priority: "HIGH",
    status: "IN_PROGRESS",
    registeredAt: "2026-08-03T08:00:00.000Z",
    assignedUnitId: "unit-ops-billing",
    assignedUnitName: "Ops Billing",
    assigneeOfficerId: MOCK_OFFICER_ID,
    slaDueAt: hoursFrom("2026-08-05T03:00:00.000Z", 4),
    progressNotes: [
      {
        id: "note-b6-esc-1",
        text: "Officer prepared context; awaiting Supervisor escalation path (R2).",
        recordedAt: "2026-08-05T01:30:00.000Z",
      },
    ],
    followUpNotes: [],
    resolutionSummary: null,
    evidenceItems: [
      {
        id: "evid-b6-esc-1",
        fileName: "dispute-timeline.pdf",
        status: "ATTACHED",
      },
    ],
    submittedAt: null,
    rejectReason: null,
    escalationNew: true,
    escalationNote: "New escalation — customer requested Supervisor handover",
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [
      {
        id: "hist-b6-esc-open-1",
        type: "ESCALATION_OPEN",
        at: "2026-08-05T01:00:00.000Z",
        actorId: MOCK_OFFICER_ID,
        actorName: "Demo Officer",
        reason: "New escalation — customer requested Supervisor handover",
        fromStatus: "IN_PROGRESS",
        toStatus: "IN_PROGRESS",
      },
    ],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-r2b3-ctx-001",
    reference: "CMP-2026-0805-401",
    subject: "SLA breach escalation awaiting officer context",
    description: "Supervisor requested structured context before Handle/Forward.",
    category: "Service",
    customerRef: "CUST-2100",
    customerName: "Indra Kusuma",
    channel: "Chat",
    priority: "HIGH",
    status: "IN_PROGRESS",
    registeredAt: "2026-08-04T10:00:00.000Z",
    assignedUnitId: "unit-ops-billing",
    assignedUnitName: "Ops Billing",
    assigneeOfficerId: MOCK_OFFICER_ID,
    slaDueAt: hoursFrom("2026-08-05T03:00:00.000Z", 3),
    progressNotes: [
      {
        id: "note-r2b3-ctx-1",
        text: "Checked billing ledger; partial refund already offered.",
        recordedAt: "2026-08-05T00:45:00.000Z",
      },
    ],
    followUpNotes: [],
    resolutionSummary: null,
    evidenceItems: [],
    submittedAt: null,
    rejectReason: null,
    escalationNew: true,
    escalationNote: "Customer insists on Head Office review of refund refusal",
    escalationContextRequested: true,
    escalationContextPackage: null,
    decisionHistory: [
      {
        id: "hist-r2b3-esc-open-1",
        type: "ESCALATION_OPEN",
        at: "2026-08-05T01:10:00.000Z",
        actorId: MOCK_OFFICER_ID,
        actorName: "Demo Officer",
        reason: "Customer insists on Head Office review of refund refusal",
        fromStatus: "IN_PROGRESS",
        toStatus: "IN_PROGRESS",
      },
      {
        id: "hist-r2b3-esc-ctx-req-1",
        type: "ESCALATION_CONTEXT_REQUEST",
        at: "2026-08-05T01:40:00.000Z",
        actorId: MOCK_SUPERVISOR_ID,
        actorName: MOCK_SUPERVISOR_NAME,
        reason: "Need officer context package before Handle/Forward",
        fromStatus: "IN_PROGRESS",
        toStatus: "IN_PROGRESS",
      },
    ],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-b6-sla-001",
    reference: "CMP-2026-0805-202",
    subject: "Branch counter outage nearing SLA",
    description: "Assigned outage case with SLA approaching breach.",
    category: "Service",
    customerRef: "CUST-1002",
    customerName: "Budi Santoso",
    channel: "Walk-in",
    priority: "HIGH",
    status: "ASSIGNED",
    registeredAt: "2026-08-05T00:30:00.000Z",
    assignedUnitId: "unit-cs-south",
    assignedUnitName: "CS South Desk",
    assigneeOfficerId: MOCK_OFFICER_ID,
    slaDueAt: hoursFrom("2026-08-05T03:00:00.000Z", 2),
    progressNotes: [],
    followUpNotes: [],
    resolutionSummary: null,
    evidenceItems: [],
    submittedAt: null,
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-r2b1-001",
    reference: "CMP-2026-0805-301",
    subject: "Incorrect fee after service restore",
    description: "Fee still charged after service was restored; prior submission rejected.",
    category: "Billing",
    customerRef: "CUST-1001",
    customerName: "Ayu Pratama",
    channel: "Phone",
    priority: "HIGH",
    status: "IN_PROGRESS",
    registeredAt: "2026-08-04T05:00:00.000Z",
    assignedUnitId: "unit-ops-billing",
    assignedUnitName: "Ops Billing",
    assigneeOfficerId: MOCK_OFFICER_ID,
    slaDueAt: hoursFrom("2026-08-05T03:00:00.000Z", 8),
    progressNotes: [
      {
        id: "note-r2b1-1",
        text: "Prepared fee reversal; submitted for review.",
        recordedAt: "2026-08-05T00:30:00.000Z",
      },
    ],
    followUpNotes: [],
    resolutionSummary:
      "Fee reversal prepared on billing worksheet; awaiting corrected evidence.",
    evidenceItems: [
      {
        id: "evid-r2b1-1",
        fileName: "fee-reversal-draft.pdf",
        status: "ATTACHED",
      },
    ],
    submittedAt: "2026-08-05T01:00:00.000Z",
    rejectReason: "Need clearer proof that the fee was reversed on the live invoice.",
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [
      {
        id: "hist-r2b1-submit-1",
        type: "SUBMIT",
        at: "2026-08-05T01:00:00.000Z",
        actorId: MOCK_OFFICER_ID,
        actorName: "Demo Officer",
        fromStatus: "IN_PROGRESS",
        toStatus: "PENDING_REVIEW",
      },
      {
        id: "hist-r2b1-reject-1",
        type: "REJECT",
        at: "2026-08-05T02:00:00.000Z",
        actorId: MOCK_SUPERVISOR_ID,
        actorName: MOCK_SUPERVISOR_NAME,
        reason:
          "Need clearer proof that the fee was reversed on the live invoice.",
        fromStatus: "PENDING_REVIEW",
        toStatus: "IN_PROGRESS",
      },
    ],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-r2b2-closed-001",
    reference: "CMP-2026-0803-501",
    subject: "Closed billing dispute — reopen candidate",
    description: "Customer disputes residual charge after prior closure.",
    category: "Billing",
    customerRef: "CUST-3001",
    customerName: "Joko Raharjo",
    channel: "Email",
    priority: "MEDIUM",
    status: "CLOSED",
    registeredAt: "2026-08-01T08:00:00.000Z",
    assignedUnitId: "unit-ops-billing",
    assignedUnitName: "Ops Billing",
    assigneeOfficerId: MOCK_OFFICER_ID,
    slaDueAt: null,
    progressNotes: [
      {
        id: "note-r2b2-c1",
        text: "Credit applied; customer accepted at time of closure.",
        recordedAt: "2026-08-02T10:00:00.000Z",
      },
    ],
    followUpNotes: [],
    resolutionSummary: "Credit applied and confirmed with customer before close.",
    evidenceItems: [
      {
        id: "evid-r2b2-c1",
        fileName: "closure-credit-note.pdf",
        status: "ATTACHED",
      },
    ],
    submittedAt: "2026-08-02T11:00:00.000Z",
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [
      {
        id: "hist-r2b2-c1-submit",
        type: "SUBMIT",
        at: "2026-08-02T11:00:00.000Z",
        actorId: MOCK_OFFICER_ID,
        actorName: "Demo Officer",
        fromStatus: "IN_PROGRESS",
        toStatus: "PENDING_REVIEW",
      },
      {
        id: "hist-r2b2-c1-approve",
        type: "APPROVE",
        at: "2026-08-02T12:00:00.000Z",
        actorId: MOCK_SUPERVISOR_ID,
        actorName: MOCK_SUPERVISOR_NAME,
        fromStatus: "PENDING_REVIEW",
        toStatus: "CLOSED",
      },
    ],
    closedAt: "2026-08-02T12:00:00.000Z",
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  },
  {
    id: "cmp-r2b2-pending-001",
    reference: "CMP-2026-0802-502",
    subject: "Closed service ticket awaiting reopen decision",
    description: "Customer reports issue returned after prior service restore.",
    category: "Service",
    customerRef: "CUST-3002",
    customerName: "Kartika Sari",
    channel: "Chat",
    priority: "HIGH",
    status: "CLOSED",
    registeredAt: "2026-07-30T09:00:00.000Z",
    assignedUnitId: "unit-cs-south",
    assignedUnitName: "CS South Desk",
    assigneeOfficerId: MOCK_OFFICER_ID,
    slaDueAt: null,
    progressNotes: [
      {
        id: "note-r2b2-p1",
        text: "Service restored; monitored for 24h before close.",
        recordedAt: "2026-08-01T08:00:00.000Z",
      },
    ],
    followUpNotes: [],
    resolutionSummary: "Outage cleared; customer confirmed service restored.",
    evidenceItems: [
      {
        id: "evid-r2b2-p1",
        fileName: "restore-confirmation.pdf",
        status: "ATTACHED",
      },
    ],
    submittedAt: "2026-08-01T09:00:00.000Z",
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [
      {
        id: "hist-r2b2-p1-approve",
        type: "APPROVE",
        at: "2026-08-01T10:00:00.000Z",
        actorId: MOCK_SUPERVISOR_ID,
        actorName: MOCK_SUPERVISOR_NAME,
        fromStatus: "PENDING_REVIEW",
        toStatus: "CLOSED",
      },
      {
        id: "hist-r2b2-p1-req",
        type: "REOPEN_REQUEST",
        at: "2026-08-05T01:30:00.000Z",
        actorId: MOCK_OFFICER_ID,
        actorName: "Demo Officer",
        reason: "Customer reports the same outage symptoms returned overnight.",
        fromStatus: "CLOSED",
        toStatus: "CLOSED",
      },
    ],
    closedAt: "2026-08-01T10:00:00.000Z",
    reopenPending: true,
    reopenReason: "Customer reports the same outage symptoms returned overnight.",
    reopenRequestedAt: "2026-08-05T01:30:00.000Z",
  },
  {
    id: "cmp-r2b2-reopened-001",
    reference: "CMP-2026-0801-503",
    subject: "Reopened product activation case",
    description: "Wrong tier activation previously closed; reopen approved for continuation.",
    category: "Product",
    customerRef: "CUST-2099",
    customerName: "Hana Wijaya",
    channel: "App",
    priority: "MEDIUM",
    status: "REOPENED",
    registeredAt: "2026-07-28T07:00:00.000Z",
    assignedUnitId: "unit-ops-billing",
    assignedUnitName: "Ops Billing",
    assigneeOfficerId: MOCK_OFFICER_ID,
    slaDueAt: hoursFrom("2026-08-05T03:00:00.000Z", 10),
    progressNotes: [
      {
        id: "note-r2b2-r1",
        text: "Original handling: mapped activation form vs applied tier.",
        recordedAt: "2026-07-29T12:00:00.000Z",
      },
    ],
    followUpNotes: [],
    resolutionSummary: "Tier corrected at first closure; customer later reported mismatch again.",
    evidenceItems: [
      {
        id: "evid-r2b2-r1",
        fileName: "activation-form.pdf",
        status: "ATTACHED",
      },
    ],
    submittedAt: "2026-07-29T14:00:00.000Z",
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [
      {
        id: "hist-r2b2-r1-approve",
        type: "APPROVE",
        at: "2026-07-29T15:00:00.000Z",
        actorId: MOCK_SUPERVISOR_ID,
        actorName: MOCK_SUPERVISOR_NAME,
        fromStatus: "PENDING_REVIEW",
        toStatus: "CLOSED",
      },
      {
        id: "hist-r2b2-r1-req",
        type: "REOPEN_REQUEST",
        at: "2026-08-04T08:00:00.000Z",
        actorId: MOCK_OFFICER_ID,
        actorName: "Demo Officer",
        reason: "Customer still sees wrong tier after prior closure.",
        fromStatus: "CLOSED",
        toStatus: "CLOSED",
      },
      {
        id: "hist-r2b2-r1-ok",
        type: "REOPEN_APPROVE",
        at: "2026-08-04T09:00:00.000Z",
        actorId: MOCK_SUPERVISOR_ID,
        actorName: MOCK_SUPERVISOR_NAME,
        fromStatus: "CLOSED",
        toStatus: "REOPENED",
      },
    ],
    closedAt: "2026-07-29T15:00:00.000Z",
    reopenPending: false,
    reopenReason: "Customer still sees wrong tier after prior closure.",
    reopenRequestedAt: "2026-08-04T08:00:00.000Z",
  },
];

type Listener = () => void;

let complaints: MockComplaint[] = SEED.map(cloneComplaint);
let heldDrafts: MockHeldDraft[] = [];
let registerSeq = 100;
const listeners = new Set<Listener>();

function emit(): void {
  for (const listener of listeners) listener();
}

function cloneComplaint(c: MockComplaint): MockComplaint {
  return {
    ...c,
    progressNotes: c.progressNotes.map((n) => ({ ...n })),
    followUpNotes: c.followUpNotes.map((n) => ({ ...n })),
    evidenceItems: c.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: (c.decisionHistory ?? []).map((e) => ({ ...e })),
  };
}

function cloneHeldDraft(d: MockHeldDraft): MockHeldDraft {
  return { ...d };
}

export function subscribeAssignmentRepo(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function getAssignmentSnapshot(): readonly MockComplaint[] {
  return complaints;
}

export function getHeldDraftsSnapshot(): readonly MockHeldDraft[] {
  return heldDrafts;
}

export function listUnassigned(): MockComplaint[] {
  return complaints
    .filter((c) => c.status === "REGISTERED")
    .slice()
    .sort(
      (a, b) =>
        new Date(a.registeredAt).getTime() - new Date(b.registeredAt).getTime(),
    );
}

/** SCR-Q-02 — pending approval segment (PENDING_REVIEW). */
export function listPendingReview(): MockComplaint[] {
  return complaints
    .filter((c) => c.status === "PENDING_REVIEW" && !c.escalationNew)
    .slice()
    .sort((a, b) => {
      const aAt = a.submittedAt ?? a.registeredAt;
      const bAt = b.submittedAt ?? b.registeredAt;
      return new Date(aAt).getTime() - new Date(bAt).getTime();
    })
    .map(cloneComplaint);
}

/** B6 — new escalation segment (display only; action stub → R2). */
export function listNewEscalations(): MockComplaint[] {
  return complaints
    .filter((c) => c.escalationNew && c.status !== "CLOSED")
    .slice()
    .sort(
      (a, b) =>
        new Date(b.registeredAt).getTime() - new Date(a.registeredAt).getTime(),
    )
    .map(cloneComplaint);
}

/** SLA at-risk threshold — matches Officer handling near-SLA warning (8h). */
export const SLA_AT_RISK_MS = 8 * 3600_000;

/**
 * B6 — SLA at-risk / overdue segment.
 * Excludes escalation items, unassigned (REGISTERED), pending review, and CLOSED.
 */
export function listSlaAtRisk(nowMs: number = Date.now()): MockComplaint[] {
  return complaints
    .filter((c) => {
      if (c.escalationNew) return false;
      if (c.status === "REGISTERED" || c.status === "CLOSED") return false;
      if (c.status === "PENDING_REVIEW") return false;
      if (!c.slaDueAt) return false;
      const remaining = new Date(c.slaDueAt).getTime() - nowMs;
      return remaining < SLA_AT_RISK_MS;
    })
    .slice()
    .sort((a, b) => {
      const aDue = a.slaDueAt ? new Date(a.slaDueAt).getTime() : Number.MAX_SAFE_INTEGER;
      const bDue = b.slaDueAt ? new Date(b.slaDueAt).getTime() : Number.MAX_SAFE_INTEGER;
      return aDue - bDue;
    })
    .map(cloneComplaint);
}

/** SCR-Q-01 — assignee queue: ASSIGNED + IN_PROGRESS + REOPENED, sorted by SLA remaining. */
export function listOfficerAssigned(
  officerId: string = MOCK_OFFICER_ID,
): MockComplaint[] {
  return complaints
    .filter(
      (c) =>
        c.assigneeOfficerId === officerId &&
        (c.status === "ASSIGNED" ||
          c.status === "IN_PROGRESS" ||
          c.status === "REOPENED"),
    )
    .slice()
    .sort((a, b) => {
      const aDue = a.slaDueAt ? new Date(a.slaDueAt).getTime() : Number.MAX_SAFE_INTEGER;
      const bDue = b.slaDueAt ? new Date(b.slaDueAt).getTime() : Number.MAX_SAFE_INTEGER;
      return aDue - bDue;
    });
}

export function getComplaintById(id: string): MockComplaint | undefined {
  const found = complaints.find((c) => c.id === id);
  return found ? cloneComplaint(found) : undefined;
}

export function getUnitById(id: string): MockUnit | undefined {
  return MOCK_UNITS.find((u) => u.id === id);
}

export function getCustomerByRef(ref: string): MockCustomer | undefined {
  return MOCK_CUSTOMERS.find((c) => c.ref === ref);
}

/** Customer reference lookup (cache/reference only — no master write). */
export function searchCustomers(query: string): MockCustomer[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  return MOCK_CUSTOMERS.filter(
    (c) =>
      c.ref.toLowerCase().includes(q) ||
      c.name.toLowerCase().includes(q) ||
      c.phone.toLowerCase().includes(q) ||
      c.email.toLowerCase().includes(q),
  ).map((c) => ({ ...c }));
}

/**
 * Active cases for a customer reference (SCR-WS-01 → SCR-WS-02 routing).
 * Excludes CLOSED (and reopen-pending CLOSED) — those route to SCR-WS-03.
 */
export function listActiveCasesByCustomerRef(
  customerRef: string,
): MockComplaint[] {
  const ref = customerRef.trim();
  if (!ref) return [];
  return complaints
    .filter(
      (c) =>
        c.customerRef === ref &&
        c.status !== "CLOSED",
    )
    .slice()
    .sort(
      (a, b) =>
        new Date(b.registeredAt).getTime() - new Date(a.registeredAt).getTime(),
    )
    .map(cloneComplaint);
}

/**
 * Closed cases for a customer (SCR-WS-01 → SCR-WS-03 reopen routing).
 * Prefer cases without an active reopen pending when selecting a target.
 */
export function listClosedCasesByCustomerRef(
  customerRef: string,
): MockComplaint[] {
  const ref = customerRef.trim();
  if (!ref) return [];
  return complaints
    .filter((c) => c.customerRef === ref && c.status === "CLOSED")
    .slice()
    .sort((a, b) => {
      const aAt = a.closedAt ?? a.registeredAt;
      const bAt = b.closedAt ?? b.registeredAt;
      return new Date(bAt).getTime() - new Date(aAt).getTime();
    })
    .map(cloneComplaint);
}

/** SCR-Q-02 — pending reopen approval (CLOSED + reopenPending). */
export function listPendingReopen(): MockComplaint[] {
  return complaints
    .filter((c) => c.status === "CLOSED" && c.reopenPending)
    .slice()
    .sort((a, b) => {
      const aAt = a.reopenRequestedAt ?? a.closedAt ?? a.registeredAt;
      const bAt = b.reopenRequestedAt ?? b.closedAt ?? b.registeredAt;
      return new Date(aAt).getTime() - new Date(bAt).getTime();
    })
    .map(cloneComplaint);
}

export function listHeldDrafts(): MockHeldDraft[] {
  return heldDrafts
    .slice()
    .sort(
      (a, b) => new Date(b.heldAt).getTime() - new Date(a.heldAt).getTime(),
    )
    .map(cloneHeldDraft);
}

export function slaRemainingMs(
  complaint: MockComplaint,
  nowMs: number = Date.now(),
): number | null {
  if (!complaint.slaDueAt) return null;
  return new Date(complaint.slaDueAt).getTime() - nowMs;
}

export interface AssignResult {
  ok: true;
  complaint: MockComplaint;
}

export interface AssignError {
  ok: false;
  reason: "NOT_FOUND" | "NOT_REGISTERED" | "UNIT_NOT_FOUND";
}

/**
 * B1 — Assign complaint to a unit: REGISTERED → ASSIGNED.
 * Also binds the demo officer so B2 Officer Queue can consume the item.
 */
export function assignComplaintToUnit(
  complaintId: string,
  unitId: string,
  officerId: string = MOCK_OFFICER_ID,
): AssignResult | AssignError {
  const unit = getUnitById(unitId);
  if (!unit) return { ok: false, reason: "UNIT_NOT_FOUND" };

  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.status !== "REGISTERED") {
    return { ok: false, reason: "NOT_REGISTERED" };
  }

  const nowIso = new Date().toISOString();
  const updated: MockComplaint = {
    ...current,
    status: "ASSIGNED",
    assignedUnitId: unit.id,
    assignedUnitName: unit.name,
    assigneeOfficerId: officerId,
    slaDueAt: hoursFrom(nowIso, 24),
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: [...current.evidenceItems],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type StartHandlingErrorReason =
  | "NOT_FOUND"
  | "NOT_ASSIGNED"
  | "NOT_ASSIGNEE";

export interface StartHandlingResult {
  ok: true;
  complaint: MockComplaint;
}

export interface StartHandlingError {
  ok: false;
  reason: StartHandlingErrorReason;
}

/** B2 — Start handling: ASSIGNED → IN_PROGRESS. */
export function startHandling(
  complaintId: string,
  officerId: string = MOCK_OFFICER_ID,
): StartHandlingResult | StartHandlingError {
  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.assigneeOfficerId !== officerId) {
    return { ok: false, reason: "NOT_ASSIGNEE" };
  }
  if (current.status !== "ASSIGNED") {
    return { ok: false, reason: "NOT_ASSIGNED" };
  }

  const updated: MockComplaint = {
    ...current,
    status: "IN_PROGRESS",
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: [...current.evidenceItems],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type RecordProgressErrorReason =
  | "NOT_FOUND"
  | "NOT_IN_PROGRESS"
  | "NOT_ASSIGNEE"
  | "EMPTY_NOTE";

export interface RecordProgressResult {
  ok: true;
  complaint: MockComplaint;
}

export interface RecordProgressError {
  ok: false;
  reason: RecordProgressErrorReason;
}

/** B2 / R2-B2 — Record progress note while IN_PROGRESS or REOPENED. */
export function recordProgress(
  complaintId: string,
  text: string,
  officerId: string = MOCK_OFFICER_ID,
): RecordProgressResult | RecordProgressError {
  const trimmed = text.trim();
  if (!trimmed) return { ok: false, reason: "EMPTY_NOTE" };

  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.assigneeOfficerId !== officerId) {
    return { ok: false, reason: "NOT_ASSIGNEE" };
  }
  if (current.status !== "IN_PROGRESS" && current.status !== "REOPENED") {
    return { ok: false, reason: "NOT_IN_PROGRESS" };
  }

  const note: MockProgressNote = {
    id: `note-${Date.now()}`,
    text: trimmed,
    recordedAt: new Date().toISOString(),
  };
  const updated: MockComplaint = {
    ...current,
    status: "IN_PROGRESS",
    progressNotes: [...current.progressNotes, note],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: [...current.evidenceItems],
    decisionHistory: (current.decisionHistory ?? []).map((e) => ({ ...e })),
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type RegisterIntakeErrorReason =
  | "INCOMPLETE"
  | "ACTIVE_CASE_EXISTS"
  | "CUSTOMER_REQUIRED";

export interface RegisterIntakeResult {
  ok: true;
  complaint: MockComplaint;
}

export interface RegisterIntakeError {
  ok: false;
  reason: RegisterIntakeErrorReason;
}

function isIntakeComplete(input: IntakeFormInput): boolean {
  return Boolean(
    input.customerRef.trim() &&
      input.customerName.trim() &&
      input.subject.trim() &&
      input.description.trim() &&
      input.category &&
      input.channel &&
      input.priority,
  );
}

/**
 * B3 — Forward / Register when complete → REGISTERED.
 * Blocks when the customer already has an active case (use Follow-up).
 */
export function registerIntake(
  input: IntakeFormInput,
): RegisterIntakeResult | RegisterIntakeError {
  if (!input.customerRef.trim() || !input.customerName.trim()) {
    return { ok: false, reason: "CUSTOMER_REQUIRED" };
  }
  if (!isIntakeComplete(input)) {
    return { ok: false, reason: "INCOMPLETE" };
  }
  if (listActiveCasesByCustomerRef(input.customerRef).length > 0) {
    return { ok: false, reason: "ACTIVE_CASE_EXISTS" };
  }

  registerSeq += 1;
  const nowIso = new Date().toISOString();
  const day = nowIso.slice(0, 10).replaceAll("-", "");
  const created: MockComplaint = {
    id: `cmp-b3-${registerSeq}`,
    reference: `CMP-${day}-${String(registerSeq).padStart(3, "0")}`,
    subject: input.subject.trim(),
    description: input.description.trim(),
    category: input.category,
    customerRef: input.customerRef.trim(),
    customerName: input.customerName.trim(),
    channel: input.channel,
    priority: input.priority,
    status: "REGISTERED",
    registeredAt: nowIso,
    assignedUnitId: null,
    assignedUnitName: null,
    assigneeOfficerId: null,
    slaDueAt: null,
    progressNotes: [],
    followUpNotes: [],
    resolutionSummary: null,
    evidenceItems: [],
    submittedAt: null,
    rejectReason: null,
    escalationNew: false,
    escalationNote: null,
    escalationContextRequested: false,
    escalationContextPackage: null,
    decisionHistory: [],
    closedAt: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
  };
  complaints = [...complaints, created];
  emit();
  return { ok: true, complaint: cloneComplaint(created) };
}

export type HoldIntakeErrorReason = "EMPTY" | "CUSTOMER_REQUIRED";

export interface HoldIntakeResult {
  ok: true;
  draft: MockHeldDraft;
}

export interface HoldIntakeError {
  ok: false;
  reason: HoldIntakeErrorReason;
}

/**
 * B3 — Hold to complete: store incomplete draft in mock repo (no REGISTERED row).
 * Does not create a complaint primary record.
 */
export function holdIntakeDraft(input: {
  customerRef: string;
  customerName: string;
  subject: string;
  description: string;
  category: MockCategory | "";
  channel: MockChannel | "";
  priority: MockPriority | "";
}): HoldIntakeResult | HoldIntakeError {
  const hasContent = Boolean(
    input.subject.trim() ||
      input.description.trim() ||
      input.category ||
      input.channel ||
      input.priority,
  );
  if (!input.customerRef.trim() || !input.customerName.trim()) {
    return { ok: false, reason: "CUSTOMER_REQUIRED" };
  }
  if (!hasContent) {
    return { ok: false, reason: "EMPTY" };
  }

  const draft: MockHeldDraft = {
    id: `hold-${Date.now()}`,
    customerRef: input.customerRef.trim(),
    customerName: input.customerName.trim(),
    subject: input.subject.trim(),
    description: input.description.trim(),
    category: input.category,
    channel: input.channel,
    priority: input.priority,
    heldAt: new Date().toISOString(),
  };
  heldDrafts = [...heldDrafts, draft];
  emit();
  return { ok: true, draft: cloneHeldDraft(draft) };
}

export function consumeHeldDraft(draftId: string): MockHeldDraft | undefined {
  const index = heldDrafts.findIndex((d) => d.id === draftId);
  if (index < 0) return undefined;
  const draft = cloneHeldDraft(heldDrafts[index]!);
  heldDrafts = [
    ...heldDrafts.slice(0, index),
    ...heldDrafts.slice(index + 1),
  ];
  emit();
  return draft;
}

export type SaveFollowUpErrorReason =
  | "NOT_FOUND"
  | "NOT_ACTIVE"
  | "EMPTY_NOTE";

export interface SaveFollowUpResult {
  ok: true;
  complaint: MockComplaint;
}

export interface SaveFollowUpError {
  ok: false;
  reason: SaveFollowUpErrorReason;
}

/**
 * B3 — Save follow-up note on an existing active case.
 * Does not create a new complaint / primary record. Status unchanged.
 */
export function saveFollowUp(
  complaintId: string,
  text: string,
): SaveFollowUpResult | SaveFollowUpError {
  const trimmed = text.trim();
  if (!trimmed) return { ok: false, reason: "EMPTY_NOTE" };

  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  // Active lifecycle rows (not CLOSED — CLOSED arrives in B5).
  if (
    current.status !== "REGISTERED" &&
    current.status !== "ASSIGNED" &&
    current.status !== "IN_PROGRESS" &&
    current.status !== "PENDING_REVIEW"
  ) {
    return { ok: false, reason: "NOT_ACTIVE" };
  }

  const note: MockFollowUpNote = {
    id: `fu-${Date.now()}`,
    text: trimmed,
    recordedAt: new Date().toISOString(),
  };
  const updated: MockComplaint = {
    ...current,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes, note],
    evidenceItems: [...current.evidenceItems],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

/** SCR-WS-05 checklist — resolution + attached evidence (C-EVID-MIN). */
export function submitCompleteness(input: {
  resolutionSummary: string;
  evidenceItems: readonly MockEvidenceItem[];
}): { key: string; filled: boolean }[] {
  const hasAttached = input.evidenceItems.some((e) => e.status === "ATTACHED");
  return [
    { key: "resolution", filled: Boolean(input.resolutionSummary.trim()) },
    { key: "evidence", filled: hasAttached },
  ];
}

export type SubmitForReviewErrorReason =
  | "NOT_FOUND"
  | "NOT_IN_PROGRESS"
  | "NOT_ASSIGNEE"
  | "RESOLUTION_REQUIRED"
  | "EVIDENCE_REQUIRED"
  | "HISTORY_REQUIRED";

export interface SubmitForReviewResult {
  ok: true;
  complaint: MockComplaint;
}

export interface SubmitForReviewError {
  ok: false;
  reason: SubmitForReviewErrorReason;
}

/**
 * B4 / R2-B1 — Submit for review: IN_PROGRESS → PENDING_REVIEW.
 * Requires resolution summary and at least one ATTACHED evidence item (C-EVID-MIN).
 * Preserves Decision History; clears active rejectReason mirror; appends SUBMIT entry.
 */
export function submitForReview(
  complaintId: string,
  resolutionSummary: string,
  officerId: string = MOCK_OFFICER_ID,
): SubmitForReviewResult | SubmitForReviewError {
  const trimmed = resolutionSummary.trim();
  if (!trimmed) return { ok: false, reason: "RESOLUTION_REQUIRED" };

  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.assigneeOfficerId !== officerId) {
    return { ok: false, reason: "NOT_ASSIGNEE" };
  }
  if (current.status !== "IN_PROGRESS" && current.status !== "REOPENED") {
    return { ok: false, reason: "NOT_IN_PROGRESS" };
  }
  if (!current.evidenceItems.some((e) => e.status === "ATTACHED")) {
    return { ok: false, reason: "EVIDENCE_REQUIRED" };
  }
  // Continuity gate (SCR-WS-06): rejected cases must carry REJECT Decision History.
  if (
    Boolean(current.rejectReason?.trim()) &&
    !(current.decisionHistory ?? []).some((e) => e.type === "REJECT")
  ) {
    return { ok: false, reason: "HISTORY_REQUIRED" };
  }
  if (
    (current.decisionHistory ?? []).some((e) => e.type === "REJECT") &&
    !(current.decisionHistory ?? []).some((e) => e.type === "REJECT" && e.reason?.trim())
  ) {
    return { ok: false, reason: "HISTORY_REQUIRED" };
  }
  // Continuity gate (SCR-WS-07): reopened cases must carry prior closure / reopen history.
  if (
    current.status === "REOPENED" &&
    !(current.decisionHistory ?? []).some(
      (e) => e.type === "APPROVE" || e.type === "REOPEN_APPROVE",
    )
  ) {
    return { ok: false, reason: "HISTORY_REQUIRED" };
  }

  const nowIso = new Date().toISOString();
  const historyEntry: MockDecisionHistoryEntry = {
    id: `hist-submit-${Date.now()}`,
    type: "SUBMIT",
    at: nowIso,
    actorId: officerId,
    actorName: "Demo Officer",
    fromStatus: current.status,
    toStatus: "PENDING_REVIEW",
  };

  const updated: MockComplaint = {
    ...current,
    status: "PENDING_REVIEW",
    resolutionSummary: trimmed,
    submittedAt: nowIso,
    rejectReason: null,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: [...(current.decisionHistory ?? []), historyEntry],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type AddEvidenceErrorReason =
  | "NOT_FOUND"
  | "NOT_IN_PROGRESS"
  | "NOT_ASSIGNEE"
  | "EMPTY_NAME";

export interface AddEvidenceResult {
  ok: true;
  complaint: MockComplaint;
}

export interface AddEvidenceError {
  ok: false;
  reason: AddEvidenceErrorReason;
}

/** B4 — Add a minimal evidence row (filename only; no upload / formal Evidence Views). */
export function addMinimalEvidence(
  complaintId: string,
  fileName: string,
  officerId: string = MOCK_OFFICER_ID,
): AddEvidenceResult | AddEvidenceError {
  const name = fileName.trim();
  if (!name) return { ok: false, reason: "EMPTY_NAME" };

  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.assigneeOfficerId !== officerId) {
    return { ok: false, reason: "NOT_ASSIGNEE" };
  }
  if (current.status !== "IN_PROGRESS" && current.status !== "REOPENED") {
    return { ok: false, reason: "NOT_IN_PROGRESS" };
  }

  const item: MockEvidenceItem = {
    id: `evid-${Date.now()}`,
    fileName: name,
    status: "ATTACHED",
  };
  const updated: MockComplaint = {
    ...current,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: [...current.evidenceItems, item],
    decisionHistory: (current.decisionHistory ?? []).map((e) => ({ ...e })),
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type ApproveCloseErrorReason = "NOT_FOUND" | "NOT_PENDING_REVIEW";

export interface ApproveCloseResult {
  ok: true;
  complaint: MockComplaint;
}

export interface ApproveCloseError {
  ok: false;
  reason: ApproveCloseErrorReason;
}

/** B5 — Approve & Close: PENDING_REVIEW → CLOSED. */
export function approveAndClose(
  complaintId: string,
): ApproveCloseResult | ApproveCloseError {
  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.status !== "PENDING_REVIEW") {
    return { ok: false, reason: "NOT_PENDING_REVIEW" };
  }

  const nowIso = new Date().toISOString();
  const historyEntry: MockDecisionHistoryEntry = {
    id: `hist-approve-${Date.now()}`,
    type: "APPROVE",
    at: nowIso,
    actorId: MOCK_SUPERVISOR_ID,
    actorName: MOCK_SUPERVISOR_NAME,
    fromStatus: "PENDING_REVIEW",
    toStatus: "CLOSED",
  };

  const updated: MockComplaint = {
    ...current,
    status: "CLOSED",
    closedAt: nowIso,
    rejectReason: null,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: [...(current.decisionHistory ?? []), historyEntry],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type RejectReviewErrorReason =
  | "NOT_FOUND"
  | "NOT_PENDING_REVIEW"
  | "REASON_REQUIRED";

export interface RejectReviewResult {
  ok: true;
  complaint: MockComplaint;
}

export interface RejectReviewError {
  ok: false;
  reason: RejectReviewErrorReason;
}

/**
 * B5 / R2-B1 — Reject: PENDING_REVIEW → IN_PROGRESS.
 * Appends REJECT Decision History (SCR-HX-01). Continuity UI = SCR-WS-06 (R2-B1).
 */
export function rejectReview(
  complaintId: string,
  reason: string,
): RejectReviewResult | RejectReviewError {
  const trimmed = reason.trim();
  if (!trimmed) return { ok: false, reason: "REASON_REQUIRED" };

  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.status !== "PENDING_REVIEW") {
    return { ok: false, reason: "NOT_PENDING_REVIEW" };
  }

  const nowIso = new Date().toISOString();
  const historyEntry: MockDecisionHistoryEntry = {
    id: `hist-reject-${Date.now()}`,
    type: "REJECT",
    at: nowIso,
    actorId: MOCK_SUPERVISOR_ID,
    actorName: MOCK_SUPERVISOR_NAME,
    reason: trimmed,
    fromStatus: "PENDING_REVIEW",
    toStatus: "IN_PROGRESS",
  };

  const updated: MockComplaint = {
    ...current,
    status: "IN_PROGRESS",
    rejectReason: trimmed,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: [...(current.decisionHistory ?? []), historyEntry],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

/**
 * True when Officer should open SCR-WS-06 (rejected continuity) instead of SCR-WS-04.
 * Requires IN_PROGRESS + Decision History REJECT (or rejectReason mirror).
 */
export function hasRejectContinuity(complaint: MockComplaint): boolean {
  if (complaint.status !== "IN_PROGRESS") return false;
  const history = complaint.decisionHistory ?? [];
  if (history.some((entry) => entry.type === "REJECT")) return true;
  return Boolean(complaint.rejectReason?.trim());
}

/** Latest REJECT history entry (SCR-HX-01 continuity). */
export function latestRejectHistory(
  complaint: MockComplaint,
): MockDecisionHistoryEntry | undefined {
  const history = complaint.decisionHistory ?? [];
  for (let i = history.length - 1; i >= 0; i -= 1) {
    const entry = history[i]!;
    if (entry.type === "REJECT") return entry;
  }
  return undefined;
}

/**
 * R2-B1 — Save correction without status change (SCR-WS-06 when not ready to resubmit).
 * Updates resolution summary only; One Primary Action: Save correction XOR Resubmit.
 */
export type SaveCorrectionErrorReason =
  | "NOT_FOUND"
  | "NOT_IN_PROGRESS"
  | "NOT_ASSIGNEE"
  | "RESOLUTION_REQUIRED"
  | "HISTORY_REQUIRED";

export interface SaveCorrectionResult {
  ok: true;
  complaint: MockComplaint;
}

export interface SaveCorrectionError {
  ok: false;
  reason: SaveCorrectionErrorReason;
}

export function saveCorrection(
  complaintId: string,
  resolutionSummary: string,
  officerId: string = MOCK_OFFICER_ID,
): SaveCorrectionResult | SaveCorrectionError {
  const trimmed = resolutionSummary.trim();
  if (!trimmed) return { ok: false, reason: "RESOLUTION_REQUIRED" };

  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.assigneeOfficerId !== officerId) {
    return { ok: false, reason: "NOT_ASSIGNEE" };
  }
  if (current.status !== "IN_PROGRESS") {
    return { ok: false, reason: "NOT_IN_PROGRESS" };
  }
  if (!hasRejectContinuity(current)) {
    return { ok: false, reason: "HISTORY_REQUIRED" };
  }

  const updated: MockComplaint = {
    ...current,
    resolutionSummary: trimmed,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: (current.decisionHistory ?? []).map((e) => ({ ...e })),
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

/** Continuity gate — Decision History must include REJECT before resubmit. */
export function hasRequiredRejectHistory(complaint: MockComplaint): boolean {
  return (complaint.decisionHistory ?? []).some((e) => e.type === "REJECT");
}

/** True when Officer should open SCR-WS-07 (reopened continuation). */
export function hasReopenContinuity(complaint: MockComplaint): boolean {
  return complaint.status === "REOPENED";
}

/** Closure record present for SCR-HX-02 / SCR-WS-12 continuity. */
export function hasRequiredClosureHistory(complaint: MockComplaint): boolean {
  return (
    Boolean(complaint.closedAt) ||
    (complaint.decisionHistory ?? []).some((e) => e.type === "APPROVE")
  );
}

export type RequestReopenErrorReason =
  | "NOT_FOUND"
  | "NOT_CLOSED"
  | "ALREADY_PENDING"
  | "REASON_REQUIRED"
  | "ACTIVE_CASE_EXISTS";

export interface RequestReopenResult {
  ok: true;
  complaint: MockComplaint;
}

export interface RequestReopenError {
  ok: false;
  reason: RequestReopenErrorReason;
}

/**
 * R2-B2 / SCR-WS-03 — Route reopen request: CLOSED → CLOSED + reopenPending.
 * Does not create a new case.
 */
export function requestReopen(
  complaintId: string,
  reason: string,
  officerId: string = MOCK_OFFICER_ID,
): RequestReopenResult | RequestReopenError {
  const trimmed = reason.trim();
  if (!trimmed) return { ok: false, reason: "REASON_REQUIRED" };

  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.status !== "CLOSED") {
    return { ok: false, reason: "NOT_CLOSED" };
  }
  if (current.reopenPending) {
    return { ok: false, reason: "ALREADY_PENDING" };
  }
  if (listActiveCasesByCustomerRef(current.customerRef).length > 0) {
    return { ok: false, reason: "ACTIVE_CASE_EXISTS" };
  }

  const nowIso = new Date().toISOString();
  const historyEntry: MockDecisionHistoryEntry = {
    id: `hist-reopen-req-${Date.now()}`,
    type: "REOPEN_REQUEST",
    at: nowIso,
    actorId: officerId,
    actorName: "Demo Officer",
    reason: trimmed,
    fromStatus: "CLOSED",
    toStatus: "CLOSED",
  };

  const updated: MockComplaint = {
    ...current,
    reopenPending: true,
    reopenReason: trimmed,
    reopenRequestedAt: nowIso,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: [...(current.decisionHistory ?? []), historyEntry],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type ApproveReopenErrorReason =
  | "NOT_FOUND"
  | "NOT_PENDING_REOPEN"
  | "HISTORY_REQUIRED";

export interface ApproveReopenResult {
  ok: true;
  complaint: MockComplaint;
}

export interface ApproveReopenError {
  ok: false;
  reason: ApproveReopenErrorReason;
}

/**
 * R2-B2 / SCR-WS-12 — Approve reopen: CLOSED+pending → REOPENED.
 * Keeps assignee for Officer continuation (SCR-WS-07).
 */
export function approveReopen(
  complaintId: string,
): ApproveReopenResult | ApproveReopenError {
  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.status !== "CLOSED" || !current.reopenPending) {
    return { ok: false, reason: "NOT_PENDING_REOPEN" };
  }
  if (!hasRequiredClosureHistory(current)) {
    return { ok: false, reason: "HISTORY_REQUIRED" };
  }

  const nowIso = new Date().toISOString();
  const historyEntry: MockDecisionHistoryEntry = {
    id: `hist-reopen-ok-${Date.now()}`,
    type: "REOPEN_APPROVE",
    at: nowIso,
    actorId: MOCK_SUPERVISOR_ID,
    actorName: MOCK_SUPERVISOR_NAME,
    fromStatus: "CLOSED",
    toStatus: "REOPENED",
  };

  const updated: MockComplaint = {
    ...current,
    status: "REOPENED",
    reopenPending: false,
    assigneeOfficerId: current.assigneeOfficerId ?? MOCK_OFFICER_ID,
    slaDueAt: hoursFrom(nowIso, 24),
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: [...(current.decisionHistory ?? []), historyEntry],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type RejectReopenErrorReason =
  | "NOT_FOUND"
  | "NOT_PENDING_REOPEN"
  | "REASON_REQUIRED"
  | "HISTORY_REQUIRED";

export interface RejectReopenResult {
  ok: true;
  complaint: MockComplaint;
}

export interface RejectReopenError {
  ok: false;
  reason: RejectReopenErrorReason;
}

/**
 * R2-B2 / SCR-WS-12 — Reject reopen: clear pending; remain CLOSED.
 */
export function rejectReopen(
  complaintId: string,
  reason: string,
): RejectReopenResult | RejectReopenError {
  const trimmed = reason.trim();
  if (!trimmed) return { ok: false, reason: "REASON_REQUIRED" };

  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.status !== "CLOSED" || !current.reopenPending) {
    return { ok: false, reason: "NOT_PENDING_REOPEN" };
  }
  if (!hasRequiredClosureHistory(current)) {
    return { ok: false, reason: "HISTORY_REQUIRED" };
  }

  const nowIso = new Date().toISOString();
  const historyEntry: MockDecisionHistoryEntry = {
    id: `hist-reopen-no-${Date.now()}`,
    type: "REOPEN_REJECT",
    at: nowIso,
    actorId: MOCK_SUPERVISOR_ID,
    actorName: MOCK_SUPERVISOR_NAME,
    reason: trimmed,
    fromStatus: "CLOSED",
    toStatus: "CLOSED",
  };

  const updated: MockComplaint = {
    ...current,
    reopenPending: false,
    reopenReason: null,
    reopenRequestedAt: null,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: [...(current.decisionHistory ?? []), historyEntry],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type ContinueReopenedErrorReason =
  | "NOT_FOUND"
  | "NOT_REOPENED"
  | "NOT_ASSIGNEE"
  | "HISTORY_REQUIRED";

export interface ContinueReopenedResult {
  ok: true;
  complaint: MockComplaint;
}

export interface ContinueReopenedError {
  ok: false;
  reason: ContinueReopenedErrorReason;
}

/**
 * R2-B2 / SCR-WS-07 — Continue prior case: REOPENED → IN_PROGRESS.
 */
export function continueReopened(
  complaintId: string,
  officerId: string = MOCK_OFFICER_ID,
): ContinueReopenedResult | ContinueReopenedError {
  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.assigneeOfficerId !== officerId) {
    return { ok: false, reason: "NOT_ASSIGNEE" };
  }
  if (current.status !== "REOPENED") {
    return { ok: false, reason: "NOT_REOPENED" };
  }
  if (
    !(current.decisionHistory ?? []).some(
      (e) => e.type === "REOPEN_APPROVE" || e.type === "APPROVE",
    )
  ) {
    return { ok: false, reason: "HISTORY_REQUIRED" };
  }

  const updated: MockComplaint = {
    ...current,
    status: "IN_PROGRESS",
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: (current.decisionHistory ?? []).map((e) => ({ ...e })),
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

const ESCALATION_HISTORY_TYPES: ReadonlySet<MockDecisionHistoryType> = new Set([
  "ESCALATION_OPEN",
  "ESCALATION_CONTEXT_REQUEST",
  "ESCALATION_CONTEXT_PROVIDED",
  "ESCALATION_HANDLE",
  "ESCALATION_FORWARD",
]);

/** SCR-HX-02 escalation portion — continuity gate for SCR-WS-11. */
export function hasRequiredEscalationHistory(complaint: MockComplaint): boolean {
  if (complaint.escalationNote?.trim()) return true;
  return (complaint.decisionHistory ?? []).some((e) =>
    ESCALATION_HISTORY_TYPES.has(e.type),
  );
}

/** Officer entry to SCR-WS-08 — context requested, escalation still open. */
export function hasEscalationContextRequest(complaint: MockComplaint): boolean {
  return (
    complaint.escalationNew &&
    complaint.escalationContextRequested &&
    complaint.status !== "CLOSED"
  );
}

export type RequestEscalationContextErrorReason =
  | "NOT_FOUND"
  | "NOT_ESCALATION"
  | "ALREADY_REQUESTED"
  | "HISTORY_REQUIRED";

export interface RequestEscalationContextResult {
  ok: true;
  complaint: MockComplaint;
}

export interface RequestEscalationContextError {
  ok: false;
  reason: RequestEscalationContextErrorReason;
}

/**
 * R2-B3 / SCR-WS-11 secondary — Request officer context → SCR-WS-08.
 * Does not clear escalation; does not reset officer progress.
 */
export function requestEscalationContext(
  complaintId: string,
): RequestEscalationContextResult | RequestEscalationContextError {
  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (!current.escalationNew || current.status === "CLOSED") {
    return { ok: false, reason: "NOT_ESCALATION" };
  }
  if (!hasRequiredEscalationHistory(current)) {
    return { ok: false, reason: "HISTORY_REQUIRED" };
  }
  if (current.escalationContextRequested) {
    return { ok: false, reason: "ALREADY_REQUESTED" };
  }

  const nowIso = new Date().toISOString();
  const historyEntry: MockDecisionHistoryEntry = {
    id: `hist-esc-ctx-req-${Date.now()}`,
    type: "ESCALATION_CONTEXT_REQUEST",
    at: nowIso,
    actorId: MOCK_SUPERVISOR_ID,
    actorName: MOCK_SUPERVISOR_NAME,
    reason: "Supervisor requested officer escalation context",
    fromStatus: current.status,
    toStatus: current.status,
  };
  const updated: MockComplaint = {
    ...current,
    escalationContextRequested: true,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: [...(current.decisionHistory ?? []), historyEntry],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type SubmitEscalationContextErrorReason =
  | "NOT_FOUND"
  | "NOT_REQUESTED"
  | "NOT_ASSIGNEE"
  | "CONTEXT_REQUIRED"
  | "ESCALATION_CLOSED";

export interface SubmitEscalationContextResult {
  ok: true;
  complaint: MockComplaint;
}

export interface SubmitEscalationContextError {
  ok: false;
  reason: SubmitEscalationContextErrorReason;
}

/**
 * R2-B3 / SCR-WS-08 — Provide escalation context.
 * Progress notes are preserved (no reset). Escalation remains open for Supervisor.
 */
export function submitEscalationContext(
  complaintId: string,
  contextPackage: string,
  officerId: string = MOCK_OFFICER_ID,
): SubmitEscalationContextResult | SubmitEscalationContextError {
  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (current.assigneeOfficerId !== officerId) {
    return { ok: false, reason: "NOT_ASSIGNEE" };
  }
  if (!current.escalationNew || current.status === "CLOSED") {
    return { ok: false, reason: "ESCALATION_CLOSED" };
  }
  if (!current.escalationContextRequested) {
    return { ok: false, reason: "NOT_REQUESTED" };
  }
  const trimmed = contextPackage.trim();
  if (!trimmed) {
    return { ok: false, reason: "CONTEXT_REQUIRED" };
  }

  const nowIso = new Date().toISOString();
  const historyEntry: MockDecisionHistoryEntry = {
    id: `hist-esc-ctx-${Date.now()}`,
    type: "ESCALATION_CONTEXT_PROVIDED",
    at: nowIso,
    actorId: officerId,
    actorName: "Demo Officer",
    reason: trimmed,
    fromStatus: current.status,
    toStatus: current.status,
  };
  const updated: MockComplaint = {
    ...current,
    escalationContextRequested: false,
    escalationContextPackage: trimmed,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: [...(current.decisionHistory ?? []), historyEntry],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type HandleEscalationErrorReason =
  | "NOT_FOUND"
  | "NOT_ESCALATION"
  | "HISTORY_REQUIRED";

export interface HandleEscalationResult {
  ok: true;
  complaint: MockComplaint;
}

export interface HandleEscalationError {
  ok: false;
  reason: HandleEscalationErrorReason;
}

/**
 * R2-B3 / SCR-WS-11 — Handle escalation (clears new-escalation queue flag).
 * Case status and officer progress remain unchanged.
 */
export function handleEscalation(
  complaintId: string,
): HandleEscalationResult | HandleEscalationError {
  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (!current.escalationNew || current.status === "CLOSED") {
    return { ok: false, reason: "NOT_ESCALATION" };
  }
  if (!hasRequiredEscalationHistory(current)) {
    return { ok: false, reason: "HISTORY_REQUIRED" };
  }

  const nowIso = new Date().toISOString();
  const historyEntry: MockDecisionHistoryEntry = {
    id: `hist-esc-handle-${Date.now()}`,
    type: "ESCALATION_HANDLE",
    at: nowIso,
    actorId: MOCK_SUPERVISOR_ID,
    actorName: MOCK_SUPERVISOR_NAME,
    reason: "Supervisor handled escalation",
    fromStatus: current.status,
    toStatus: current.status,
  };
  const updated: MockComplaint = {
    ...current,
    escalationNew: false,
    escalationContextRequested: false,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: [...(current.decisionHistory ?? []), historyEntry],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

export type ForwardEscalationErrorReason =
  | "NOT_FOUND"
  | "NOT_ESCALATION"
  | "REASON_REQUIRED"
  | "HISTORY_REQUIRED";

export interface ForwardEscalationResult {
  ok: true;
  complaint: MockComplaint;
}

export interface ForwardEscalationError {
  ok: false;
  reason: ForwardEscalationErrorReason;
}

/**
 * R2-B3 / SCR-WS-11 — Forward escalation (Branch → Head Office path, mock).
 * Clears new-escalation flag; preserves case status and progress.
 */
export function forwardEscalation(
  complaintId: string,
  reason: string,
): ForwardEscalationResult | ForwardEscalationError {
  const index = complaints.findIndex((c) => c.id === complaintId);
  if (index < 0) return { ok: false, reason: "NOT_FOUND" };

  const current = complaints[index]!;
  if (!current.escalationNew || current.status === "CLOSED") {
    return { ok: false, reason: "NOT_ESCALATION" };
  }
  if (!hasRequiredEscalationHistory(current)) {
    return { ok: false, reason: "HISTORY_REQUIRED" };
  }
  const trimmed = reason.trim();
  if (!trimmed) {
    return { ok: false, reason: "REASON_REQUIRED" };
  }

  const nowIso = new Date().toISOString();
  const historyEntry: MockDecisionHistoryEntry = {
    id: `hist-esc-fwd-${Date.now()}`,
    type: "ESCALATION_FORWARD",
    at: nowIso,
    actorId: MOCK_SUPERVISOR_ID,
    actorName: MOCK_SUPERVISOR_NAME,
    reason: trimmed,
    fromStatus: current.status,
    toStatus: current.status,
  };
  const updated: MockComplaint = {
    ...current,
    escalationNew: false,
    escalationContextRequested: false,
    escalationNote: current.escalationNote ?? trimmed,
    progressNotes: [...current.progressNotes],
    followUpNotes: [...current.followUpNotes],
    evidenceItems: current.evidenceItems.map((e) => ({ ...e })),
    decisionHistory: [...(current.decisionHistory ?? []), historyEntry],
  };
  complaints = [
    ...complaints.slice(0, index),
    updated,
    ...complaints.slice(index + 1),
  ];
  emit();
  return { ok: true, complaint: cloneComplaint(updated) };
}

/** Completeness checklist for SCR-WS-01 (required vs filled). */
export function intakeCompleteness(input: {
  customerRef: string;
  subject: string;
  description: string;
  category: string;
  channel: string;
  priority: string;
}): { key: string; filled: boolean }[] {
  return [
    { key: "customer", filled: Boolean(input.customerRef.trim()) },
    { key: "subject", filled: Boolean(input.subject.trim()) },
    { key: "description", filled: Boolean(input.description.trim()) },
    { key: "category", filled: Boolean(input.category) },
    { key: "channel", filled: Boolean(input.channel) },
    { key: "priority", filled: Boolean(input.priority) },
  ];
}

export function isIntakeFormComplete(input: {
  customerRef: string;
  customerName: string;
  subject: string;
  description: string;
  category: string;
  channel: string;
  priority: string;
}): boolean {
  return intakeCompleteness(input).every((item) => item.filled);
}

/** Test / demo helper — restore seed data. */
export function resetAssignmentRepository(): void {
  complaints = SEED.map(cloneComplaint);
  heldDrafts = [];
  registerSeq = 100;
  emit();
}
