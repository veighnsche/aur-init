#!/usr/bin/env bash
set -euo pipefail

# Remove generated smoke projects from the .smoke/ folder.
# Usage: scripts/smoke/clean.sh [pattern]
# If pattern provided, only removes matching directories.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
SMOKE_DIR="$ROOT_DIR/.smoke"
PATTERN=${1:-"smoke-*"}

if [[ ! -d "$SMOKE_DIR" ]]; then
  echo "No .smoke directory to clean."
  exit 0
fi

shopt -s nullglob
cd "$SMOKE_DIR"

declare -a targets=( $PATTERN )
if [[ ${#targets[@]} -eq 0 ]]; then
  echo "No targets matching pattern '$PATTERN' in $SMOKE_DIR"
  exit 0
fi

echo "Cleaning ${#targets[@]} directories in $SMOKE_DIR matching: $PATTERN"
for d in "${targets[@]}"; do
  if [[ -d "$d" ]]; then
    echo "  rm -rf $d"
    rm -rf -- "$d"
  fi
done

echo "Done."
