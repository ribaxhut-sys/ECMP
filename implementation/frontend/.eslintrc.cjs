/* eslint-env node */
module.exports = {
  root: true,
  env: { browser: true, es2022: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  // Lint only app sources — `eslint .` previously walked verification assets /
  // caches and could hang in constrained CI sandboxes (Sprint-07 P0).
  ignorePatterns: [
    'dist',
    'node_modules',
    'coverage',
    'verification',
    '.eslintrc.cjs',
    'vite.config.ts',
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      {
        allowConstantExport: true,
        // Shared context modules intentionally export hooks alongside providers.
        allowExportNames: ['useAuth', 'useToast'],
      },
    ],
  },
}
