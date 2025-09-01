#!/usr/bin/env python3
import sys


def collect_interactive_inputs(args):
    """
    Prompt the user for inputs interactively, using current args as defaults.
    If the optional 'questionary' package is available, use it for nicer prompts.
    Otherwise, fall back to stdlib input()-based prompts so no extra deps are required.
    """
    # Helper fallbacks
    def _err(msg: str):
        print(msg, file=sys.stderr)

    def _input_text(prompt, default=None):
        suffix = f" [{default}]" if default is not None and default != "" else ""
        val = input(f"{prompt}{suffix}: ").strip()
        return val if val != "" else (default or "")

    def _input_confirm(prompt, default=False):
        d = "Y/n" if default else "y/N"
        val = input(f"{prompt} ({d}): ").strip().lower()
        if val in ("y", "yes"):
            return True
        if val in ("n", "no"):
            return False
        return bool(default)

    def _input_select(prompt, choices, default=None):
        # Simple numeric menu
        print(f"{prompt}:")
        for idx, ch in enumerate(choices, start=1):
            mark = " (default)" if default is not None and ch == default else ""
            print(f"  {idx}. {ch}{mark}")
        while True:
            raw = input("Choose number: ").strip()
            if raw == "" and default is not None:
                return default
            if raw.isdigit():
                i = int(raw)
                if 1 <= i <= len(choices):
                    return choices[i - 1]
            print("Invalid selection, try again.")

    # Try to use questionary if present
    try:
        import questionary  # type: ignore
        use_q = True
    except Exception:
        questionary = None  # type: ignore
        use_q = False

    # Unified adapters
    def ask_text(prompt: str, default: str = "") -> str:
        if use_q:
            res = questionary.text(prompt, default=(default or "")).ask()
            if res is None:
                raise KeyboardInterrupt
            return res
        return _input_text(prompt, default=(default or ""))

    def ask_confirm(prompt: str, default: bool = False) -> bool:
        if use_q:
            res = questionary.confirm(prompt, default=bool(default)).ask()
            if res is None:
                raise KeyboardInterrupt
            return bool(res)
        return bool(_input_confirm(prompt, default=bool(default)))

    def ask_select(prompt: str, choices: list[str], default: str | None = None):
        if use_q:
            res = questionary.select(prompt, choices=choices, default=(default or choices[0] if choices else None)).ask()
            if res is None:
                raise KeyboardInterrupt
            return res
        return _input_select(prompt, choices=choices, default=default)

    try:
        # Choose interaction depth first
        mode = ask_select("Mode", choices=["Simple", "Advanced"], default="Simple")
        advanced = (mode == "Advanced")

        # pkgname next, as other defaults may depend on it
        pkgname = ask_text("Package name (pkgname)", default=(args.pkgname or ""))
        if not pkgname:
            _err("Error: pkgname is required.")
            sys.exit(2)

        type_choices = ["", "python", "node", "go", "cmake", "rust"]
        type_choice = ask_select("Project type", choices=type_choices, default=(args.type or ""))

        maintainer = ask_text("Maintainer", default=(args.maintainer or "vince <you@example.com>"))
        description = ask_text("Description", default=(args.description or "TODO: describe your package"))

        default_url = args.url or f"https://example.com/{pkgname}"
        url = ask_text("Project URL", default=default_url)
        license_ = ask_text("License", default=(args.license or "MIT"))

        vcs_choices = ["", "git"]
        vcs = ask_select("VCS", choices=vcs_choices, default=(args.vcs or ""))

        vcs_url = args.vcs_url
        if vcs == "git":
            vcs_url = ask_text("VCS URL (required for git)", default=(args.vcs_url or ""))
            if not vcs_url:
                _err("Error: --vcs-url is required when --vcs is 'git'.")
                sys.exit(2)

        # Simple prompts (always ask)
        git_init = ask_confirm("Initialize git repo?", default=bool(args.git_init))
        with_tests = ask_confirm("Include test scaffolding?", default=bool(args.with_tests))

        # Advanced prompts (optional)
        if advanced:
            gen_srcinfo = ask_confirm("Generate .SRCINFO?", default=bool(args.gen_srcinfo))
            add_ci = ask_confirm("Add CI workflow?", default=bool(args.add_ci))
            if type_choice:
                with_man = ask_confirm("Scaffold a minimal man page?", default=bool(getattr(args, "with_man", False)))
                with_compl = ask_confirm("Scaffold shell completions (bash/zsh/fish)?", default=bool(getattr(args, "with_completions", False)))
            else:
                with_man = False
                with_compl = False
            if type_choice == "rust":
                rust_lock = ask_confirm("For Rust, generate Cargo.lock (requires cargo)?", default=bool(getattr(args, "rust_lock", False)))
            else:
                rust_lock = False
            dry_run = ask_confirm("Dry-run (print PKGBUILD/.SRCINFO only)?", default=bool(getattr(args, "dry_run", False)))
            strict = ask_confirm("Strict mode (fail on missing metadata)?", default=bool(getattr(args, "strict", True)))
            explain = ask_confirm("Explain mode (print short hints with links)?", default=bool(getattr(args, "explain", False)))
            doctor_flag = ask_confirm("Run doctor (check prerequisites) instead of scaffolding?", default=bool(getattr(args, "doctor", False)))
            force = ask_confirm("Overwrite non-empty target directory?", default=bool(args.force))
        else:
            # Defaults in simple mode (no prompts): keep current CLI defaults
            gen_srcinfo = bool(getattr(args, "gen_srcinfo", False))
            add_ci = bool(getattr(args, "add_ci", False))
            with_man = False
            with_compl = False
            rust_lock = False if type_choice != "rust" else bool(getattr(args, "rust_lock", False))
            dry_run = bool(getattr(args, "dry_run", False))
            strict = bool(getattr(args, "strict", True))
            explain = bool(getattr(args, "explain", False))
            doctor_flag = bool(getattr(args, "doctor", False))
            force = bool(args.force)

        # Update args
        args.pkgname = pkgname
        args.type = type_choice
        args.maintainer = maintainer
        args.description = description
        args.url = url or None  # Treat empty string as None so existing fallback applies later
        args.license = license_
        args.vcs = vcs
        args.vcs_url = vcs_url or ""
        args.git_init = bool(git_init)
        args.gen_srcinfo = bool(gen_srcinfo)
        args.add_ci = bool(add_ci)
        args.with_tests = bool(with_tests)
        args.with_man = bool(with_man)
        args.with_completions = bool(with_compl)
        args.rust_lock = bool(rust_lock)
        args.dry_run = bool(dry_run)
        args.strict = bool(strict)
        args.explain = bool(explain)
        args.doctor = bool(doctor_flag)
        args.force = bool(force)
        return args
    except KeyboardInterrupt:
        _err("\nAborted by user (Ctrl+C). No files were created.")
        sys.exit(130)
    except EOFError:
        _err("\nAborted: input stream closed (EOF).")
        sys.exit(130)
