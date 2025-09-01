#!/usr/bin/env bash
set -euo pipefail

# Dedicated smoke workspace under repo root
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
AURINIT_BIN=${1:-"$ROOT_DIR/aur-init"}
SMOKE_DIR="$ROOT_DIR/.smoke"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

if [[ ! -x "$AURINIT_BIN" ]]; then
  echo "aur-init not found or not executable: $AURINIT_BIN" >&2
  exit 1
fi

mkdir -p "$SMOKE_DIR"
cd "$SMOKE_DIR"

declare -a types=( "" python node go cmake rust )
status=0

for t in "${types[@]}"; do
  name="smoke-${t:-minimal}-$TIMESTAMP"
  cmd=("$AURINIT_BIN")
  [[ -n "$t" ]] && cmd+=(--type "$t")
  cmd+=("$name")
  echo "[SMOKE] Generating: ${cmd[*]}"
  if ! "${cmd[@]}"; then
    echo "[SMOKE] Generation failed for $name" >&2
    status=1
    continue
  fi
  pushd "$name" >/dev/null
  # Local source validation: ensure files in source=() exist (ignores VCS/URLs)
  if [[ -f PKGBUILD ]]; then
    echo "[SMOKE] validate local sources in PKGBUILD"
    mapfile -t SRC_LINES < <(awk '/^source=\(/, /^\)/ {print}' PKGBUILD)
    SRC_JOINED=$(printf '%s' "${SRC_LINES[@]}")
    # Strip leading 'source=(' and trailing ')', split on spaces
    SRC_CONTENT=${SRC_JOINED#*source=(}
    SRC_CONTENT=${SRC_CONTENT%)*}
    # Iterate tokens
    err=0
    while read -r tok; do
      [[ -z "$tok" ]] && continue
      tok=${tok#\'}; tok=${tok%\'}
      if [[ "$tok" == *://* || "$tok" == *::* ]]; then
        continue
      fi
      if [[ ! -f "$tok" ]]; then
        echo "[SMOKE] missing local source: $tok" >&2
        err=1
      fi
    done < <(tr ' ' '\n' <<<"$SRC_CONTENT")
    if [[ $err -ne 0 ]]; then
      status=1
    fi
  fi

  # Optional makepkg verification if explicitly enabled
  if [[ "${SMOKE_USE_MAKEPKG:-0}" == 1 ]]; then
    if command -v makepkg >/dev/null 2>&1; then
      echo "[SMOKE] makepkg --verifysource"
      if ! makepkg -f --verifysource >/dev/null; then
        echo "[SMOKE] makepkg --verifysource failed for $name" >&2
        status=1
      fi
    else
      echo "[SMOKE] makepkg not available; skipping build check"
    fi
  fi
  popd >/dev/null
  echo "[SMOKE] OK: $name"
  echo
done

echo "[SMOKE] Artifacts in: $SMOKE_DIR"
exit $status
