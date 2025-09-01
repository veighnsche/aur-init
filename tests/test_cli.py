import cli


def test_parse_args_minimal():
    args = cli.parse_args(["mypkg"])
    assert args.pkgname == "mypkg"
    assert args.type == ""
    assert args.vcs == ""
    assert args.git_init is False
    assert args.gen_srcinfo is False
    assert args.add_ci is False
    assert args.with_tests is False
    assert args.force is False


def test_parse_args_full():
    argv = [
        "mypkg", "--type", "python", "--vcs", "git", "--vcs-url", "https://example/repo.git",
        "-m", "A <a@example.com>", "-d", "desc", "-u", "https://url", "-l", "Apache-2.0",
        "--git-init", "--srcinfo", "--ci", "--tests", "--force",
    ]
    args = cli.parse_args(argv)
    assert args.pkgname == "mypkg"
    assert args.type == "python"
    assert args.vcs == "git"
    assert args.vcs_url.endswith("repo.git")
    assert args.maintainer.startswith("A ")
    assert args.description == "desc"
    assert args.url == "https://url"
    assert args.license == "Apache-2.0"
    assert args.git_init
    assert args.gen_srcinfo
    assert args.add_ci
    assert args.with_tests
    assert args.force
