#!/bin/bash

# Test script for Project Samarth API endpoints
# Usage: ./test_endpoints.sh [API_BASE_URL]

API_BASE=${1:-"http://localhost:8000"}
RESULTS_DIR="test_results"

echo "🌾 Testing Project Samarth API at $API_BASE"
echo "=================================================="

# Create results directory
mkdir -p $RESULTS_DIR

# Test 1: Health check
echo "1. Testing health endpoint..."
curl -s "$API_BASE/health" | jq '.' > "$RESULTS_DIR/health.json"
if [ $? -eq 0 ]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi

# Test 2: Root endpoint
echo "2. Testing root endpoint..."
curl -s "$API_BASE/" | jq '.' > "$RESULTS_DIR/root.json"
if [ $? -eq 0 ]; then
    echo "✅ Root endpoint passed"
else
    echo "❌ Root endpoint failed"
fi

# Test 3: Datasets
echo "3. Testing datasets endpoint..."
curl -s "$API_BASE/datasets" | jq '.' > "$RESULTS_DIR/datasets.json"
if [ $? -eq 0 ]; then
    echo "✅ Datasets endpoint passed"
else
    echo "❌ Datasets endpoint failed"
fi

# Test 4: Metrics
echo "4. Testing metrics endpoint..."
curl -s "$API_BASE/metrics" | jq '.' > "$RESULTS_DIR/metrics.json"
if [ $? -eq 0 ]; then
    echo "✅ Metrics endpoint passed"
else
    echo "❌ Metrics endpoint failed"
fi

# Test 5: Q&A endpoint
echo "5. Testing Q&A endpoint..."
curl -s -X POST "$API_BASE/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Compare rainfall in Maharashtra and Punjab"}' \
  | jq '.' > "$RESULTS_DIR/ask_comparison.json"

if [ $? -eq 0 ]; then
    echo "✅ Q&A comparison query passed"
else
    echo "❌ Q&A comparison query failed"
fi

# Test 6: Trend analysis
echo "6. Testing trend analysis..."
curl -s -X POST "$API_BASE/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Show rice production trend in Punjab from 2010 to 2014"}' \
  | jq '.' > "$RESULTS_DIR/ask_trend.json"

if [ $? -eq 0 ]; then
    echo "✅ Q&A trend query passed"
else
    echo "❌ Q&A trend query failed"
fi

# Test 7: Correlation analysis
echo "7. Testing correlation analysis..."
curl -s -X POST "$API_BASE/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Analyze correlation between rainfall and crop production"}' \
  | jq '.' > "$RESULTS_DIR/ask_correlation.json"

if [ $? -eq 0 ]; then
    echo "✅ Q&A correlation query passed"
else
    echo "❌ Q&A correlation query failed"
fi

# Test 8: Raw data endpoint
echo "8. Testing raw data endpoint..."
curl -s "$API_BASE/raw/agri-1" | jq '.' > "$RESULTS_DIR/raw_data.json"
if [ $? -eq 0 ]; then
    echo "✅ Raw data endpoint passed"
else
    echo "❌ Raw data endpoint failed (may be expected if dataset doesn't exist)"
fi

echo ""
echo "=================================================="
echo "✅ Test complete! Results saved to $RESULTS_DIR/"
echo "📊 Check the JSON files for detailed responses"
echo ""

# Summary
echo "📋 Test Summary:"
echo "- Health: $([ -f "$RESULTS_DIR/health.json" ] && echo "✅" || echo "❌")"
echo "- Root: $([ -f "$RESULTS_DIR/root.json" ] && echo "✅" || echo "❌")"
echo "- Datasets: $([ -f "$RESULTS_DIR/datasets.json" ] && echo "✅" || echo "❌")"
echo "- Metrics: $([ -f "$RESULTS_DIR/metrics.json" ] && echo "✅" || echo "❌")"
echo "- Q&A Comparison: $([ -f "$RESULTS_DIR/ask_comparison.json" ] && echo "✅" || echo "❌")"
echo "- Q&A Trend: $([ -f "$RESULTS_DIR/ask_trend.json" ] && echo "✅" || echo "❌")"
echo "- Q&A Correlation: $([ -f "$RESULTS_DIR/ask_correlation.json" ] && echo "✅" || echo "❌")"
echo "- Raw Data: $([ -f "$RESULTS_DIR/raw_data.json" ] && echo "✅" || echo "❌")"