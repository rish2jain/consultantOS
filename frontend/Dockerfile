# Multi-stage build for Next.js frontend
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set build-time environment variable (can be overridden at build time)
# Default to production API URL for Cloud Run deployments
ARG NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Disable telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1
# Force webpack instead of Turbopack for Next.js 16
ENV NEXT_PRIVATE_SKIP_TURBO=1

# Build Next.js app
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files from standalone build
# Standalone output structure: .next/standalone contains the server
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

# Expose port (Cloud Run will set PORT env var automatically)
EXPOSE 8080

ENV HOSTNAME="0.0.0.0"
# PORT is set by Cloud Run automatically, don't set it here

# Start Next.js server
# In standalone mode, server.js is at the root after copying .next/standalone
CMD ["node", "server.js"]

