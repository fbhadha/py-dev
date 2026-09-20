#!/usr/bin/env python3
"""Fail when a change made a file it touched worse.

Runs Repowise's change review over a revision range and exits non-zero if the
diff introduced any new code-health finding (deeper nesting, a new god class,
I/O inside a loop, a swallowed exception, duplication) on the files it changed.
Pre-existing findings in those files are reported but do not fail the run.

Usage:
    uv run python scripts/repowise_gate.py origin/main..HEAD
    uv run python scripts/repowise_gate.py            # uncommitted work, or HEAD

Exit codes:
    0  nothing introduced
    1  at least one finding introduced
    2  Repowise is not installed or the repo is not indexed
    3  the health lane was unavailable or degraded (fail closed; see --allow-unavailable)

Repowise is AGPL-3.0. This script imports it in CI and in a developer's shell,
and is never shipped inside a product.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "revspec", nargs="?", default=None, help="commit or base..head; omit for the working tree"
    )
    parser.add_argument(
        "--allow-unavailable",
        action="store_true",
        help="exit 0 instead of 3 when Repowise could not analyse the change",
    )
    args = parser.parse_args()

    try:
        from repowise.core.analysis.change_health import GitRevisionSource
        from repowise.core.analysis.change_review import ChangeReviewRequest, ChangeReviewService
    except ImportError:
        print("repowise is not installed: uv add --group dev repowise", file=sys.stderr)
        return 2

    service = ChangeReviewService(GitRevisionSource("."), repo_path=".")
    bundle = service.review(ChangeReviewRequest(revspec=args.revspec))
    health = bundle.lane("health")

    if health.state != "available":
        print(f"health lane {health.state}: {health.reason}", file=sys.stderr)
        return 0 if args.allow_unavailable else 3

    payload = bundle.as_dict()["health"]
    introduced = [f for f in payload["findings"] if f["change_kind"] == "introduced"]
    worsened = [f for f in payload["findings"] if f["change_kind"] == "worsened"]
    unchanged = payload.get("unchanged_total", 0)

    scope = payload.get("scope", {})
    print(
        f"repowise change gate: {scope.get('analyzed', 0)} file(s) analysed, "
        f"{len(introduced)} introduced, {len(worsened)} worsened, {unchanged} pre-existing"
    )
    for finding in introduced + worsened:
        where = f"{finding['path']}:{finding['line_start']}"
        symbol = finding.get("symbol") or "-"
        print(
            f"  {finding['change_kind']:<10} {finding['biomarker_type']:<22} "
            f"{where}  {symbol}: {finding['reason']}"
        )

    if introduced or worsened:
        print(
            "\nFix the findings above, or explain in the PR why the shape is right "
            "and get a reviewer to agree."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
