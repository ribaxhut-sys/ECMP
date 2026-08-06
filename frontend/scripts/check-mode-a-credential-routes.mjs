#!/usr/bin/env node
/**
 * K-3 / AEN-03 — Mode A credential-route build guard (ADR-014).
 *
 * Mode A (standalone) may ship local login / password UI.
 * Mode B (enterprise) builds MUST hard-fail if those routes remain in the tree.
 *
 * Usage:
 *   node scripts/check-mode-a-credential-routes.mjs
 *   ECMP_FRONTEND_DEPLOY_MODE=enterprise node scripts/check-mode-a-credential-routes.mjs
 *   node scripts/check-mode-a-credential-routes.mjs --mode enterprise
 *   node scripts/check-mode-a-credential-routes.mjs --self-test
 *
 * Exit codes:
 *   0 = PASS
 *   1 = hard-fail (enterprise profile found Mode A credential routes)
 *   2 = usage / self-test failure
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FRONTEND_ROOT = path.resolve(__dirname, "..");

/** App Router pages that own Mode A local credential AuthN UX (FE-ARCH §5.3). */
export const MODE_A_CREDENTIAL_ROUTES = Object.freeze([
  "src/app/login/page.tsx",
]);

export function resolveMode(argv) {
  const flagIdx = argv.indexOf("--mode");
  if (flagIdx >= 0 && argv[flagIdx + 1]) {
    return String(argv[flagIdx + 1]).trim().toLowerCase();
  }
  const env = (process.env.ECMP_FRONTEND_DEPLOY_MODE || "standalone")
    .trim()
    .toLowerCase();
  return env || "standalone";
}

export function inventory() {
  return MODE_A_CREDENTIAL_ROUTES.map((rel) => {
    const abs = path.join(FRONTEND_ROOT, rel);
    return { rel, present: fs.existsSync(abs) };
  });
}

function printInventory(rows) {
  console.log("Mode A credential routes (FE-ARCH §5.3 / ADR-014):");
  for (const row of rows) {
    console.log(`  [${row.present ? "PRESENT" : "MISSING"}] ${row.rel}`);
  }
}

export function checkStandalone(rows) {
  printInventory(rows);
  const present = rows.filter((r) => r.present);
  console.log(
    `OK (standalone): ${present.length}/${rows.length} Mode A credential route(s) present — allowed for Mode A delivery.`,
  );
  console.log(
    "Note: set ECMP_FRONTEND_DEPLOY_MODE=enterprise to hard-fail when any of these remain (Mode B builds).",
  );
  return 0;
}

export function checkEnterprise(rows) {
  printInventory(rows);
  const present = rows.filter((r) => r.present);
  if (present.length === 0) {
    console.log(
      "OK (enterprise): no Mode A credential routes present — build may proceed.",
    );
    return 0;
  }
  console.error(
    "FAIL (enterprise): Mode A credential routes must not ship in Mode B / enterprise builds (ADR-014 / AEN-03 / audit K-3).",
  );
  for (const row of present) {
    console.error(`  - ${row.rel}`);
  }
  console.error(
    "Remove or exclude these routes before an enterprise production build, or keep ECMP_FRONTEND_DEPLOY_MODE=standalone for Mode A only.",
  );
  return 1;
}

function selfTest() {
  const rows = inventory();
  const presentCount = rows.filter((r) => r.present).length;
  if (presentCount === 0) {
    console.error(
      "SELF-TEST FAIL: expected Mode A credential routes to exist while Mode B is CLOSED; inventory empty.",
    );
    return 2;
  }
  const code = checkEnterprise(rows);
  if (code !== 1) {
    console.error(
      `SELF-TEST FAIL: enterprise mode expected exit 1 while routes exist; got ${code}.`,
    );
    return 2;
  }
  console.log(
    "SELF-TEST OK: enterprise profile correctly hard-fails while Mode A credential routes remain.",
  );
  return 0;
}

export function main(argv = process.argv.slice(2)) {
  if (argv.includes("--help") || argv.includes("-h")) {
    console.log(`Usage: check-mode-a-credential-routes.mjs [--mode standalone|enterprise] [--self-test]
Env: ECMP_FRONTEND_DEPLOY_MODE=standalone|enterprise (default: standalone)`);
    return 0;
  }
  if (argv.includes("--self-test")) {
    return selfTest();
  }
  const mode = resolveMode(argv);
  const rows = inventory();
  if (mode === "enterprise" || mode === "mode_b" || mode === "mode-b") {
    return checkEnterprise(rows);
  }
  if (mode === "standalone" || mode === "mode_a" || mode === "mode-a") {
    return checkStandalone(rows);
  }
  console.error(
    `Unknown mode '${mode}'. Use standalone|enterprise (or ECMP_FRONTEND_DEPLOY_MODE).`,
  );
  return 2;
}

const isDirectRun =
  process.argv[1] != null &&
  import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href;

if (isDirectRun) {
  process.exit(main());
}