from pathlib import Path
import types
import features


class DummyRun:
    def __init__(self):
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return types.SimpleNamespace(returncode=0)


def test_maybe_git_init_skips_without_git(tmp_path, monkeypatch):
    monkeypatch.setattr(features.shutil, "which", lambda _: None)
    features.maybe_git_init(tmp_path, True, "p")
    # Should not raise, and no repo created
    assert not (tmp_path / ".git").exists()


def test_maybe_git_init_runs_with_git(tmp_path, monkeypatch):
    monkeypatch.setattr(features.shutil, "which", lambda _: "/usr/bin/git")
    dummy = DummyRun()
    monkeypatch.setattr(features, "subprocess", types.SimpleNamespace(run=dummy))
    # create files to stage
    (tmp_path / "PKGBUILD").write_text("")
    (tmp_path / ".gitignore").write_text("")
    (tmp_path / "README.md").write_text("")
    features.maybe_git_init(tmp_path, True, "p")
    # Ensure git init and commit attempted
    cmds = [c[0][0][0] for c in dummy.calls]
    assert "git" in cmds


def test_maybe_gen_srcinfo_skips_without_makepkg(tmp_path, monkeypatch):
    monkeypatch.setattr(features.shutil, "which", lambda _: None)
    features.maybe_gen_srcinfo(tmp_path, True)


def test_maybe_gen_srcinfo_runs_with_makepkg(tmp_path, monkeypatch):
    monkeypatch.setattr(features.shutil, "which", lambda _: "/usr/bin/makepkg")
    dummy = DummyRun()
    monkeypatch.setattr(features, "subprocess", types.SimpleNamespace(run=dummy))
    features.maybe_gen_srcinfo(tmp_path, True)
    assert dummy.calls, "should have invoked makepkg --printsrcinfo"


def test_maybe_add_ci_from_template(tmp_path, monkeypatch):
    # Build a fake template dir structure
    troot = tmp_path / "tpl"
    (troot / "common").mkdir(parents=True)
    (troot / "common/ci.yml.tmpl").write_text("name: CI")
    monkeypatch.setattr(features, "find_templates_dir", lambda: troot)
    features.maybe_add_ci(tmp_path, True)
    assert (tmp_path / ".github/workflows/aur.yml").exists()


def test_maybe_add_ci_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(features, "find_templates_dir", lambda: tmp_path / "does-not-exist")
    features.maybe_add_ci(tmp_path, True)
    assert (tmp_path / ".github/workflows/aur.yml").exists()
