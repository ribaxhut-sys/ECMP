/// <reference types="vitest/config" />
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

/** Separate Vitest project for warning-mode a11y (not part of blocking coverage gate). */
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
    include: ['src/**/*.a11y.test.{ts,tsx}'],
    exclude: ['**/node_modules/**', '**/dist/**'],
  },
})
