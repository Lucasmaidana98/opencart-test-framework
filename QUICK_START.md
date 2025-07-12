# Quick Start Guide

**Get the OpenCart Test Framework running in 5 minutes**

## Prerequisites

- Python 3.9 or higher
- Git
- Chrome/Firefox/Edge browser
- 4GB RAM minimum

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/opencart-test-framework.git
cd opencart-test-framework
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Validate Framework
```bash
python test_framework_structure.py
```

## Running Tests

### Basic Test Execution
```bash
# Run user registration tests
pytest tests/frontend/test_user_registration.py -v

# Run shopping cart tests  
pytest tests/frontend/test_shopping_cart.py -v

# Run all frontend tests
pytest tests/frontend/ -v
```

### Parallel Execution
```bash
# Run with automatic parallelization
pytest -n auto tests/frontend/

# Run with specific number of workers
pytest -n 4 tests/frontend/
```

### Generate Reports
```bash
# HTML report
pytest --html=reports/report.html --self-contained-html

# JSON report for CI/CD
pytest --json-report --json-report-file=reports/report.json
```

## Configuration

### Browser Selection
```bash
# Chrome (default)
pytest tests/ --browser=chrome

# Firefox
pytest tests/ --browser=firefox

# Edge  
pytest tests/ --browser=edge
```

### Environment Configuration
```bash
# Local environment (default)
pytest tests/ --environment=LOCAL

# Docker environment
pytest tests/ --environment=DOCKER
```

### Headless Execution
```bash
pytest tests/ --headless
```

## Test Matrix Generation

```bash
# Generate test matrix for CI/CD
python scripts/generate_test_matrix.py --test-suite=frontend --browser=chrome

# Generate cross-browser matrix
python scripts/generate_test_matrix.py --test-suite=all --browser=all --max-parallel=20
```

## CI/CD Pipeline

The GitHub Actions pipeline automatically runs:
- On push to main/develop branches
- On pull request creation
- Daily scheduled runs
- Manual workflow dispatch

### Pipeline Features
- 20 parallel jobs for maximum speed
- Cross-browser testing
- Automatic report generation
- Failure notifications

## Troubleshooting

### Common Issues

**WebDriver Issues:**
```bash
# Clear WebDriver cache
rm -rf ~/.wdm/

# Reinstall webdriver-manager
pip uninstall webdriver-manager
pip install webdriver-manager
```

**Permission Issues:**
```bash
# On Linux/Mac, ensure execute permissions
chmod +x scripts/*.py
```

**Memory Issues:**
```bash
# Reduce parallel workers
pytest -n 2 tests/
```

### Getting Help

- Check the [full documentation](docs/)
- Review [troubleshooting guide](docs/TROUBLESHOOTING.md)
- Open an issue on GitHub

## Next Steps

1. **Explore the codebase** - Start with `pages/` and `tests/` directories
2. **Read the documentation** - Check `docs/PROJECT_OVERVIEW.md`
3. **Understand parallelism** - Review `docs/PARALLELISM_STRATEGY.md`
4. **Customize configuration** - Modify `config/settings.py`
5. **Add new tests** - Follow the existing patterns

## Key Files

- `conftest.py` - pytest configuration and fixtures
- `pytest.ini` - pytest settings and markers
- `config/settings.py` - framework configuration
- `utils/driver_manager.py` - WebDriver management
- `pages/base_page.py` - base page object functionality

**Ready to explore the framework? Start with the test files in `tests/frontend/` to see the framework in action!**