/**
 * K-3 — Node test for Mode A credential-route build guard.
 * Run: node --test scripts/check-mode-a-credential-routes.test.mjs
 */
import assert from "node:assert/strict";
import test from "node:test";
import {
  MODE_A_CREDENTIAL_ROUTES,
  checkEnterprise,
  checkStandalone,
  inventory,
  resolveMode,
} from "./check-mode-a-credential-routes.mjs";

test("inventories all Mode A credential pages as present while Mode B is CLOSED", () => {
  const rows = inventory();
  assert.equal(rows.length, MODE_A_CREDENTIAL_ROUTES.length);
  assert.ok(rows.every((r) => r.present));
});

test("resolveMode prefers --mode flag", () => {
  assert.equal(resolveMode(["--mode", "enterprise"]), "enterprise");
  assert.equal(resolveMode(["--mode", "standalone"]), "standalone");
});

test("checkStandalone allows present Mode A routes", () => {
  assert.equal(checkStandalone(inventory()), 0);
});

test("checkEnterprise hard-fails while Mode A credential routes remain", () => {
  assert.equal(checkEnterprise(inventory()), 1);
});
