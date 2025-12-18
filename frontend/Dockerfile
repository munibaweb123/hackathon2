# Frontend Dockerfile for hackathon-todo
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run the application in development mode
CMD ["npm", "run", "dev"]