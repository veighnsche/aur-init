#!/usr/bin/env python3
import sys
from pathlib import Path

from render import (
    find_templates_dir,
    render_template,
    compute_arch_line,
    join_single_quoted,
    compute_source_and_sha,
    build_block,
    check_block,
    package_block,
    pkgver_block,
)
from scaffold import (
    ensure_dir,
    write_file,
    scaffold_common_files,
    scaffold_template,
    maybe_scaffold_tests,
)
from features import (
    maybe_git_init,
    maybe_gen_srcinfo,
    maybe_add_ci,
)


def execute(args) -> int:
    """Run the main aur-init workflow using fully prepared args.

    Exits early with non-zero codes on validation errors. Returns 0 on success.
    """
    pkgname = args.pkgname
    t = args.type
    vcs = args.vcs
    vcs_url = args.vcs_url

    # Basic pkgname validation (letters, digits, @._+-)
    import re
    if not re.fullmatch(r"[a-z0-9@._+-][a-z0-9@._+\-]*", pkgname):
        print("Invalid pkgname: only lowercase letters, digits and @._+- are allowed", file=sys.stderr)
        return 2

    target = Path.cwd() / pkgname
    if target.exists() and any(target.iterdir()) and not args.force:
        print(f"Target directory '{pkgname}' exists and is not empty. Use --force to overwrite.", file=sys.stderr)
        return 1

    ensure_dir(target)

    maintainer = args.maintainer
    pkgdesc = args.description
    pkgurl = args.url or f"https://example.com/{pkgname}"
    pkglicense = args.license

    depends: list[str] = []
    makedepends: list[str] = []
    local_sources: list[str] = []

    if t == "python":
        depends.append("python")
        if not vcs:
            local_sources += [f"bin/{pkgname}", f"src/{pkgname}/main.py"]
    elif t == "node":
        depends.append("nodejs")
        if not vcs:
            local_sources += [f"bin/{pkgname}", "src/main.js"]
    elif t == "go":
        makedepends.append("go")
        if not vcs:
            local_sources += ["main.go"]
    elif t == "cmake":
        makedepends += ["cmake", "make", "gcc"]
        if not vcs:
            local_sources += ["CMakeLists.txt", "src/main.cpp"]
    elif t == "rust":
        makedepends += ["rust", "cargo"]
        if not vcs:
            local_sources += ["Cargo.toml", "src/main.rs"]
    elif t == "":
        pass
    else:
        print(f"Unknown --type: {t}", file=sys.stderr)
        return 1

    if vcs and not vcs_url:
        print("--vcs-url is required when --vcs is specified", file=sys.stderr)
        return 1
    if vcs and vcs != "git":
        print(f"Unsupported --vcs: {vcs}", file=sys.stderr)
        return 1

    # Scaffold files (skipped for dry-run)
    if not getattr(args, "dry_run", False):
        scaffold_common_files(target, pkgname)
        scaffold_template(target, t, pkgname)
        maybe_scaffold_tests(target, args.with_tests)
        # Optional docs and completions
        from scaffold import maybe_scaffold_man, maybe_scaffold_completions, maybe_generate_rust_lock
        maybe_scaffold_man(target, pkgname, getattr(args, "with_man", False))
        maybe_scaffold_completions(target, pkgname, getattr(args, "with_completions", False))
        if t == "rust":
            maybe_generate_rust_lock(target, getattr(args, "rust_lock", False))

    # PKGBUILD rendering
    tpl_dir = find_templates_dir()
    tmpl = tpl_dir / "common/PKGBUILD.tmpl"
    if not tmpl.exists():
        print(f"Template not found: {tmpl}. Ensure templates are installed at '{tpl_dir}' (dev: templates/; install: /usr/share/aur-init/templates)", file=sys.stderr)
        return 1
    arch_line = compute_arch_line(t)
    dep_line = f"depends=({join_single_quoted(depends)})" if depends else ""
    makedep_line = f"makedepends=({join_single_quoted(makedepends)})" if makedepends else ""
    # Ensure optional assets are shipped when requested
    if args.with_tests:
        local_sources.append("scripts/tests/test.sh")
    if getattr(args, "with_man", False):
        # Look for man page in common locations
        for manpath in (f"man/{pkgname}.1", f"{pkgname}.1", f"docs/{pkgname}.1"):
            if (target / manpath).exists():
                local_sources.append(manpath)
                break
    if getattr(args, "with_completions", False):
        for compl in (f"completions/{pkgname}.bash", f"completions/bash/{pkgname}", f"completions/zsh/_{pkgname}", f"completions/fish/{pkgname}.fish"):
            if (target / compl).exists():
                local_sources.append(compl)
        
    src_sha = compute_source_and_sha(local_sources, vcs, vcs_url, pkgname)

    rendered = render_template(
        tmpl,
        {
            "MAINTAINER": maintainer,
            "PKGNAME": pkgname,
            "PKGVER": "0.3.0",
            "PKGDESC": pkgdesc,
            "ARCH_LINE": arch_line,
            "PKGURL": pkgurl,
            "PKGLICENSE": pkglicense,
            "DEPENDS_LINE": dep_line,
            "MAKEDEPENDS_LINE": makedep_line,
            "SOURCE_AND_SHA": src_sha,
            "BUILD_BLOCK": build_block(t, bool(vcs)),
            "CHECK_BLOCK": check_block(args.with_tests),
            "PACKAGE_BLOCK": package_block(t, bool(vcs)),
            "PKGVER_BLOCK": pkgver_block(bool(vcs)),
        },
    )
    # Strict mode checks
    if getattr(args, "strict", True):
        missing = []
        if not pkgurl:
            missing.append("url")
        if not pkglicense:
            missing.append("license")
        # For language types, we expect at least one runtime dependency
        if t in {"python", "node"} and not depends:
            missing.append("depends")
        if missing:
            print(f"Strict mode: missing required metadata: {', '.join(missing)}", file=sys.stderr)
            return 2

    # Explain mode: print brief rationale with ArchWiki links
    if getattr(args, "explain", False):
        print("# Explain: Key PKGBUILD fields (see ArchWiki: PKGBUILD)")
        print("# pkgname/pkver/pkgrel: mandatory identity/version fields — https://wiki.archlinux.org/title/PKGBUILD")
        print("# url/license: upstream home and license — https://wiki.archlinux.org/title/PKGBUILD#license")
        print("# depends/makedepends: runtime vs build deps — https://wiki.archlinux.org/title/PKGBUILD#depends")
        print("# source/sha256sums: sources and checksums — https://wiki.archlinux.org/title/PKGBUILD#source")
        print("# prepare/build/check/package: phases separation — https://wiki.archlinux.org/title/PKGBUILD#Package_guidelines")
        if vcs:
            print("# pkgver(): derive version from VCS — https://wiki.archlinux.org/title/VCS_package_guidelines")

    if getattr(args, "dry_run", False):
        # Print PKGBUILD to stdout and optionally .SRCINFO
        print(rendered)
        if getattr(args, "gen_srcinfo", False):
            import tempfile, subprocess, shutil
            with tempfile.TemporaryDirectory() as td:
                td_path = Path(td)
                (td_path / "PKGBUILD").write_text(rendered)
                makepkg = shutil.which("makepkg")
                if makepkg:
                    try:
                        out = subprocess.check_output([makepkg, "--printsrcinfo"], cwd=td, text=True)
                        print("# .SRCINFO\n" + out)
                    except Exception as e:
                        print(f"[dry-run] Failed to run makepkg --printsrcinfo: {e}", file=sys.stderr)
                else:
                    print("[dry-run] makepkg not found; cannot generate .SRCINFO", file=sys.stderr)
        return 0

    write_file(target / "PKGBUILD", rendered, 0o600)

    # Features
    if not getattr(args, "dry_run", False):
        maybe_git_init(target, args.git_init, pkgname)
        maybe_gen_srcinfo(target, args.gen_srcinfo)
        maybe_add_ci(target, args.add_ci)

    print(f"✅ AUR package project initialized in {pkgname}/")
    return 0
