# aur-init

`aur-init` is a tiny scaffolding tool for creating new Arch Linux / AUR package projects.

## Features

- Generates a ready-to-build AUR project folder: `PKGBUILD`, `.gitignore`, `README.md`
- Language templates: minimal sources for `python`, `node`, `go`, `cmake`, `rust`
- Optional extras: initialize git, generate `.SRCINFO`, add CI workflow, test scaffold
- Interactive mode to pick options without memorizing flags

## Install

```bash
makepkg -si
```

## Usage

```bash
aur-init [options] [pkgname]
```

This generates a new folder named after `<pkgname>` containing:

* PKGBUILD
* .gitignore
* README.md

## Options

- `--type {,python,node,go,cmake,rust}` — Template to scaffold (empty for plain PKGBUILD)
- `-m, --maintainer` — Maintainer string. Default: `vince <you@example.com>`
- `-d, --description` — Package description
- `-u, --url` — Project URL (defaults to `https://example.com/<pkgname>`)
- `-l, --license` — License identifier (default: `MIT`)
- `--vcs {,git}` — Use a VCS source (supports `git`), adds `pkgver()`
- `--vcs-url` — Required when `--vcs` is set
- `--git-init` — Initialize a git repository
- `--srcinfo` — Generate `.SRCINFO` via `makepkg --printsrcinfo`
- `--ci` — Add a basic GitHub Actions workflow
- `--tests` — Add a simple test script and enable `check()`
- `--force` — Overwrite non-empty target directory
- `-i, --interactive` — Run an interactive form to choose options
- `-h, --help` — Show help

### Examples

```bash
# Minimal (plain PKGBUILD)
aur-init hello-world

# With metadata and dependencies
aur-init -m "Jane Doe <jane@example.com>" \
         -d "Hello world example" \
         -u https://example.com/hello-world \
         -l MIT \
         --git-init --srcinfo --ci \
         hello-world

# Python CLI with tests
aur-init --type python --tests mypycli

# Go binary, init git, and CI
aur-init --type go --git-init --ci mygocli

# Node binary with dependencies
aur-init --type node mynodecli

# CMake project
aur-init --type cmake mycmakeapp

# Rust binary
aur-init --type rust myrustcli

# VCS package (git)
aur-init --vcs git --vcs-url https://github.com/user/proj.git proj-git

# Interactive flow (no extra deps required)
aur-init --interactive
```

## Generated PKGBUILD

Templates produce minimal sources so the generated `PKGBUILD` can build immediately.

To regenerate `.SRCINFO`:

```
makepkg --printsrcinfo > .SRCINFO
```

## QA before publishing

- namcap:

  ```bash
  namcap PKGBUILD
  makepkg -f
  namcap *.pkg.tar.*
  ```

- Clean chroot build (extra/devtools):

  ```bash
  # one-time setup per arch
  mkarchroot /var/lib/archbuild/clean/root base-devel

  # build
  extra-x86_64-build   # or: arch-nspawn /var/lib/archbuild/clean/root makepkg -s
  ```

## Notes

- With `--vcs`, the generated `PKGBUILD` assumes the repository layout matches the chosen template (e.g., `src/<pkgname>/main.py` for `python`, `src/main.js` for `node`, etc.). Adjust paths if your repo differs.
- Use `--force` to scaffold into an existing non-empty directory (files will be overwritten).
