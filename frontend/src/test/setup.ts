import "@testing-library/jest-dom/vitest";

// Vitest sets NODE_ENV=test; api client refuses silent localhost without an explicit base URL.
process.env.NEXT_PUBLIC_API_BASE_URL ??= "http://localhost:8000";
