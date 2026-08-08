/**
 * DEC-020 — Aggregate path/header helpers (no network).
 * Keeps `/api/v1/cm` distinct from foundation `/api/v1/complaints`.
 */
import { describe, expect, it } from "vitest";
import {
  CM_BATCH1_BASE,
  buildCmBatch1CreateHeaders,
  cmBatch1Paths,
} from "./cmBatch1Contract";
import { FOUNDATION_COMPLAINTS_BASE } from "./dualSotNamespaces";

describe("cmBatch1Paths", () => {
  it("anchors all Aggregate ops under /api/v1/cm", () => {
    const paths = cmBatch1Paths();
    expect(CM_BATCH1_BASE).toBe("/api/v1/cm");
    expect(paths.complaints).toBe("/api/v1/cm/complaints");
    expect(paths.customerSearch).toBe("/api/v1/cm/customers/search");
    expect(paths.duplicatesCheck).toBe("/api/v1/cm/duplicates/check");
    expect(paths.attachmentsTransfer).toBe("/api/v1/cm/attachments/transfer");
    expect(paths.supervisorQueue).toBe("/api/v1/cm/supervisor/queue");
    expect(paths.complaint("c/1")).toBe("/api/v1/cm/complaints/c%2F1");
    expect(paths.intakeEscalationRequest("c/1")).toBe(
      "/api/v1/cm/complaints/c%2F1/intake-escalation/request",
    );
    expect(paths.customer360("cust 1")).toBe(
      "/api/v1/cm/customers/cust%201/batch1-360",
    );
  });

  it("does not collide with foundation /api/v1/complaints create path", () => {
    expect(cmBatch1Paths().complaints).not.toBe(FOUNDATION_COMPLAINTS_BASE);
  });
});

describe("buildCmBatch1CreateHeaders", () => {
  it("omits empty optional headers", () => {
    expect(buildCmBatch1CreateHeaders()).toEqual({});
    expect(
      buildCmBatch1CreateHeaders({ idempotencyKey: "  ", channelMessageId: "" }),
    ).toEqual({});
  });

  it("sets Idempotency-Key and X-Channel-Message-Id when provided", () => {
    expect(
      buildCmBatch1CreateHeaders({
        idempotencyKey: " req-1 ",
        channelMessageId: " ch-9 ",
      }),
    ).toEqual({
      "Idempotency-Key": "req-1",
      "X-Channel-Message-Id": "ch-9",
    });
  });
});
