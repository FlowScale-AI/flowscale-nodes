# Development Environment Setup with Ruff and Makefile

## 🚀 **Quick Start**

1. **Setup development environment:**
   ```bash
   ./scripts/setup-dev.sh
   ```

2. **Or manually:**
   ```bash
   pip install -e ".[dev]"
   make help
   ```

## 📋 **Available Commands**

### **Code Quality**
```bash
make lint          # Check code quality
make format        # Format all Python files
make check         # Check without making changes
make fix           # Auto-fix issues and format
make quick         # Quick workflow (fix + lint)
```

### **File-Specific Commands**
```bash
make utilitynodes  # Process utility nodes
make api           # Process API files
make nodes         # Process all node files

# Target specific files
make lint-files FILES="path/to/file.py"
make format-files FILES="path/to/file.py"
```

### **Project Management**
```bash
make clean         # Clean build artifacts
make build         # Build the package
make status        # Show git status
make config        # Show Ruff configuration
```

## ⚙️ **Ruff Configuration**

The project uses Ruff for both linting and formatting, configured in `pyproject.toml`:

### **Enabled Rules:**
- **E/W**: pycodestyle errors and warnings
- **F**: Pyflakes (undefined names, imports, etc.)
- **UP**: pyupgrade (modern Python syntax)
- **B**: flake8-bugbear (likely bugs and design problems)
- **SIM**: flake8-simplify (simplification suggestions)
- **I**: isort (import sorting)
- **C90**: mccabe (complexity analysis)

### **Key Settings:**
- **Line length**: 100 characters
- **Target Python**: 3.8+
- **Quote style**: Double quotes
- **Indentation**: 4 spaces
- **Max complexity**: 10

## 🔧 **Integration with IDEs**

### **VS Code**
Add to your `.vscode/settings.json`:
```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    },
    "ruff.lint.args": ["--config=pyproject.toml"],
    "ruff.format.args": ["--config=pyproject.toml"]
}
```

### **Pre-commit Hooks**
Install pre-commit hooks (optional):
```bash
pip install pre-commit
pre-commit install
```

## 📁 **Project Structure**

```
flowscale-nodes/
├── pyproject.toml          # Main configuration
├── Makefile               # Development commands
├── scripts/
│   └── setup-dev.sh       # Quick setup script
├── api/                   # API endpoints
├── nodes/                 # Core node implementations
├── utilitynodes/          # Utility nodes
└── web/                   # Frontend assets
```

## 🎯 **Common Workflows**

### **Daily Development**
```bash
# Before committing
make quick

# Fix specific files
make fix FILES="path/to/changed/file.py"

# Check everything
make check
```

### **Code Review Preparation**
```bash
make clean
make fix
make lint
make status
```

### **CI/CD Integration**
```bash
# In CI pipeline
make check  # Fails if code needs formatting/fixing
```

## 🔍 **Understanding Ruff Output**

Ruff provides detailed error codes and suggestions:

- **Format violations**: Automatically fixed with `make format`
- **Import issues**: Fixed with `ruff check --fix`
- **Code quality**: Suggestions for improvement
- **Complexity warnings**: Code that might be too complex

## 📊 **Performance Benefits**

Ruff is significantly faster than traditional tools:
- **~100x faster** than flake8
- **~30x faster** than black
- **Single tool** replaces multiple linters
- **Rust-powered** for maximum performance

## 🛠️ **Customization**

To modify linting rules, edit `pyproject.toml`:

```toml
[tool.ruff.lint]
# Add or remove rules
select = ["E", "W", "F", "UP", "B", "SIM", "I", "C90"]
ignore = ["E501"]  # Ignore specific rules

# Per-file customization
[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py
```

## 🔧 **Troubleshooting**

### **Ruff not found**
```bash
pip install ruff
# or
make install-dev
```

### **Configuration not loading**
```bash
make config  # Check current settings
```

### **Conflicts with existing tools**
Ruff can replace:
- black → `ruff format`
- isort → `ruff check --select I`
- flake8 → `ruff check`
- pyupgrade → `ruff check --select UP`

Just remove the old tools and use Ruff!

Happy coding! 🎉
