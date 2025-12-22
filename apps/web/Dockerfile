# Frontend Dockerfile - Next.js Application

FROM node:20-alpine AS base

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy application code
COPY . .

# Build the Next.js application
RUN pnpm build

# Production stage
FROM node:20-alpine AS runner

RUN npm install -g pnpm

WORKDIR /app

ENV NODE_ENV production

# Copy built application
COPY --from=base /app/package.json ./
COPY --from=base /app/pnpm-lock.yaml* ./
COPY --from=base /app/.next ./.next
COPY --from=base /app/public ./public
COPY --from=base /app/node_modules ./node_modules

EXPOSE 3000

ENV HOSTNAME=0.0.0.0

CMD ["pnpm", "start"]
