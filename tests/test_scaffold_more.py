from pathlib import Path
import scaffold


def test_maybe_scaffold_man(tmp_path: Path):
    scaffold.maybe_scaffold_man(tmp_path, "mypkg", True)
    p = tmp_path / "man/mypkg.1"
    assert p.exists()
    txt = p.read_text()
    assert ".TH mypkg 1" in txt
    assert "\\- example CLI" in txt  # escaped hyphen present


def test_maybe_scaffold_completions(tmp_path: Path):
    scaffold.maybe_scaffold_completions(tmp_path, "mypkg", True)
    bash = tmp_path / "completions/bash/mypkg"
    zsh = tmp_path / "completions/zsh/_mypkg"
    fish = tmp_path / "completions/fish/mypkg.fish"
    for f in (bash, zsh, fish):
        assert f.exists()
    assert "bash completion stub" in bash.read_text()
    assert "#compdef mypkg" in zsh.read_text()
    assert "fish completion stub" in fish.read_text()
