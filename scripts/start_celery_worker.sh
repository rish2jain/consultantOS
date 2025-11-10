#!/bin/bash
# Startup script for Celery worker

set -e

echo "Starting Celery Worker for ConsultantOS..."

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
CONCURRENCY=${CONCURRENCY:-4}
LOG_LEVEL=${LOG_LEVEL:-info}
MAX_TASKS_PER_CHILD=${MAX_TASKS_PER_CHILD:-1000}
QUEUES=${QUEUES:-critical,high,normal,low}

echo "Worker Configuration:"
echo "  Concurrency: $CONCURRENCY"
echo "  Log Level: $LOG_LEVEL"
echo "  Max Tasks Per Child: $MAX_TASKS_PER_CHILD"
echo "  Queues: $QUEUES"

# Setup monitoring signal handlers
setup_monitoring() {
    echo "Setting up Celery monitoring..."
    # Initialize Prometheus metrics if enabled
    if [ "$ENABLE_METRICS" = "true" ]; then
        echo "Prometheus metrics enabled on port ${METRICS_PORT:-9090}"
    fi
}

# Graceful shutdown handler
shutdown_handler() {
    echo "Received shutdown signal. Gracefully stopping worker..."
    # Celery will wait for running tasks to complete
    kill -TERM $WORKER_PID
    wait $WORKER_PID
    echo "Worker stopped."
    exit 0
}

# Setup signal handlers
trap shutdown_handler SIGTERM SIGINT

# Setup monitoring
setup_monitoring

# Start Celery worker
echo "Starting Celery worker..."
celery -A consultantos.jobs.celery_app worker \
    --loglevel=$LOG_LEVEL \
    --concurrency=$CONCURRENCY \
    --max-tasks-per-child=$MAX_TASKS_PER_CHILD \
    --queues=$QUEUES \
    --time-limit=300 \
    --soft-time-limit=270 \
    --prefetch-multiplier=1 \
    --without-gossip \
    --without-mingle \
    --without-heartbeat &

WORKER_PID=$!

echo "Celery worker started with PID: $WORKER_PID"
echo "Access Flower UI at: http://localhost:5555"
echo "Press Ctrl+C to stop gracefully..."

# Wait for worker process
wait $WORKER_PID
