from types import SimpleNamespace
from pathlib import Path
import builtins
import io
import sys

import core


def _args(**kw):
    # Reasonable defaults mirroring CLI parser defaults
    d = dict(
        pkgname="pkg",
        type="",
        maintainer="vince <you@example.com>",
        description="TODO: describe your package",
        url=None,
        license="MIT",
        vcs="",
        vcs_url="",
        git_init=False,
        gen_srcinfo=False,
        add_ci=False,
        with_tests=False,
        with_man=False,
        with_completions=False,
        rust_lock=False,
        dry_run=True,
        strict=True,
        explain=False,
        doctor=False,
        force=False,
    )
    d.update(kw)
    return SimpleNamespace(**d)


def test_execute_minimal_dry_run(tmp_path: Path, monkeypatch):
    # Run in temp directory
    monkeypatch.chdir(tmp_path)
    args = _args(pkgname="hello")
    # Capture stdout for dry-run output
    cap = io.StringIO()
    monkeypatch.setattr(sys, "stdout", cap)
    rc = core.execute(args)
    assert rc == 0
    out = cap.getvalue()
    # Sanity: PKGBUILD content should include key fields
    assert "pkgname=hello" in out
    assert "pkgver()" not in out  # no VCS by default


def test_execute_invalid_pkgname(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = _args(pkgname="InvalidUpper")
    rc = core.execute(args)
    assert rc == 2


def test_execute_unknown_type(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = _args(pkgname="p", type="unknown")
    rc = core.execute(args)
    assert rc == 1


def test_execute_vcs_requires_url(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = _args(pkgname="p", type="go", vcs="git", vcs_url="")
    rc = core.execute(args)
    assert rc == 1


def test_execute_python_dep_and_check_block(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # python type with tests should include depends and check() content
    args = _args(pkgname="p", type="python", with_tests=True)
    cap = io.StringIO()
    monkeypatch.setattr(sys, "stdout", cap)
    rc = core.execute(args)
    assert rc == 0
    out = cap.getvalue()
    assert "depends=('python')" in out
    assert "check()" in out


def test_execute_rust_pkgver_block_when_vcs(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = _args(pkgname="p", type="rust", vcs="git", vcs_url="https://example.com/x.git")
    cap = io.StringIO()
    monkeypatch.setattr(sys, "stdout", cap)
    rc = core.execute(args)
    assert rc == 0
    out = cap.getvalue()
    assert "pkgver()" in out
