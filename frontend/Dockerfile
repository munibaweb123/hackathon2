# syntax=docker/dockerfile:1

# ===================================
# Multi-stage Dockerfile for Next.js Frontend
# Production-optimized with security hardening
# ===================================

# -----------------------------------
# Stage 1: Dependencies
# -----------------------------------
FROM node:20-alpine AS deps

WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci --only=production=false

# -----------------------------------
# Stage 2: Builder
# -----------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build arguments for environment variables
ARG NEXT_PUBLIC_API_URL=http://todo-backend:8000
ARG NEXT_PUBLIC_APP_VERSION=v1.0.0

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_APP_VERSION=$NEXT_PUBLIC_APP_VERSION
ENV NEXT_TELEMETRY_DISABLED=1

# Build the application
RUN npm run build

# -----------------------------------
# Stage 3: Runner - Minimal production image
# -----------------------------------
FROM node:20-alpine AS runner

WORKDIR /app

# Create non-root user with UID 10001+ for Kubernetes pod security compliance
RUN addgroup -g 10001 appgroup && \
    adduser -D -u 10001 -G appgroup -s /sbin/nologin nextjs && \
    mkdir -p /app && \
    chown -R nextjs:appgroup /app

# Set environment to production
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:appgroup /app/.next/standalone ./
COPY --from=builder --chown=nextjs:appgroup /app/.next/static ./.next/static

# Switch to non-root user (use numeric UID for portability)
USER 10001

# Expose port
EXPOSE 3000

# Health check using wget (built into Alpine, no curl needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --spider -q http://localhost:3000/api/health/live || exit 1

# Run the application
CMD ["node", "server.js"]
