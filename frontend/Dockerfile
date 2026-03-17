# Stage 1: Base - Common for both Dev and Prod
FROM node:20-alpine AS base
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: Development - Only what we need to run 'npm run dev'
FROM base AS development
COPY . .
# We DO NOT set NODE_ENV here; Next.js handles it automatically
CMD ["npm", "run", "dev"]

# Stage 3: Builder - Only used for Production builds
FROM base AS builder
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

# Stage 4: Runner - The final, tiny production image
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]