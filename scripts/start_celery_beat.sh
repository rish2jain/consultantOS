#!/bin/bash
# Startup script for Celery Beat scheduler

set -e

echo "Starting Celery Beat for ConsultantOS..."

# Load environment variables
if [ -f .env ]; then
    echo "Loading environment from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if Redis is available
if [ -z "$REDIS_URL" ]; then
    echo "ERROR: REDIS_URL not set. Please configure in .env file."
    exit 1
fi

echo "Connecting to Redis: $REDIS_URL"

# Parse command line arguments
LOG_LEVEL=${LOG_LEVEL:-info}
SCHEDULE_FILE=${SCHEDULE_FILE:-/tmp/celerybeat-schedule}

echo "Beat Configuration:"
echo "  Log Level: $LOG_LEVEL"
echo "  Schedule File: $SCHEDULE_FILE"

# Remove stale schedule file if it exists
if [ -f "$SCHEDULE_FILE" ]; then
    echo "Removing stale schedule file..."
    rm -f "$SCHEDULE_FILE"
fi

# Graceful shutdown handler
shutdown_handler() {
    echo "Received shutdown signal. Stopping Beat scheduler..."
    kill -TERM $BEAT_PID
    wait $BEAT_PID
    echo "Beat scheduler stopped."
    exit 0
}

# Setup signal handlers
trap shutdown_handler SIGTERM SIGINT

# Start Celery Beat
echo "Starting Celery Beat scheduler..."
celery -A consultantos.jobs.celery_app beat \
    --loglevel=$LOG_LEVEL \
    --schedule=$SCHEDULE_FILE \
    --pidfile=/tmp/celerybeat.pid &

BEAT_PID=$!

echo "Celery Beat started with PID: $BEAT_PID"
echo "Scheduled tasks will run according to configuration in celery_app.py"
echo "Press Ctrl+C to stop gracefully..."

# Wait for beat process
wait $BEAT_PID
