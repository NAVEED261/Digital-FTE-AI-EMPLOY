#!/bin/bash
# Validation Gate Runner - Tests each tier before proceeding to next

set -e

TIER=${1:-bronze}
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)

case "$TIER" in
    bronze)
        TIER_PATH="$PROJECT_ROOT/Tier_1_Bronze"
        TIER_NAME="Bronze"
        ;;
    silver)
        TIER_PATH="$PROJECT_ROOT/Tier_2_Silver"
        TIER_NAME="Silver"
        ;;
    gold)
        TIER_PATH="$PROJECT_ROOT/Tier_3_Gold"
        TIER_NAME="Gold"
        ;;
    *)
        echo "❌ Invalid tier: $TIER"
        echo "Valid options: bronze, silver, gold"
        exit 1
        ;;
esac

echo "🔍 Running Validation Gate for $TIER_NAME Tier"
echo "=========================================="
echo ""

cd "$TIER_PATH/tests"

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -q pytest pytest-cov pytest-asyncio pytest-timeout 2>/dev/null || true

# Run tests with coverage
echo "🧪 Running tests..."
pytest -v --tb=short --cov="../src" --cov-report=term-missing 2>&1 | tee test_results.txt

# Extract test results
if grep -q "passed" test_results.txt; then
    PASSED_COUNT=$(grep -oP '\d+(?= passed)' test_results.txt | tail -1 || echo "0")
    FAILED_COUNT=$(grep -oP '\d+(?= failed)' test_results.txt | tail -1 || echo "0")
    COVERAGE=$(grep -oP '\d+%' test_results.txt | tail -1 || echo "0%")
    
    echo ""
    echo "=========================================="
    echo "📊 Test Results:"
    echo "   Passed: $PASSED_COUNT"
    echo "   Failed: $FAILED_COUNT"
    echo "   Coverage: $COVERAGE"
    echo "=========================================="
    echo ""
    
    if [ "$FAILED_COUNT" = "0" ]; then
        echo "✅ VALIDATION GATE PASSED: $TIER_NAME Tier 100% Functional"
        echo ""
        echo "You may proceed to the next tier."
        exit 0
    else
        echo "❌ VALIDATION GATE FAILED: $TIER_NAME Tier Not Ready"
        echo ""
        echo "Fix failing tests before proceeding. DO NOT continue to next tier."
        exit 1
    fi
else
    echo "❌ Test execution failed"
    exit 1
fi
