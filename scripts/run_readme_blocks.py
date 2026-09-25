#!/usr/bin/env python3
"""Execute every ```bash ci``` block in a Markdown file, so the README cannot lie.

A block is fenced as:

    ```bash ci
    uv run pytest
    ```

Plain ```bash``` blocks are documentation and are not run. Each ci block runs
in the repo root with `bash -euo pipefail`; the first failing block stops the
run and its output is printed.

Usage: uv run python scripts/run_readme_blocks.py README.md
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

FENCE = re.compile(r"^```bash ci\s*\n(.*?)^```", re.DOTALL | re.MULTILINE)


def main(path: str) -> int:
    text = Path(path).read_text(encoding="utf-8")
    blocks = FENCE.findall(text)
    if not blocks:
        print(f"{path}: no ```bash ci``` blocks; nothing to run")
        return 0
    for index, block in enumerate(blocks, start=1):
        print(f"--- block {index}/{len(blocks)} ---\n{block.rstrip()}")
        result = subprocess.run(
            ["bash", "-euo", "pipefail", "-c", block], text=True, capture_output=True, check=False
        )
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        if result.returncode != 0:
            print(f"{path}: block {index} failed with exit code {result.returncode}")
            return result.returncode
    print(f"{path}: {len(blocks)} block(s) ran clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "README.md"))
