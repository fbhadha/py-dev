"""render_agents.py --check: the Copilot agent files are what the script would write."""

import subprocess
import sys
from pathlib import Path


def test_the_rendered_agents_are_current(root: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "render_agents.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "rendered agent files are current" in result.stdout
