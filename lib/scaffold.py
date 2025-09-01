#!/usr/bin/env python3
import os
from pathlib import Path


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def write_file(p: Path, data: str, mode=0o644):
    ensure_dir(p.parent)
    p.write_text(data)
    os.chmod(p, mode)


def scaffold_common_files(root: Path, pkgname: str):
    write_file(root / ".gitignore", """# Build artifacts
/pkg/
*.tar.*
*.tar.gz
*.tar.zst
*.log
*.lock
""", 0o644)
    write_file(root / "README.md", f"""# {pkgname}

Initialized with `aur-init`.

## Build and install

1. Review and update fields in `PKGBUILD` as needed (pkgdesc, url, license, depends, makedepends).
2. Build and install:

   ```bash
   makepkg -si
   ```

## Developer notes

- Generate `.SRCINFO`:

  ```bash
  makepkg --printsrcinfo > .SRCINFO
  ```

- Clean build artifacts:

  ```bash
  rm -rf pkg/ src/ *.tar.* *.tar.zst *.log *.lock
  ```

## Project layout

- `PKGBUILD` — package recipe
- `bin/` — installed entrypoints (if applicable)
- `src/` — project sources (if applicable)

## Running

After install, `{pkgname}` should be available on your `PATH` if a `bin/{pkgname}` script was generated.
""", 0o644)


def scaffold_template(root: Path, t: str, pkgname: str):
    if t == "python":
        ensure_dir(root / f"src/{pkgname}")
        write_file(root / f"src/{pkgname}/main.py", f"""#!/usr/bin/env python
print(\"Hello from {pkgname} (python)\")
""", 0o755)
        write_file(root / f"bin/{pkgname}", f"""#!/usr/bin/env bash
exec python "/usr/share/{pkgname}/main.py" "$@"
""", 0o755)
    elif t == "node":
        ensure_dir(root / "src")
        write_file(root / "src/main.js", f"""#!/usr/bin/env node
console.log('Hello from {pkgname} (node)');
""", 0o755)
        write_file(root / f"bin/{pkgname}", f"""#!/usr/bin/env node
require('/usr/share/{pkgname}/main.js')
""", 0o755)
    elif t == "go":
        write_file(root / "main.go", """package main
import "fmt"
func main(){fmt.Println("Hello from GO")}
""", 0o644)
    elif t == "cmake":
        ensure_dir(root / "src")
        write_file(root / "CMakeLists.txt", f"""cmake_minimum_required(VERSION 3.10)
project({pkgname})
add_executable({pkgname} src/main.cpp)
""", 0o644)
        write_file(root / "src/main.cpp", f"""#include <iostream>
int main(){{ std::cout << "Hello from {pkgname} (cmake)\\n"; return 0; }}
""", 0o644)
    elif t == "rust":
        ensure_dir(root / "src")
        write_file(root / "Cargo.toml", f"""[package]
name = "{pkgname}"
version = "0.1.0"
edition = "2021"

[dependencies]
""", 0o644)
        write_file(root / "src/main.rs", f"""fn main() {{
    println!("Hello from {pkgname} (rust)");
}}
""", 0o644)
    # else minimal: nothing


def maybe_scaffold_tests(root: Path, with_tests: bool):
    if with_tests:
        ensure_dir(root / "scripts/tests")
        write_file(root / "scripts/tests/test.sh", """#!/usr/bin/env bash
set -euo pipefail
echo "Running basic test..."
[[ -f PKGBUILD ]] && echo "PKGBUILD exists"
""", 0o755)
