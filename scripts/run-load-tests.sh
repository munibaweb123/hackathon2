#!/bin/bash

# Script to run k6 load tests for the todo application

set -e  # Exit on any error

echo "🔍 Starting load tests for Advanced Cloud Deployment..."

# Check if k6 is installed
if ! command -v k6 &> /dev/null; then
    echo "❌ k6 is not installed. Please install k6 from https://k6.io/"
    echo "For Ubuntu/Debian: sudo gpg -k https://dl.k6.io/key.gpg | sudo apt-key add -"
    echo "                  echo 'deb https://dl.k6.io/deb stable main' | sudo tee /etc/apt/sources.list.d/k6.list"
    echo "                  sudo apt-get update && sudo apt-get install k6"
    echo ""
    echo "For macOS: brew install k6"
    echo "For other systems, visit: https://k6.io/docs/get-started/installation/"
    exit 1
fi

# Check if the backend is running
BACKEND_URL=${API_URL:-"http://localhost:8000"}
echo "📡 Testing connection to backend at: $BACKEND_URL"

if ! curl -s --connect-timeout 5 "$BACKEND_URL/health" > /dev/null; then
    echo "❌ Backend is not accessible at $BACKEND_URL"
    echo "💡 Please start the backend with: cd backend && uvicorn app.main:app --reload"
    echo "   Or set API_URL environment variable to point to your running backend"
    exit 1
fi

echo "✅ Backend is accessible"

# Run the load tests
echo ""
echo "🧪 Running load tests..."
echo "📊 Test configuration:"
echo "   - Ramp-up: 2m to 50 users"
echo "   - Sustain: 5m at 50 users"
echo "   - Ramp-up: 2m to 100 users"
echo "   - Sustain: 5m at 100 users"
echo "   - Thresholds: p95 response time <500ms, failure rate <10%"
echo ""

k6 run tests/load/tasks-api.js --env API_URL="$BACKEND_URL"

TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo ""
    echo "🎉 Load tests completed successfully!"
    echo "✅ All performance thresholds met"
    echo "📈 System is ready for production deployment"
else
    echo ""
    echo "⚠️  Load tests had failures or exceeded thresholds"
    echo "🔍 Please review the test output above"
    exit $TEST_RESULT
fi