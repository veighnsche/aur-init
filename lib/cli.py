#!/usr/bin/env python3
import argparse

def parse_args(argv):
    if not argv:
        argv = ["-h"]
    ap = argparse.ArgumentParser(
        prog="aur-init",
        description=(
            "Scaffold high-quality Arch Linux/AUR packages with minimal boilerplate.\n"
            "Generates PKGBUILD, .gitignore, README, optional language templates, and CI."
        ),
        epilog=(
            "Examples:\n"
            "  aur-init hello-go -t go --url https://example.com/hello-go --strict --srcinfo\n"
            "  aur-init hello-rs -t rust --with-man --with-completions --rust-lock\n"
            "  aur-init --doctor\n"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,
    )

    # Positional
    ap.add_argument("pkgname", nargs="?", help="Package name (AUR-compliant lowercase)" )

    # Project metadata
    meta = ap.add_argument_group("Project metadata")
    meta.add_argument("-t", "--type", dest="type", choices=["", "python", "node", "go", "cmake", "rust"], default="", help="Template type")
    meta.add_argument("-m", "--maintainer", default="vince <you@example.com>", help="Maintainer identity")
    meta.add_argument("-d", "--description", default="TODO: describe your package", help="Short package description")
    meta.add_argument("-u", "--url", default=None, help="Upstream project URL")
    meta.add_argument("-l", "--license", dest="license", default="MIT", help="License identifier")

    # VCS/source
    vcs = ap.add_argument_group("Source/VCS")
    vcs.add_argument("--vcs", choices=["", "git"], default="", help="Use a VCS package style (e.g., -git)")
    vcs.add_argument("--vcs-url", dest="vcs_url", default="", metavar="URL", help="Repository URL when --vcs is set")
    vcs.add_argument("--git-init", action="store_true", help="Initialize a git repo in the scaffolded project")

    # Features
    feats = ap.add_argument_group("Features")
    feats.add_argument("--srcinfo", dest="gen_srcinfo", action="store_true", help="Generate .SRCINFO via makepkg --printsrcinfo")
    feats.add_argument("--ci", dest="add_ci", action="store_true", help="Add GitHub Actions workflow (.SRCINFO + namcap)")
    feats.add_argument("--tests", dest="with_tests", action="store_true", help="Include minimal test scaffolding and check()")
    feats.add_argument("--with-man", dest="with_man", action="store_true", help="Scaffold a minimal man page (man/$pkgname.1)")
    feats.add_argument("--with-completions", dest="with_completions", action="store_true", help="Scaffold bash/zsh/fish completions under completions/")
    feats.add_argument("--rust-lock", dest="rust_lock", action="store_true", help="For Rust templates, generate Cargo.lock (uses cargo)")

    # Modes & UX
    ux = ap.add_argument_group("Modes & UX")
    ux.add_argument("--dry-run", dest="dry_run", action="store_true", help="Do not write; print PKGBUILD and optionally .SRCINFO")
    ux.add_argument("--strict", dest="strict", action="store_true", default=True, help="Enable strict validations (fail on missing metadata)")
    ux.add_argument("--no-strict", dest="strict", action="store_false", help="Relax validations (allow some defaults)")
    ux.add_argument("--explain", dest="explain", action="store_true", help="Print short hints for PKGBUILD fields with ArchWiki links")
    ux.add_argument("--doctor", dest="doctor", action="store_true", help="Check local prerequisites: makepkg, fakeroot, git, namcap")
    ux.add_argument("-f", "--force", action="store_true", help="Overwrite an existing non-empty target directory")
    ux.add_argument("-i", "--interactive", action="store_true", help="Run an interactive form to choose options")
    ux.add_argument("--from-file", dest="from_file", default=None, metavar="PATH", help="Load default preferences from a TOML/JSON file")

    return ap.parse_args(argv)


