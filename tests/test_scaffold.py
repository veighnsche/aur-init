from pathlib import Path
import os
import scaffold


def test_ensure_dir_and_write_file(tmp_path: Path):
    p = tmp_path / "a/b/c.txt"
    scaffold.write_file(p, "data", 0o644)
    assert p.read_text() == "data"
    assert p.exists()


def test_scaffold_common_files(tmp_path: Path):
    scaffold.scaffold_common_files(tmp_path, "mypkg")
    assert (tmp_path / ".gitignore").exists()
    assert (tmp_path / "README.md").exists()


def test_scaffold_template_python(tmp_path: Path):
    scaffold.scaffold_template(tmp_path, "python", "mypkg")
    assert (tmp_path / "src/mypkg/main.py").exists()
    assert (tmp_path / "bin/mypkg").exists()


def test_scaffold_template_node(tmp_path: Path):
    scaffold.scaffold_template(tmp_path, "node", "mypkg")
    assert (tmp_path / "src/main.js").exists()
    assert (tmp_path / "bin/mypkg").exists()


def test_scaffold_template_go(tmp_path: Path):
    scaffold.scaffold_template(tmp_path, "go", "mypkg")
    assert (tmp_path / "main.go").exists()


def test_scaffold_template_cmake(tmp_path: Path):
    scaffold.scaffold_template(tmp_path, "cmake", "mypkg")
    assert (tmp_path / "CMakeLists.txt").exists()
    assert (tmp_path / "src/main.cpp").exists()


def test_maybe_scaffold_tests(tmp_path: Path):
    scaffold.maybe_scaffold_tests(tmp_path, True)
    assert (tmp_path / "scripts/tests/test.sh").exists()
    scaffold.maybe_scaffold_tests(tmp_path, False)
    # no exception when disabled
