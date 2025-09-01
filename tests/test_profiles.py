import json
import os
import subprocess
from pathlib import Path


def run(cmd, cwd, env=None):
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )


def test_summary_emitted_with_profile(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    aur = root / "aur-init"
    assert aur.exists()

    # Create a profile file (JSON) with some toggles
    profile = {
        "with_tests": True,
        "git_init": True,
        "type": "go",
        "vcs": "git",
        "vcs_url": "https://example.com/repo.git",
    }
    prof_path = tmp_path / "profile.json"
    prof_path.write_text(json.dumps(profile), encoding="utf-8")

    name = "e2e-profile-summary"
    cp = run([str(aur), "--from-file", str(prof_path), name], cwd=tmp_path)

    # Should scaffold and print a one-line summary to stderr
    err = cp.stderr
    assert "[aur-init]" in err
    assert f"Scaffolding {name}" in err
    assert "type=go" in err
    assert "vcs=git" in err
    # Enabled switches show up
    assert "git-init" in err
    assert "tests" in err
    # Profile path is included
    assert str(prof_path) in err

    # Project should be created
    d = tmp_path / name
    assert (d / "PKGBUILD").exists()


essential_env_keys = [
    # ensure predictable environment for aur-init
    "PATH",
    "HOME",
]


def _env_with_xdg(tmp_path: Path):
    env = {k: os.environ.get(k, "") for k in essential_env_keys}
    env["XDG_CONFIG_HOME"] = str(tmp_path)
    return env


def test_auto_discover_profile_via_xdg(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    aur = root / "aur-init"

    # Write config under $XDG_CONFIG_HOME/aur-init/config.json
    cfg_dir = tmp_path / "aur-init"
    cfg_dir.mkdir(parents=True)
    profile = {
        "add_ci": True,
        "type": "python",
    }
    cfg = cfg_dir / "config.json"
    cfg.write_text(json.dumps(profile), encoding="utf-8")

    env = _env_with_xdg(tmp_path)
    name = "e2e-xdg-profile"
    cp = run([str(aur), name], cwd=tmp_path, env=env)

    # Summary should include profile path and reflect type and ci flag
    err = cp.stderr
    assert "[aur-init]" in err
    assert "type=python" in err
    assert "ci" in err
    assert str(cfg) in err

    d = tmp_path / name
    assert (d / "PKGBUILD").exists()


def test_no_summary_on_dry_run(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    aur = root / "aur-init"

    name = "e2e-dry-run"
    cp = run([str(aur), "--dry-run", name], cwd=tmp_path)

    # No summary should be emitted in dry-run
    assert "[aur-init]" not in cp.stderr
    # Dry-run still prints content to stdout; ensure command succeeded
    assert cp.stdout
