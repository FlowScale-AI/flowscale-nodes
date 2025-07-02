#!/bin/bash
# FlowScale Nodes - Quick Development Setup Script
#
# This script sets up the development environment and runs common tasks

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}FlowScale Nodes - Development Setup${NC}"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: pyproject.toml not found. Are you in the FlowScale nodes directory?${NC}"
    exit 1
fi

# Install development dependencies
echo -e "${BLUE}Installing development dependencies...${NC}"
pip install -e ".[dev]"

# Check if ruff is installed
if ! command -v ruff &> /dev/null; then
    echo -e "${YELLOW}Ruff not found, installing...${NC}"
    pip install ruff
fi

echo -e "${GREEN}✓ Development environment ready!${NC}"
echo ""

# Show available make commands
echo -e "${BLUE}Available Make commands:${NC}"
make help

echo ""
echo -e "${GREEN}Quick start:${NC}"
echo -e "  ${YELLOW}make quick${NC}     - Fix and lint files quickly"
echo -e "  ${YELLOW}make format${NC}    - Format all Python files"
echo -e "  ${YELLOW}make lint${NC}      - Check code quality"
echo -e "  ${YELLOW}make clean${NC}     - Clean build artifacts"
echo ""
echo -e "${BLUE}Happy coding! 🚀${NC}"
