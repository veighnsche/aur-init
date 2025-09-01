import os
import subprocess
from pathlib import Path


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def test_e2e_generate_minimal(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    aur = root / "aur-init"
    assert aur.exists()
    name = "e2e-minimal"
    run([str(aur), name], cwd=tmp_path)
    d = tmp_path / name
    assert (d / "PKGBUILD").exists()
    # minimal should have no depends/makedepends lines rendered
    content = (d / "PKGBUILD").read_text()
    assert "depends=(" not in content
    assert "makedepends=(" not in content


def test_e2e_generate_python(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    aur = root / "aur-init"
    name = "e2e-python"
    run([str(aur), "--type", "python", name], cwd=tmp_path)
    d = tmp_path / name
    assert (d / "PKGBUILD").exists()
    content = (d / "PKGBUILD").read_text()
    assert "depends=('python')" in content
    assert (d / f"src/{name}/main.py").exists()
    assert (d / f"bin/{name}").exists()


def test_e2e_generate_rust(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    aur = root / "aur-init"
    name = "e2e-rust"
    run([str(aur), "--type", "rust", name], cwd=tmp_path)
    d = tmp_path / name
    assert (d / "PKGBUILD").exists()
    content = (d / "PKGBUILD").read_text()
    assert "makedepends=('rust' 'cargo')" in content
    assert (d / "Cargo.toml").exists()
    assert (d / "src/main.rs").exists()
