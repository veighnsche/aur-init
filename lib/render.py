#!/usr/bin/env python3
from pathlib import Path

# Template directory resolution
SCRIPT_DIR = Path(__file__).resolve().parent.parent  # lib/.. (project root)
INSTALL_TPL_DIR = Path("/usr/share/aur-init/templates")
DEV_TPL_DIR = SCRIPT_DIR / "templates"


def find_templates_dir() -> Path:
    if DEV_TPL_DIR.is_dir():
        return DEV_TPL_DIR
    if INSTALL_TPL_DIR.is_dir():
        return INSTALL_TPL_DIR
    return DEV_TPL_DIR


def render_template(template_path: Path, replacements: dict) -> str:
    content = template_path.read_text()
    for k, v in replacements.items():
        content = content.replace(f"@{k}@", v)
    return content


def compute_arch_line(t: str) -> str:
    if t in ("go", "cmake"):
        return "arch=('x86_64')"
    return "arch=('any')"


def join_single_quoted(items) -> str:
    return " ".join([f"'{x}'" for x in items])


def compute_source_and_sha(local_sources, vcs, vcs_url, pkgname):
    parts = []
    sha = []
    for s in local_sources:
        parts.append(f"'{s}'")
        sha.append("'SKIP'")
    if vcs:
        parts.append(f"'{pkgname}::{vcs}+{vcs_url}'")
        sha.append("'SKIP'")
    if parts:
        return f"source=({ ' '.join(parts) })\nsha256sums=({ ' '.join(sha) })"
    else:
        return "source=()\nsha256sums=()"


def build_block(t: str, vcs: bool) -> str:
    lines = []
    if not vcs and t == "go":
        lines.append('  cd "$srcdir"; go build -o "$pkgname" .')
    if not vcs and t == "cmake":
        lines.append('  cmake -S "$srcdir" -B "$srcdir/build" -DCMAKE_BUILD_TYPE=Release && cmake --build "$srcdir/build" --config Release')
    if vcs and t == "go":
        lines.append('  cd "$srcdir/$pkgname"; go build -o "$pkgname" .')
    if vcs and t == "cmake":
        lines.append('  cmake -S "$srcdir/$pkgname" -B "$srcdir/build" -DCMAKE_BUILD_TYPE=Release && cmake --build "$srcdir/build" --config Release')
    return ("\n".join(lines) + ("\n" if lines else ""))


def check_block(with_tests: bool) -> str:
    if not with_tests:
        return ""
    return (
        "check()"\
        "{\n  bash scripts/tests/test.sh\n}\n"
    )


def package_block(t: str, vcs: bool) -> str:
    lines = []
    if not vcs and t == "python":
        lines.append('  install -Dm644 "$srcdir/src/$pkgname/main.py" "$pkgdir/usr/share/$pkgname/main.py"')
        lines.append('  install -Dm755 "$srcdir/bin/$pkgname" "$pkgdir/usr/bin/$pkgname"')
    if not vcs and t == "node":
        lines.append('  install -Dm644 "$srcdir/src/main.js" "$pkgdir/usr/share/$pkgname/main.js"')
        lines.append('  install -Dm755 "$srcdir/bin/$pkgname" "$pkgdir/usr/bin/$pkgname"')
    if not vcs and t == "go":
        lines.append('  install -Dm755 "$srcdir/$pkgname" "$pkgdir/usr/bin/$pkgname"')
    if not vcs and t == "cmake":
        lines.append('  install -Dm755 "$srcdir/build/$pkgname" "$pkgdir/usr/bin/$pkgname"')
    if vcs and t == "python":
        lines.append('  install -Dm644 "$srcdir/$pkgname/src/$pkgname/main.py" "$pkgdir/usr/share/$pkgname/main.py"')
        lines.append('  install -Dm755 "$srcdir/$pkgname/bin/$pkgname" "$pkgdir/usr/bin/$pkgname"')
    if vcs and t == "node":
        lines.append('  install -Dm644 "$srcdir/$pkgname/src/main.js" "$pkgdir/usr/share/$pkgname/main.js"')
        lines.append('  install -Dm755 "$srcdir/$pkgname/bin/$pkgname" "$pkgdir/usr/bin/$pkgname"')
    if vcs and t == "go":
        lines.append('  install -Dm755 "$srcdir/$pkgname/$pkgname" "$pkgdir/usr/bin/$pkgname"')
    if vcs and t == "cmake":
        lines.append('  install -Dm755 "$srcdir/build/$pkgname" "$pkgdir/usr/bin/$pkgname"')
    return ("\n".join(lines) + ("\n" if lines else ""))


def pkgver_block(vcs: bool) -> str:
    if not vcs:
        return ""
    return (
        "pkgver()\n"\
        "{\n  cd \"${srcdir}/${pkgname}\" || return 0\n  git describe --tags --long 2>/dev/null | sed 's/^v//' | tr '-' '.' || echo \"0\"\n}\n"
    )
