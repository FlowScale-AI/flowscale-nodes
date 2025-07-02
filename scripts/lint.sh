#!/bin/bash
# Ruff linting and formatting script for FlowScale Nodes

echo "🔍 Running Ruff linter..."
ruff check .

echo "🎨 Running Ruff formatter..."
ruff format .

echo "✅ Linting and formatting complete!"

# Check if there are any remaining issues
if ruff check . --quiet; then
    echo "✨ All checks passed!"
else
    echo "⚠️  Some issues remain. Please review the output above."
    exit 1
fi
