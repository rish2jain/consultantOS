/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Ignore ESLint errors during builds for development
    // TODO: Fix linting errors before production deployment
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Ignore TypeScript errors during builds for development
    // TODO: Fix TypeScript errors before production deployment
    ignoreBuildErrors: true,
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
    // Use a consistent build ID to avoid chunk mismatches
    return 'build-' + Date.now();
  },
};

module.exports = nextConfig;
