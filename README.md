# aur-init

`aur-init` is a scaffolding tool for creating new Arch Linux / AUR package projects.

## Usage

```
aur-init [options] <pkgname>
```

This will generate a new folder with:

* PKGBUILD
* .gitignore
* README.md

## Options

- `-m, --maintainer "Name <email>"` — Maintainer string. Default: `$(whoami) <you@example.com>`
- `-d, --desc "Description"` — Package description.
- `-u, --url URL` — Project URL. Defaults to `https://example.com/<pkgname>` if not set.
- `-l, --license LICENSE` — License identifier. Default: `MIT`.
- `-D, --depends "dep1 dep2"` — Space-separated runtime dependencies.
- `--git-init` — Initialize a git repository and create an initial commit.
- `--gen-srcinfo` — Generate `.SRCINFO` using `makepkg --printsrcinfo` (if available).
- `--type TYPE` — Template to scaffold language/tooling. One of: `python`, `go`, `node`, `cmake`.
- `--with-tests` — Add a simple test script and a `check()` function to `PKGBUILD`.
- `--vcs git` — Use a VCS source (currently supports `git`) and add a `pkgver()` function.
- `--vcs-url URL` — VCS repository URL, required when `--vcs` is used.
- `--ci` — Add a basic GitHub Actions workflow to generate `.SRCINFO` on pushes/PRs.
- `--force` — Overwrite files if the target directory exists and is not empty.
- `-h, --help` — Show help.

### Examples

```bash
# Minimal
aur-init hello-world

# With metadata and dependencies
aur-init -m "Jane Doe <jane@example.com>" \
         -d "Hello world example" \
         -u https://example.com/hello-world \
         -l MIT \
         -D "curl jq" \
         --git-init --gen-srcinfo \
         hello-world

# Language-specific scaffolds
# Python CLI with tests
aur-init --type python --with-tests mypycli

# Go binary, init git, and CI
aur-init --type go --git-init --ci mygocli

# Node binary with dependencies
aur-init --type node -D "nodejs npm" mynodecli

# CMake project
aur-init --type cmake mycmakeapp

# VCS package (git)
aur-init --vcs git --vcs-url https://github.com/user/proj.git proj-git
```

## Install

```
makepkg -si
```

Or, once published:

```
paru -S aur-init
```

## Generated PKGBUILD

The template includes empty `prepare()`/`build()` functions and a simple `package()` that installs a README file into `/usr/share/<pkgname>/`. Adjust as needed for your software.

To regenerate `.SRCINFO`:

```
makepkg --printsrcinfo > .SRCINFO
```

## Notes

- Templates create minimal sources so the generated `PKGBUILD` can build immediately.
- With `--vcs`, the generated `PKGBUILD` assumes the repository layout matches the chosen template (e.g., `src/<pkgname>/main.py` for `python`, `src/main.js` for `node`, etc.). Adjust paths if your repo differs.
- Use `--force` to scaffold into an existing non-empty directory (files will be overwritten).
