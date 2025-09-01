#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from typing import Any, Dict, Tuple
from pathlib import Path

# Ensure local lib directory is importable
LIB_DIR = Path(__file__).resolve().parent
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from cli import parse_args  # noqa: E402
from interactive import collect_interactive_inputs  # noqa: E402
from core import execute  # noqa: E402
from features import doctor  # noqa: E402


# --- Profile loading utilities ---

def _load_profile(from_file: str | None) -> Tuple[str | None, Dict[str, Any]]:
    """Load a preferences profile from a provided path or default XDG locations.
    Supports TOML (.toml) and JSON (.json). Returns (path, data) or (None, {}).
    """
    candidates: list[Path] = []
    if from_file:
        candidates.append(Path(from_file).expanduser())
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME")
        if xdg:
            candidates.append(Path(xdg) / "aur-init" / "config.toml")
            candidates.append(Path(xdg) / "aur-init" / "config.json")
        home = Path.home() / ".config" / "aur-init"
        candidates.append(home / "config.toml")
        candidates.append(home / "config.json")

    for p in candidates:
        try:
            if p.is_file():
                if p.suffix.lower() == ".toml":
                    try:
                        import tomllib  # Python 3.11+
                    except Exception:
                        print(f"Warning: cannot read TOML without tomllib: {p}", file=sys.stderr)
                        return (None, {})
                    with p.open("rb") as f:
                        data = tomllib.load(f)
                    return (str(p), data)
                elif p.suffix.lower() == ".json":
                    import json

                    with p.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                    return (str(p), data)
        except Exception as e:
            print(f"Warning: failed to load profile {p}: {e}", file=sys.stderr)
            return (None, {})
    return (None, {})


def _apply_profile_defaults(args: Any, profile: Dict[str, Any]) -> None:
    """Apply profile values to args only when args currently hold parser defaults.
    This preserves CLI overrides. Also attach derived fields like url_base.
    """
    # Known parser defaults (must match lib/cli.py)
    defaults: Dict[str, Any] = {
        "type": "",
        "maintainer": "vince <you@example.com>",
        "description": "TODO: describe your package",
        "url": None,
        "license": "MIT",
        "vcs": "",
        "vcs_url": "",
        "git_init": False,
        "gen_srcinfo": False,
        "add_ci": False,
        "with_tests": False,
        "with_man": False,
        "with_completions": False,
        "rust_lock": False,
        "dry_run": False,
        "strict": True,
        "explain": False,
        "doctor": False,
        "force": False,
    }

    # Simple copy helper: set only if current equals default
    def set_if_default(attr: str, value: Any):
        if not hasattr(args, attr):
            return
        current = getattr(args, attr)
        if attr in defaults and current == defaults[attr]:
            setattr(args, attr, value)

    # Flat keys
    for key, val in profile.items():
        if key in ("rust",):
            continue
        if key == "url_base":
            # Not a CLI arg; attach as helper for interactive defaults
            setattr(args, "url_base", str(val))
            continue
        set_if_default(key, val)

    # Nested rust options
    rust_section = profile.get("rust")
    if isinstance(rust_section, dict) and hasattr(args, "type") and args.type == "rust":
        if "rust_lock" in rust_section:
            set_if_default("rust_lock", bool(rust_section["rust_lock"]))


def main(argv):
    args = parse_args(argv)
    # Load preferences profile (from flag or default paths) and merge into args
    profile_path, profile = _load_profile(getattr(args, "from_file", None))
    if profile:
        _apply_profile_defaults(args, profile)
    if getattr(args, "doctor", False):
        return doctor()
    # Interactive mode handling and required-field validation
    try:
        if getattr(args, "interactive", False):
            if not sys.stdin.isatty():
                print("--interactive requires a TTY. Run in a terminal or omit --interactive.", file=sys.stderr)
                return 2
            args = collect_interactive_inputs(args)
            # If user chose doctor interactively, run it now
            if getattr(args, "doctor", False):
                return doctor()
        elif not args.pkgname:
            print("pkgname is required. Provide it positionally or use --interactive.", file=sys.stderr)
            return 2
        # Emit a concise summary before scaffolding (avoid on doctor/dry-run)
        if not getattr(args, "doctor", False) and not getattr(args, "dry_run", False):
            parts = [
                f"Scaffolding {args.pkgname}",
                f"type={args.type or 'generic'}",
                f"vcs={args.vcs or 'none'}",
            ]
            if profile_path:
                parts.append(f"profile={profile_path}")
            # Feature switches (only show enabled)
            if getattr(args, "git_init", False):
                parts.append("git-init")
            if getattr(args, "with_tests", False):
                parts.append("tests")
            if getattr(args, "gen_srcinfo", False):
                parts.append("srcinfo")
            if getattr(args, "add_ci", False):
                parts.append("ci")
            if getattr(args, "with_man", False):
                parts.append("man")
            if getattr(args, "with_completions", False):
                parts.append("completions")
            if getattr(args, "rust_lock", False):
                parts.append("rust-lock")
            if getattr(args, "force", False):
                parts.append("force")
            # Policy flags
            parts.append("strict" if getattr(args, "strict", True) else "no-strict")
            print("[aur-init] " + " ".join(parts), file=sys.stderr)
        return execute(args)
    except KeyboardInterrupt:
        print("\nAborted by user (Ctrl+C).", file=sys.stderr)
        return 130
    except EOFError:
        print("\nAborted: input stream closed (EOF).", file=sys.stderr)
        return 130



if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
