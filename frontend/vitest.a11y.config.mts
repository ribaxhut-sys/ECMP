import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";

/** Separate Vitest project for warning-mode a11y (FE-CI-POL-001 Phase B). */
export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.a11y.test.{ts,tsx}"],
    exclude: ["**/node_modules/**", "**/.next/**", "**/coverage/**"],
  },
});
