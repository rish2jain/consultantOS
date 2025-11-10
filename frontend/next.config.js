/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Only ignore ESLint errors in non-production environments
    // Production builds should fail on lint errors
    ignoreDuringBuilds:
      process.env.NODE_ENV !== "production" || process.env.DEV_DEMO === "true",
  },
  typescript: {
    // Only ignore TypeScript errors in non-production environments
    // Production builds should fail on type errors
    ignoreBuildErrors:
      process.env.NODE_ENV !== "production" || process.env.DEV_DEMO === "true",
  },
  // Enable standalone output for Cloud Run deployment
  output: "standalone",
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
  },
};

module.exports = nextConfig;
