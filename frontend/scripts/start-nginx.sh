#!/bin/sh
# Nginx startup script for production

set -e

echo "Starting TeamFlow Frontend..."

# Substitute environment variables in nginx config if needed
if [ -n "$API_BASE_URL" ]; then
    echo "Configuring API base URL: $API_BASE_URL"
    # Add environment variable substitution if needed
fi

# Start nginx
echo "Starting Nginx..."
exec nginx -g 'daemon off;'