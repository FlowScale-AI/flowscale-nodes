# FlowScale Nodes - Development Makefile
# 
# This Makefile provides convenient commands for development tasks including
# linting, formatting, testing, and deployment.

.PHONY: help install install-dev clean lint format check test build upload
.DEFAULT_GOAL := help

# Colors for terminal output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# UV and Python commands
PYTHON := python3
UV := uv

## Help
help: ## Show this help message
	@echo "$(BLUE)FlowScale Nodes Development Commands$(RESET)"
	@echo
	@echo "$(GREEN)Setup:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^(install|install-dev|clean):' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo
	@echo "$(GREEN)Code Quality:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^(lint|format|check|fix):' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo
	@echo "$(GREEN)Testing:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^(test|coverage):' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo
	@echo "$(GREEN)Build & Deploy:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^(build|upload|release):' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo
	@echo "$(GREEN)Utilities:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v -E '^(install|install-dev|clean|lint|format|check|fix|test|coverage|build|upload|release):' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'

## Setup Commands
install: ## Install the package and dependencies
	@echo "$(BLUE)Installing FlowScale Nodes...$(RESET)"
	$(UV) sync

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(UV) sync --dev
	@echo "$(GREEN)✓ Development environment ready!$(RESET)"

clean: ## Clean build artifacts and cache files
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@echo "$(GREEN)✓ Clean complete!$(RESET)"

uv-init: ## Initialize uv project and create lockfile
	@echo "$(BLUE)Initializing UV project...$(RESET)"
	$(UV) sync
	@echo "$(GREEN)✓ UV project initialized!$(RESET)"

uv-add: ## Add a new dependency (usage: make uv-add PACKAGE=package-name)
	@echo "$(BLUE)Adding package: $(PACKAGE)...$(RESET)"
	$(UV) add $(PACKAGE)

uv-add-dev: ## Add a new dev dependency (usage: make uv-add-dev PACKAGE=package-name)
	@echo "$(BLUE)Adding dev package: $(PACKAGE)...$(RESET)"
	$(UV) add --dev $(PACKAGE)

uv-remove: ## Remove a dependency (usage: make uv-remove PACKAGE=package-name)
	@echo "$(BLUE)Removing package: $(PACKAGE)...$(RESET)"
	$(UV) remove $(PACKAGE)

uv-lock: ## Update the lockfile
	@echo "$(BLUE)Updating lockfile...$(RESET)"
	$(UV) lock
	@echo "$(GREEN)✓ Lockfile updated!$(RESET)"

## Code Quality Commands
lint: ## Run Ruff linter
	@echo "$(BLUE)Running Ruff linter...$(RESET)"
	$(UV) run ruff check .
	@echo "$(GREEN)✓ Linting complete!$(RESET)"

format: ## Format code with Ruff formatter
	@echo "$(BLUE)Formatting code with Ruff...$(RESET)"
	$(UV) run ruff format .
	@echo "$(GREEN)✓ Code formatted!$(RESET)"

check: ## Run both linting and formatting checks (no fixes)
	@echo "$(BLUE)Running code quality checks...$(RESET)"
	$(UV) run ruff check . --diff
	$(UV) run ruff format . --diff
	@echo "$(GREEN)✓ Code quality check complete!$(RESET)"

fix: ## Auto-fix linting issues and format code
	@echo "$(BLUE)Auto-fixing issues and formatting...$(RESET)"
	$(UV) run ruff check . --fix
	$(UV) run ruff format .
	@echo "$(GREEN)✓ Auto-fix and formatting complete!$(RESET)"

## Testing Commands
test: ## Run tests (placeholder for future test suite)
	@echo "$(YELLOW)Test suite not yet implemented$(RESET)"
	@echo "$(BLUE)You can manually test nodes in ComfyUI$(RESET)"

coverage: ## Run test coverage (placeholder)
	@echo "$(YELLOW)Coverage reporting not yet implemented$(RESET)"

## Build Commands
build: clean ## Build the package
	@echo "$(BLUE)Building package...$(RESET)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Build complete! Check dist/ directory$(RESET)"

upload: build ## Upload to PyPI (requires credentials)
	@echo "$(BLUE)Uploading to PyPI...$(RESET)"
	twine upload dist/*
	@echo "$(GREEN)✓ Upload complete!$(RESET)"

release: ## Create a new release (interactive)
	@echo "$(BLUE)Creating new release...$(RESET)"
	@echo "Current version: $(shell grep version pyproject.toml | head -1 | cut -d'"' -f2)"
	@read -p "Enter new version: " version; \
	sed -i.bak "s/version = \".*\"/version = \"$$version\"/" pyproject.toml && \
	rm pyproject.toml.bak && \
	git add pyproject.toml && \
	git commit -m "Bump version to $$version" && \
	git tag "v$$version" && \
	echo "$(GREEN)✓ Version bumped to $$version$(RESET)" && \
	echo "$(YELLOW)Don't forget to: git push && git push --tags$(RESET)"

## Utility Commands
dev-setup: install-dev ## Complete development environment setup
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	pre-commit install || echo "$(YELLOW)pre-commit not available, skipping hooks setup$(RESET)"
	@echo "$(GREEN)✓ Development environment fully configured!$(RESET)"

lint-files: ## Lint specific files (usage: make lint-files FILES="path/to/file.py")
	@echo "$(BLUE)Linting specified files...$(RESET)"
	$(UV) run ruff check $(FILES)

format-files: ## Format specific files (usage: make format-files FILES="path/to/file.py")
	@echo "$(BLUE)Formatting specified files...$(RESET)"
	$(UV) run ruff format $(FILES)

api-check: ## Check API endpoints are working
	@echo "$(BLUE)Checking FlowScale API endpoints...$(RESET)"
	@echo "$(YELLOW)This requires a running ComfyUI instance$(RESET)"
	curl -s http://localhost:8188/flowscale/io/list?directory=input || echo "$(RED)API not accessible$(RESET)"

node-list: ## List all FlowScale nodes
	@echo "$(BLUE)FlowScale Node Categories:$(RESET)"
	@find . -name "*.py" -exec grep -l "CATEGORY.*FlowScale" {} \; | while read file; do \
		echo "$(GREEN)$$file:$(RESET)"; \
		grep "CATEGORY.*FlowScale" "$$file" | sed 's/.*= *"//;s/".*//' | sed 's/^/  /'; \
	done

status: ## Show git status and current branch
	@echo "$(BLUE)Repository Status:$(RESET)"
	@echo "Branch: $(GREEN)$(shell git branch --show-current)$(RESET)"
	@echo "Status:"
	@git status --short

update-deps: ## Update all dependencies to latest versions
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	$(UV) sync --upgrade
	@echo "$(GREEN)✓ Dependencies updated!$(RESET)"

# File-specific targets for common operations
utilitynodes: ## Lint and format utility nodes
	@echo "$(BLUE)Processing utility nodes...$(RESET)"
	$(UV) run ruff check utilitynodes/ --fix
	$(UV) run ruff format utilitynodes/
	@echo "$(GREEN)✓ Utility nodes processed!$(RESET)"

api: ## Lint and format API files
	@echo "$(BLUE)Processing API files...$(RESET)"
	$(UV) run ruff check api/ --fix
	$(UV) run ruff format api/
	@echo "$(GREEN)✓ API files processed!$(RESET)"

nodes: ## Lint and format all node files
	@echo "$(BLUE)Processing node files...$(RESET)"
	$(UV) run ruff check nodes/ --fix
	$(UV) run ruff format nodes/
	@echo "$(GREEN)✓ Node files processed!$(RESET)"

web: ## Lint JavaScript files (if applicable)
	@echo "$(YELLOW)JavaScript linting not yet configured$(RESET)"

# Quick development workflow
quick: fix lint ## Quick fix and lint (common workflow)
	@echo "$(GREEN)✓ Quick workflow complete!$(RESET)"

# Show current configuration
config: ## Show current Ruff configuration
	@echo "$(BLUE)Ruff Configuration:$(RESET)"
	@$(UV) run ruff check --show-settings

# Pre-commit hook simulation
pre-commit: check ## Simulate pre-commit checks
	@echo "$(BLUE)Running pre-commit simulation...$(RESET)"
	@$(MAKE) check
	@echo "$(GREEN)✓ Pre-commit checks passed!$(RESET)"
