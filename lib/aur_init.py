#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure local lib directory is importable
LIB_DIR = Path(__file__).resolve().parent
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from cli import parse_args  # noqa: E402
from interactive import collect_interactive_inputs  # noqa: E402
from core import execute  # noqa: E402
from features import doctor  # noqa: E402


def main(argv):
    args = parse_args(argv)
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
        return execute(args)
    except KeyboardInterrupt:
        print("\nAborted by user (Ctrl+C).", file=sys.stderr)
        return 130
    except EOFError:
        print("\nAborted: input stream closed (EOF).", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
