from pathlib import Path
import render


def test_join_single_quoted():
    assert render.join_single_quoted(["a", "b"]) == "'a' 'b'"
    assert render.join_single_quoted([]) == ""


def test_compute_arch_line():
    assert render.compute_arch_line("go") == "arch=('x86_64')"
    assert render.compute_arch_line("") == "arch=('any')"


def test_compute_source_and_sha_minimal():
    s = render.compute_source_and_sha([], "", "", "pkg")
    assert "source=()" in s and "sha256sums=()" in s


def test_compute_source_and_sha_local_and_vcs():
    s = render.compute_source_and_sha(["bin/p", "src/p/main.py"], "git", "https://x.git", "p")
    assert "'bin/p'" in s and "'src/p/main.py'" in s
    assert "'p::git+https://x.git'" in s
    assert s.count("'SKIP'") == 3


def test_render_template(tmp_path: Path):
    t = tmp_path / "tmpl.txt"
    t.write_text("Hello @NAME@ @NUM@!")
    out = render.render_template(t, {"NAME": "World", "NUM": "42"})
    assert out == "Hello World 42!"
