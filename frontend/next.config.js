/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Allow ESLint errors during build only if SKIP_LINT env var is set
    ignoreDuringBuilds: process.env.SKIP_LINT === 'true',
  },
  typescript: {
    // Allow TypeScript errors during build only if SKIP_TYPE_CHECK env var is set
    ignoreBuildErrors: process.env.SKIP_TYPE_CHECK === 'true',
  },
  // Enable typed routes for Next.js
  typedRoutes: true,
  // Enable standalone output for Cloud Run deployment
  output: "standalone",
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || 
      (process.env.NODE_ENV === 'production' 
        ? "https://consultantos-api-187550875653.us-central1.run.app"
        : "http://localhost:8080"),
  },
  // Ensure proper handling of static files
  generateBuildId: async () => {
    // Use git commit hash for reproducible builds, fallback to version or timestamp
    try {
      const { execSync } = require('child_process');
      const gitHash = execSync('git rev-parse --short HEAD', { encoding: 'utf-8' }).trim();
      return gitHash;
    } catch {
      // Fallback to BUILD_ID env var or package version
      return process.env.BUILD_ID || require('./package.json').version || `build-${Date.now()}`;
    }
  },
};

module.exports = nextConfig;
