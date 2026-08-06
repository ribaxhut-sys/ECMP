import { afterEach, describe, expect, it } from "vitest";
import {
  getShellBatchOverlineKey,
  isBatchAtLeast,
  isBatchB0,
  isBatchB5,
  isBatchB6,
  isBatchR2B1,
  isBatchR2B2,
  isBatchR2B3,
  isMockAuthEnabled,
  isShellUiBatch,
} from "@/shared/config/uiBatch";

describe("uiBatch", () => {
  const originalBatch = process.env.NEXT_PUBLIC_ECMP_UI_BATCH;
  const originalMock = process.env.NEXT_PUBLIC_ECMP_MOCK_AUTH;

  afterEach(() => {
    process.env.NEXT_PUBLIC_ECMP_UI_BATCH = originalBatch;
    process.env.NEXT_PUBLIC_ECMP_MOCK_AUTH = originalMock;
  });

  it("detects R2B3 as shell batch unlocking prior R2 and R1", () => {
    process.env.NEXT_PUBLIC_ECMP_UI_BATCH = "R2B3";
    delete process.env.NEXT_PUBLIC_ECMP_MOCK_AUTH;
    expect(isBatchR2B3()).toBe(true);
    expect(isBatchR2B2()).toBe(false);
    expect(isBatchAtLeast("R2B2")).toBe(true);
    expect(isBatchAtLeast("R2B3")).toBe(true);
    expect(isBatchAtLeast("B6")).toBe(true);
    expect(getShellBatchOverlineKey()).toBe("batchOverlineR2B3");
  });

  it("detects R2B2 as shell batch unlocking R2B1 and R1", () => {
    process.env.NEXT_PUBLIC_ECMP_UI_BATCH = "R2B2";
    delete process.env.NEXT_PUBLIC_ECMP_MOCK_AUTH;
    expect(isBatchR2B2()).toBe(true);
    expect(isBatchR2B1()).toBe(false);
    expect(isBatchR2B3()).toBe(false);
    expect(isBatchAtLeast("R2B1")).toBe(true);
    expect(isBatchAtLeast("R2B2")).toBe(true);
    expect(isBatchAtLeast("R2B3")).toBe(false);
    expect(isBatchAtLeast("B6")).toBe(true);
    expect(getShellBatchOverlineKey()).toBe("batchOverlineR2B2");
  });

  it("detects R2B1 as shell batch with prior batches unlocked", () => {
    process.env.NEXT_PUBLIC_ECMP_UI_BATCH = "R2B1";
    delete process.env.NEXT_PUBLIC_ECMP_MOCK_AUTH;
    expect(isBatchR2B1()).toBe(true);
    expect(isBatchR2B2()).toBe(false);
    expect(isBatchB6()).toBe(false);
    expect(isBatchAtLeast("B0")).toBe(true);
    expect(isBatchAtLeast("B6")).toBe(true);
    expect(isBatchAtLeast("R2B1")).toBe(true);
    expect(isBatchAtLeast("R2B2")).toBe(false);
    expect(isShellUiBatch()).toBe(true);
    expect(isMockAuthEnabled()).toBe(true);
    expect(getShellBatchOverlineKey()).toBe("batchOverlineR2B1");
  });

  it("detects B6 as shell batch with mock auth and at-least helpers", () => {
    process.env.NEXT_PUBLIC_ECMP_UI_BATCH = "B6";
    delete process.env.NEXT_PUBLIC_ECMP_MOCK_AUTH;
    expect(isBatchB6()).toBe(true);
    expect(isBatchB5()).toBe(false);
    expect(isBatchR2B1()).toBe(false);
    expect(isBatchAtLeast("B0")).toBe(true);
    expect(isBatchAtLeast("B5")).toBe(true);
    expect(isBatchAtLeast("B6")).toBe(true);
    expect(isBatchAtLeast("R2B1")).toBe(false);
    expect(isShellUiBatch()).toBe(true);
    expect(isMockAuthEnabled()).toBe(true);
    expect(getShellBatchOverlineKey()).toBe("batchOverlineB6");
  });

  it("detects B5 without unlocking B6 helpers", () => {
    process.env.NEXT_PUBLIC_ECMP_UI_BATCH = "B5";
    delete process.env.NEXT_PUBLIC_ECMP_MOCK_AUTH;
    expect(isBatchB5()).toBe(true);
    expect(isBatchB6()).toBe(false);
    expect(isBatchAtLeast("B5")).toBe(true);
    expect(isBatchAtLeast("B6")).toBe(false);
    expect(getShellBatchOverlineKey()).toBe("batchOverlineB5");
  });

  it("detects B0 as shell batch", () => {
    process.env.NEXT_PUBLIC_ECMP_UI_BATCH = "B0";
    delete process.env.NEXT_PUBLIC_ECMP_MOCK_AUTH;
    expect(isBatchB0()).toBe(true);
    expect(isBatchAtLeast("B1")).toBe(false);
    expect(getShellBatchOverlineKey()).toBe("batchOverline");
  });
});
