import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL;
    if (backendUrl && !backendUrl.includes("127.0.0.1") && !backendUrl.includes("localhost")) {
      return [
        {
          source: "/api/py/:path*",
          destination: `${backendUrl}/:path*`,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
