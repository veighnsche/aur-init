#!/usr/bin/env bash
set -euo pipefail

# Simple coverage runner using coverage.py
# Requires: coverage (python-coverage) and pytest

if ! command -v coverage >/dev/null 2>&1; then
  echo "coverage (python-coverage) not found. Install it, e.g.:" >&2
  echo "  pip install coverage pytest" >&2
  echo "or on Arch Linux:" >&2
  echo "  sudo pacman -S --needed python-coverage python-pytest" >&2
  exit 127
fi

# Clean previous data
rm -f .coverage

# Run tests with coverage
coverage run -m pytest "$@"

# Text report (respecting .coveragerc)
coverage report -m

# Optional HTML report
if command -v python >/dev/null 2>&1; then
  coverage html
  echo "HTML report at: htmlcov/index.html"
fi
