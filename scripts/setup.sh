·#!/bin/bash
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Check if Python 3 is available
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required but not installed."
  echo "Please install Python 3.10+ first:"
  echo "  brew install python@3.12"
  echo "  or"
  echo "  pyenv install 3.12.7 && pyenv local 3.12.7"
  exit 1
fi

# Check if Poetry is available
if ! command -v poetry >/dev/null 2>&1; then
  echo "Poetry is required but not installed."
  echo "Please install Poetry first:"
  echo "  curl -sSL https://install.python-poetry.org | python3 -"
  exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ $(echo "$PYTHON_VERSION < 3.10" | bc -l) -eq 1 ]]; then
  echo "Python 3.10+ is required, but found Python $PYTHON_VERSION"
  exit 1
fi

echo "Using Python $PYTHON_VERSION"

# Remove existing virtual environment
if [ -d ".venv" ]; then
  echo "Removing existing .venv directory..."
  rm -rf .venv
fi

# Create virtual environment with standard venv
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Configure Poetry to use the existing venv
echo "Configuring Poetry to use .venv..."
poetry config virtualenvs.in-project true
poetry config virtualenvs.path .

# Install dependencies with Poetry
echo "Installing dependencies with Poetry..."
poetry install --no-root --extras cpu

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run tests:"
echo "  python test.py"
echo ""
echo "To convert examples:"
echo "  python scripts/convert_examples.py --remove-top-level-bullets"