#!/usr/bin/env python3
import sys
import shutil
import subprocess
from pathlib import Path

from render import find_templates_dir
from scaffold import ensure_dir, write_file


def maybe_git_init(root: Path, enabled: bool, pkgname: str):
    if not enabled:
        return
    if shutil.which("git") is None:
        print("git not found; skipping repo initialization", file=sys.stderr)
        return
    subprocess.run(["git", "init", "-q"], cwd=root, check=False)
    # Stage common files
    to_add = ["PKGBUILD", ".gitignore", "README.md"]
    if (root / ".github").exists():
        to_add.append(".github")
    for d in ("src", "bin"):
        if (root / d).exists():
            to_add.append(d)
    for f in ("main.go", "CMakeLists.txt"):
        if (root / f).exists():
            to_add.append(f)
    if (root / "scripts").exists():
        to_add.append("scripts")
    if to_add:
        subprocess.run(["git", "add", *to_add], cwd=root, check=False)
        subprocess.run(["git", "commit", "-qm", f"chore: initialize AUR package {pkgname}"], cwd=root, check=False)


def maybe_gen_srcinfo(root: Path, enabled: bool):
    if not enabled:
        return
    if shutil.which("makepkg") is None:
        print("makepkg not found; cannot generate .SRCINFO", file=sys.stderr)
        return
    with open(root / ".SRCINFO", "w") as f:
        subprocess.run(["makepkg", "--printsrcinfo"], cwd=root, check=False, stdout=f)


def maybe_add_ci(root: Path, enabled: bool):
    if not enabled:
        return
    ensure_dir(root / ".github/workflows")
    tpl_dir = find_templates_dir()
    ci_tmpl = tpl_dir / "common/ci.yml.tmpl"
    if ci_tmpl.exists():
        shutil.copy(ci_tmpl, root / ".github/workflows/aur.yml")
    else:
        write_file(root / ".github/workflows/aur.yml", """name: AUR CI
on: [push, pull_request]
jobs:
  srcinfo:
    runs-on: ubuntu-latest
    container: archlinux:latest
    steps:
      - uses: actions/checkout@v4
      - name: Install build tools
        run: pacman -Syu --noconfirm base-devel git
      - name: Generate .SRCINFO
        run: makepkg --printsrcinfo > .SRCINFO
      - name: Show .SRCINFO
        run: cat .SRCINFO || true
""", 0o644)
