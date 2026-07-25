import type { NextConfig } from "next";

// R2-04: fail production builds clearly when the API URL is missing.
// Local `next dev` may omit it (client falls back to localhost).
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "";
if (process.env.NODE_ENV === "production" && !apiBaseUrl) {
  throw new Error(
    "NEXT_PUBLIC_API_BASE_URL must be set for production builds (refusing silent localhost embed)",
  );
}

const nextConfig: NextConfig = {
  output: "standalone",
  reactStrictMode: true,
};

export default nextConfig;
