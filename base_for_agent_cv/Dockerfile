# Dockerfile for Context7 MCP Server
# Provides a containerized environment for running the MCP server

FROM node:18-alpine

# Install jq for JSON validation
RUN apk add --no-cache jq bash

# Set working directory
WORKDIR /app

# Copy MCP configuration and related files
COPY .mcp.json package.json tsconfig.json ./
COPY validate-mcp-config.sh test-mcp-setup.ts ./

# Make scripts executable
RUN chmod +x validate-mcp-config.sh test-mcp-setup.ts

# Install Node.js dependencies
RUN npm install

# Install the MCP server globally
RUN npm install -g @upstash/context7-mcp@2.1.1

# Validate configuration on build
RUN ./validate-mcp-config.sh

# Environment variables for Upstash Redis (to be provided at runtime)
ENV UPSTASH_REDIS_REST_URL=""
ENV UPSTASH_REDIS_REST_TOKEN=""

# Expose a port if the MCP server uses one (adjust as needed)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "console.log('healthy')" || exit 1

# Default command: run the MCP server
# Can be overridden with docker run command
CMD ["npx", "@upstash/context7-mcp@2.1.1"]
