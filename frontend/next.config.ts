import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

// R2-04: fail production builds clearly when the API URL is missing.
// Local `next dev` may omit it (client falls back to localhost).
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "";
if (process.env.NODE_ENV === "production" && !apiBaseUrl) {
  throw new Error(
    "NEXT_PUBLIC_API_BASE_URL must be set for production builds (refusing silent localhost embed)",
  );
}

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  output: "standalone",
  reactStrictMode: true,
  async headers() {
    return [
      {
        // Fingerprinted assets may be cached forever.
        source: "/_next/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
      {
        // HTML / RSC payloads must revalidate so deploys are not stuck on old JS.
        source: "/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "private, no-cache, no-store, must-revalidate",
          },
        ],
      },
    ];
  },
};

export default withNextIntl(nextConfig);
