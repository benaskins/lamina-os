FROM nginx:alpine

# Copy the generated configuration
COPY nginx-unified.conf /etc/nginx/nginx.conf

# Create necessary directories
RUN mkdir -p /var/cache/nginx /var/log/nginx

# Set proper permissions
RUN chown -R nginx:nginx /var/cache/nginx /var/log/nginx

EXPOSE 443 8000 11434 3100 8001

CMD ["nginx", "-g", "daemon off;"]
