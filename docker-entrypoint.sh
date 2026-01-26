#!/bin/bash
set -e

echo "🚀 Starting Linear Backend..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -p 5432 -U ${POSTGRES_USER:-linearuser}; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✅ PostgreSQL is ready!"

# Run database migrations
echo "🔄 Running Alembic migrations..."
alembic upgrade head

echo "✅ Migrations completed!"

# Create logs directory if it doesn't exist
mkdir -p /app/logs

# Start the FastAPI application
echo "🎯 Starting FastAPI application..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 4 \
    --log-level info
