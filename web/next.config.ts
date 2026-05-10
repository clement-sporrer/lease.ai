import type { NextConfig } from "next";

const API_INTERNAL = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API_INTERNAL}/:path*`,
      },
    ];
  },
};

export default nextConfig;
