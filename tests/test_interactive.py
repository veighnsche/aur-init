from types import SimpleNamespace
import builtins
import io
import sys
import interactive


def _args(**kw):
    d = dict(
        pkgname="",
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
        dry_run=False,
        strict=True,
        explain=False,
        doctor=False,
        force=False,
    )
    d.update(kw)
    return SimpleNamespace(**d)


def test_interactive_simple_flow_with_url_base(monkeypatch):
    # Prepare default args with a profile-provided url_base
    args = _args(url_base="https://example.com")
    # Sequence of inputs for simple mode (accept defaults where appropriate)
    inputs = iter([
        "",            # Mode select -> default (Simple)
        "mypkg",        # pkgname
        "",            # type select -> default ""
        "",            # maintainer (keep default)
        "",            # description (keep default)
        "",            # url (use url_base/pkgname)
        "",            # license (keep default)
        "",            # VCS select -> default ""
        "",            # git_init default False
        "",            # with_tests default False
    ])
    monkeypatch.setattr(builtins, "input", lambda *a, **k: next(inputs))
    out_err = io.StringIO()
    monkeypatch.setattr(sys, "stderr", out_err)

    res = interactive.collect_interactive_inputs(args)

    assert res.pkgname == "mypkg"
    assert res.type == ""
    assert res.url == "https://example.com/mypkg"
    assert res.git_init is False and res.with_tests is False
    assert res.strict is True


def test_interactive_advanced_flow(monkeypatch):
    args = _args()
    # Choices: type list index for "go" is 4 (1-based): ["", "python", "node", "go", ...]
    inputs = iter([
        "2",           # Mode -> Advanced
        "p",           # pkgname
        "4",           # type -> go
        "",            # maintainer keep
        "",            # description keep
        "",            # url keep default https://example.com/p
        "",            # license keep
        "1",           # VCS -> "" (no VCS)
        "y",           # git_init -> True
        "y",           # with_tests -> True
        "y",           # gen_srcinfo -> True
        "n",           # add_ci -> False
        "y",           # with_man -> True (since type selected)
        "n",           # with_completions -> False
        # rust_lock skipped (type is go)
        "y",           # dry_run -> True
        "",            # strict keep True
        "n",           # explain -> False
        "n",           # doctor -> False
        "y",           # force -> True
    ])
    monkeypatch.setattr(builtins, "input", lambda *a, **k: next(inputs))
    out_err = io.StringIO()
    monkeypatch.setattr(sys, "stderr", out_err)

    res = interactive.collect_interactive_inputs(args)

    assert res.pkgname == "p"
    assert res.type == "go"
    assert res.git_init is True
    assert res.with_tests is True
    assert res.gen_srcinfo is True
    assert res.add_ci is False
    assert res.with_man is True
    assert res.with_completions is False
    assert res.dry_run is True
    assert res.strict is True
    assert res.explain is False
    assert res.doctor is False
    assert res.force is True


def test_interactive_ctrl_c_exit(monkeypatch):
    args = _args()
    def raiser(*a, **k):
        raise KeyboardInterrupt
    monkeypatch.setattr(builtins, "input", raiser)
    err = io.StringIO()
    monkeypatch.setattr(sys, "stderr", err)
    try:
        interactive.collect_interactive_inputs(args)
        assert False, "expected SystemExit"
    except SystemExit as e:
        assert e.code == 130
        assert "Aborted by user" in err.getvalue()


def test_interactive_eof_exit(monkeypatch):
    args = _args()
    def raiser(*a, **k):
        raise EOFError
    monkeypatch.setattr(builtins, "input", raiser)
    err = io.StringIO()
    monkeypatch.setattr(sys, "stderr", err)
    try:
        interactive.collect_interactive_inputs(args)
        assert False, "expected SystemExit"
    except SystemExit as e:
        assert e.code == 130
        assert "Aborted: input stream closed (EOF)" in err.getvalue()
