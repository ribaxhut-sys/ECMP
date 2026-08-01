import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";

/**
 * Product frontend unit tests (FE-CI-POL-001 v1.0).
 * Phase C: coverage thresholds are hard-fail in CI.
 * a11y suite remains separate + warn-mode: vitest.a11y.config.ts
 */
export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    exclude: [
      "node_modules",
      ".next",
      "out",
      "coverage",
      "src/**/*.a11y.test.{ts,tsx}",
    ],
    // Bound RSS on ubuntu-latest (~7GiB total).
    fileParallelism: false,
    maxWorkers: 1,
    coverage: {
      provider: "v8",
      // Skip HTML report in CI — large sourcemap walk caused OOM after i18n catalogs.
      reporter: ["text", "json-summary"],
      include: [
        "src/features/**/statusTransitions.ts",
        "src/features/**/createComplaintForm.ts",
        "src/features/**/cmBatch1Attachments.ts",
        "src/features/**/cmBatch1SupervisorQueue.ts",
        "src/features/**/loadReportsData.ts",
        "src/features/**/reportSummaryStats.ts",
        "src/features/**/fileTypes.ts",
        "src/features/**/quickActionConfig.ts",
        "src/features/**/passwordPolicy.ts",
        "src/features/**/routes.ts",
        "src/lib/api/dualSotNamespaces.ts",
        "src/lib/api/cmBatch1Contract.ts",
        "src/shared/utils/cn.ts",
        "src/shared/layouts/app-layout/nav.ts",
      ],
      exclude: [
        "src/**/*.{test,spec}.{ts,tsx}",
        "src/**/*.a11y.test.{ts,tsx}",
        "src/test/**",
        "src/**/*.d.ts",
      ],
      // OD-FE-010 Phase C thresholds (FE-CI-POL-001 v1.0 / FE-CI-POL-CS-001 C-2 activated).
      thresholds: {
        lines: 40,
        statements: 40,
        functions: 30,
        branches: 25,
      },
    },
  },
});
