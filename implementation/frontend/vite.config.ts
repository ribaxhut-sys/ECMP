/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'

// Dev: Vite proxies /v1 → backend (same-origin). Production: set
// ECMP_ALLOWED_ORIGINS on the API when FE/BE are on different origins (Sprint-08).
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    ...(mode === 'analyze'
      ? [
          visualizer({
            filename: 'dist/stats.html',
            open: false,
            gzipSize: true,
            brotliSize: true,
            template: 'treemap',
          }),
        ]
      : []),
  ],
  server: {
    port: 5173,
    proxy: {
      '/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
    // a11y suite is warning-mode only (CI continue-on-error via npm run test:a11y).
    exclude: ['**/node_modules/**', '**/dist/**', '**/*.a11y.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json-summary'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/test/**', 'src/main.tsx', 'src/vite-env.d.ts', '**/*.a11y.test.{ts,tsx}'],
      // Sprint-10 RC1: enforce measured baseline (AC-1). Raise as suite grows.
      thresholds: {
        lines: 12,
        statements: 12,
        functions: 50,
        branches: 50,
      },
    },
  },
}))
