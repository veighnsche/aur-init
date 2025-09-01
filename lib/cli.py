#!/usr/bin/env python3
import argparse

def parse_args(argv):
    ap = argparse.ArgumentParser(prog="aur-init", add_help=True)
    ap.add_argument("pkgname")
    ap.add_argument("--type", dest="type", choices=["", "python", "node", "go", "cmake"], default="")
    ap.add_argument("-m", "--maintainer", default="vince <you@example.com>")
    ap.add_argument("-d", "--description", default="TODO: describe your package")
    ap.add_argument("-u", "--url", default=None)
    ap.add_argument("-l", "--license", dest="license", default="MIT")
    ap.add_argument("--vcs", choices=["", "git"], default="")
    ap.add_argument("--vcs-url", dest="vcs_url", default="")
    ap.add_argument("--git-init", action="store_true")
    ap.add_argument("--srcinfo", dest="gen_srcinfo", action="store_true")
    ap.add_argument("--ci", dest="add_ci", action="store_true")
    ap.add_argument("--tests", dest="with_tests", action="store_true")
    ap.add_argument("--force", action="store_true")
    return ap.parse_args(argv)
