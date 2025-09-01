import render


def test_build_block_no_vcs_variants():
    # go
    s = render.build_block("go", vcs=False)
    assert 'go build' in s and '"$srcdir"' in s
    # rust
    s = render.build_block("rust", vcs=False)
    assert 'cargo build --release' in s and '"$srcdir"' in s
    # cmake
    s = render.build_block("cmake", vcs=False)
    assert 'cmake -S "$srcdir"' in s


def test_build_block_with_vcs_variants():
    # go
    s = render.build_block("go", vcs=True)
    assert 'go build' in s and '"$srcdir/$pkgname"' in s
    # rust
    s = render.build_block("rust", vcs=True)
    assert 'cargo build --release' in s and '"$srcdir/$pkgname"' in s
    # cmake
    s = render.build_block("cmake", vcs=True)
    assert 'cmake -S "$srcdir/$pkgname"' in s


def test_check_block_toggle():
    assert render.check_block(False) == ""
    chk = render.check_block(True)
    assert chk.startswith("check()") and "bash scripts/tests/test.sh" in chk


def test_package_block_no_vcs_variants():
    # python
    s = render.package_block("python", vcs=False)
    assert 'src/$pkgname/main.py' in s and 'bin/$pkgname' in s
    # node
    s = render.package_block("node", vcs=False)
    assert 'src/main.js' in s and 'bin/$pkgname' in s
    # go
    s = render.package_block("go", vcs=False)
    assert '"$srcdir/$pkgname"' in s
    # cmake
    s = render.package_block("cmake", vcs=False)
    assert '"$srcdir/build/$pkgname"' in s
    # rust
    s = render.package_block("rust", vcs=False)
    assert 'target/release/$pkgname' in s


def test_package_block_with_vcs_variants():
    # python with vcs
    s = render.package_block("python", vcs=True)
    assert '"$srcdir/$pkgname/src/$pkgname/main.py"' in s
    # go with vcs
    s = render.package_block("go", vcs=True)
    assert '"$srcdir/$pkgname/$pkgname"' in s


def test_pkgver_block_toggle():
    assert render.pkgver_block(False) == ""
    s = render.pkgver_block(True)
    assert s.startswith("pkgver()") and 'git describe' in s


def test_compute_source_and_sha_branching():
    # only local sources
    s = render.compute_source_and_sha(["a", "b"], "", "", "p")
    assert "'a'" in s and "'b'" in s and "source=(" in s and s.count("'SKIP'") == 2
    # only vcs
    s = render.compute_source_and_sha([], "git", "https://x", "p")
    assert "'p::git+https://x'" in s and s.count("'SKIP'") == 1
    # both
    s = render.compute_source_and_sha(["bin/p"], "git", "https://x", "p")
    assert "'bin/p'" in s and "'p::git+https://x'" in s and s.count("'SKIP'") == 2
