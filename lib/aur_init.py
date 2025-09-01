#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure local lib directory is importable
LIB_DIR = Path(__file__).resolve().parent
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from cli import parse_args  # noqa: E402
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
)  # noqa: E402
from scaffold import (
    ensure_dir,
    write_file,
    scaffold_common_files,
    scaffold_template,
    maybe_scaffold_tests,
)  # noqa: E402
from features import (
    maybe_git_init,
    maybe_gen_srcinfo,
    maybe_add_ci,
)  # noqa: E402


def main(argv):
    args = parse_args(argv)
    pkgname = args.pkgname
    t = args.type
    vcs = args.vcs
    vcs_url = args.vcs_url

    target = Path.cwd() / pkgname
    if target.exists() and any(target.iterdir()) and not args.force:
        print(f"Target directory '{pkgname}' exists and is not empty. Use --force to overwrite.", file=sys.stderr)
        return 1

    ensure_dir(target)

    maintainer = args.maintainer
    pkgdesc = args.description
    pkgurl = args.url or f"https://example.com/{pkgname}"
    pkglicense = args.license

    depends = []
    makedepends = []
    local_sources = []

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

    # Scaffold files
    scaffold_common_files(target, pkgname)
    scaffold_template(target, t, pkgname)
    maybe_scaffold_tests(target, args.with_tests)

    # PKGBUILD rendering
    tpl_dir = find_templates_dir()
    tmpl = tpl_dir / "common/PKGBUILD.tmpl"
    arch_line = compute_arch_line(t)
    dep_line = f"depends=({join_single_quoted(depends)})" if depends else ""
    makedep_line = f"makedepends=({join_single_quoted(makedepends)})" if makedepends else ""
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
    write_file(target / "PKGBUILD", rendered, 0o600)

    # Features
    maybe_git_init(target, args.git_init, pkgname)
    maybe_gen_srcinfo(target, args.gen_srcinfo)
    maybe_add_ci(target, args.add_ci)

    print(f"✅ AUR package project initialized in {pkgname}/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
