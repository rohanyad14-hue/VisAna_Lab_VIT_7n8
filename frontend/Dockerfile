# Production Dockerfile for Frontend Dashboard using Nginx Alpine
FROM nginx:1.25-alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy web assets
COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/

EXPOSE 80

# Health check using IPv4 loopback
HEALTHCHECK --interval=10s --timeout=3s --start-period=3s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
