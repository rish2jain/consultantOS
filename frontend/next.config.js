/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Only ignore in development, require fixes for production
    ignoreDuringBuilds: process.env.NODE_ENV === 'development',
  },
  typescript: {
    // Only ignore in development, require fixes for production
    ignoreBuildErrors: process.env.NODE_ENV === 'development',
  },
  // Enable standalone output for Cloud Run deployment
  output: "standalone",
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
  },
  // Fix for missing chunk files - ensure proper webpack configuration
  webpack: (config, { isServer }) => {
    // Fix for dynamic imports and code splitting
    if (!isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            // Vendor chunk for node_modules
            vendor: {
              name: 'vendor',
              chunks: 'all',
              test: /node_modules/,
              priority: 20,
            },
            // Common chunk for shared code
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              priority: 10,
              reuseExistingChunk: true,
            },
          },
        },
      };
    }
    return config;
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
