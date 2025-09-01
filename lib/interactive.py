#!/usr/bin/env python3
import sys


def collect_interactive_inputs(args):
    """
    Prompt the user for inputs interactively, using current args as defaults.
    If the optional 'questionary' package is available, use it for nicer prompts.
    Otherwise, fall back to stdlib input()-based prompts so no extra deps are required.
    """
    # Helper fallbacks
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

    # pkgname first, as other defaults may depend on it
    if use_q:
        pkgname = questionary.text("Package name (pkgname)", default=(args.pkgname or "")).ask()
    else:
        pkgname = _input_text("Package name (pkgname)", default=(args.pkgname or ""))
    if not pkgname:
        print("pkgname is required", file=sys.stderr)
        sys.exit(2)

    type_choices = ["", "python", "node", "go", "cmake", "rust"]
    if use_q:
        type_choice = questionary.select(
            "Project type", choices=type_choices, default=(args.type or "")
        ).ask()
    else:
        type_choice = _input_select("Project type", choices=type_choices, default=(args.type or ""))

    if use_q:
        maintainer = questionary.text("Maintainer", default=(args.maintainer or "vince <you@example.com>")).ask()
        description = questionary.text("Description", default=(args.description or "TODO: describe your package")).ask()
    else:
        maintainer = _input_text("Maintainer", default=(args.maintainer or "vince <you@example.com>"))
        description = _input_text("Description", default=(args.description or "TODO: describe your package"))

    default_url = args.url or f"https://example.com/{pkgname}"
    if use_q:
        url = questionary.text("Project URL", default=default_url).ask()
        license_ = questionary.text("License", default=(args.license or "MIT")).ask()
    else:
        url = _input_text("Project URL", default=default_url)
        license_ = _input_text("License", default=(args.license or "MIT"))

    vcs_choices = ["", "git"]
    if use_q:
        vcs = questionary.select("VCS", choices=vcs_choices, default=(args.vcs or "")).ask()
    else:
        vcs = _input_select("VCS", choices=vcs_choices, default=(args.vcs or ""))

    vcs_url = args.vcs_url
    if vcs == "git":
        if use_q:
            vcs_url = questionary.text("VCS URL (required for git)", default=(args.vcs_url or "")).ask()
        else:
            vcs_url = _input_text("VCS URL (required for git)", default=(args.vcs_url or ""))
        if not vcs_url:
            print("--vcs-url is required when --vcs is 'git'", file=sys.stderr)
            sys.exit(2)

    if use_q:
        git_init = questionary.confirm("Initialize git repo?", default=bool(args.git_init)).ask()
        gen_srcinfo = questionary.confirm("Generate .SRCINFO?", default=bool(args.gen_srcinfo)).ask()
        add_ci = questionary.confirm("Add CI workflow?", default=bool(args.add_ci)).ask()
        with_tests = questionary.confirm("Include test scaffolding?", default=bool(args.with_tests)).ask()
        with_man = questionary.confirm("Scaffold a minimal man page?", default=bool(getattr(args, "with_man", False))).ask()
        with_compl = questionary.confirm("Scaffold shell completions (bash/zsh/fish)?", default=bool(getattr(args, "with_completions", False))).ask()
        rust_lock = questionary.confirm("For Rust, generate Cargo.lock (requires cargo)?", default=bool(getattr(args, "rust_lock", False))).ask()
        dry_run = questionary.confirm("Dry-run (print PKGBUILD/.SRCINFO only)?", default=bool(getattr(args, "dry_run", False))).ask()
        strict = questionary.confirm("Strict mode (fail on missing metadata)?", default=bool(getattr(args, "strict", True))).ask()
        explain = questionary.confirm("Explain mode (print short hints with links)?", default=bool(getattr(args, "explain", False))).ask()
        doctor_flag = questionary.confirm("Run doctor (check prerequisites) instead of scaffolding?", default=bool(getattr(args, "doctor", False))).ask()
        force = questionary.confirm("Overwrite non-empty target directory?", default=bool(args.force)).ask()
    else:
        git_init = _input_confirm("Initialize git repo?", default=bool(args.git_init))
        gen_srcinfo = _input_confirm("Generate .SRCINFO?", default=bool(args.gen_srcinfo))
        add_ci = _input_confirm("Add CI workflow?", default=bool(args.add_ci))
        with_tests = _input_confirm("Include test scaffolding?", default=bool(args.with_tests))
        with_man = _input_confirm("Scaffold a minimal man page?", default=bool(getattr(args, "with_man", False)))
        with_compl = _input_confirm("Scaffold shell completions (bash/zsh/fish)?", default=bool(getattr(args, "with_completions", False)))
        rust_lock = _input_confirm("For Rust, generate Cargo.lock (requires cargo)?", default=bool(getattr(args, "rust_lock", False)))
        dry_run = _input_confirm("Dry-run (print PKGBUILD/.SRCINFO only)?", default=bool(getattr(args, "dry_run", False)))
        strict = _input_confirm("Strict mode (fail on missing metadata)?", default=bool(getattr(args, "strict", True)))
        explain = _input_confirm("Explain mode (print short hints with links)?", default=bool(getattr(args, "explain", False)))
        doctor_flag = _input_confirm("Run doctor (check prerequisites) instead of scaffolding)?", default=bool(getattr(args, "doctor", False)))
        force = _input_confirm("Overwrite non-empty target directory?", default=bool(args.force))

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
