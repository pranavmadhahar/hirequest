# Frontend Dockerfile
FROM node:20-slim AS build

# Set working directory
WORKDIR /app

# Copy dependency files first (for caching)
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build production bundle
RUN npm run build

# -----------------------------
# Serve stage with lightweight web server
FROM nginx:alpine

# Copy built frontend to nginx html directory
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 for frontend
EXPOSE 80

# Default command
CMD ["nginx", "-g", "daemon off;"]
