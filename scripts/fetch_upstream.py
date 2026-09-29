"""Download the pinned churn repo and the cited MULTI-HEAD files."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from governance.upstream import ensure_upstream


def main() -> None:
    roots = ensure_upstream()
    for name, path in roots.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
