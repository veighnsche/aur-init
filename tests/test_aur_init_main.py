import io
import os
from pathlib import Path
import types

import aur_init


def test_main_dry_run_no_summary(monkeypatch, tmp_path: Path):
    # Avoid heavy work in execute
    monkeypatch.setattr(aur_init, "execute", lambda args: 0)
    err = io.StringIO()
    monkeypatch.setattr(aur_init.sys, "stderr", err)
    rc = aur_init.main(["pkg", "--dry-run"])  # summary should be suppressed
    assert rc == 0
    assert "[aur-init]" not in err.getvalue()


def test_main_doctor_suppresses_summary(monkeypatch):
    monkeypatch.setattr(aur_init, "doctor", lambda: 0)
    err = io.StringIO()
    monkeypatch.setattr(aur_init.sys, "stderr", err)
    rc = aur_init.main(["--doctor"])  # returns before summary/execute
    assert rc == 0
    assert "[aur-init]" not in err.getvalue()


def test_main_requires_pkgname_without_interactive(monkeypatch):
    err = io.StringIO()
    monkeypatch.setattr(aur_init.sys, "stderr", err)
    # Provide a flag so argparse doesn't default to -h
    rc = aur_init.main(["--dry-run"])  # still requires pkgname when not interactive
    assert rc == 2
    assert "pkgname is required" in err.getvalue()


def test_main_interactive_requires_tty(monkeypatch):
    # Force non-tty stdin
    class FakeIn:
        def isatty(self):
            return False
    monkeypatch.setattr(aur_init.sys, "stdin", FakeIn())
    err = io.StringIO()
    monkeypatch.setattr(aur_init.sys, "stderr", err)
    rc = aur_init.main(["--interactive"])  # no pkgname needed; should fail due to non-tty
    assert rc == 2
    assert "requires a TTY" in err.getvalue()


def test_main_summary_with_profile_auto_discovery(monkeypatch, tmp_path: Path):
    # Create XDG config with TOML profile
    cfg_dir = tmp_path / "cfg"
    (cfg_dir / "aur-init").mkdir(parents=True)
    cfg = cfg_dir / "aur-init" / "config.toml"
    cfg.write_text("""
maintainer = "Test <t@example.com>"
url_base = "https://example.com"
""".strip())
    monkeypatch.setenv("XDG_CONFIG_HOME", str(cfg_dir))
    # Avoid heavy work in execute, but allow summary emission (no dry-run)
    monkeypatch.setattr(aur_init, "execute", lambda args: 0)
    err = io.StringIO()
    monkeypatch.setattr(aur_init.sys, "stderr", err)
    rc = aur_init.main(["hello"])  # not dry-run, should print summary including profile path
    assert rc == 0
    e = err.getvalue()
    assert "[aur-init]" in e
    assert "Scaffolding hello" in e
    assert "type=generic" in e and "vcs=none" in e
    assert f"profile={cfg}" in e
