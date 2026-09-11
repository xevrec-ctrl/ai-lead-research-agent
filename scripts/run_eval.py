"""Run the offline contract checks for the redacted lead samples."""

from __future__ import annotations

import json
from pathlib import Path


REQUIRED_FIELDS = {"company", "industry", "client_need", "our_capabilities"}


def main() -> int:
    path = Path(__file__).parents[1] / "eval" / "samples.jsonl"
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    valid = sum(REQUIRED_FIELDS <= row.keys() for row in rows)
    companies = len({row["company"] for row in rows})
    print(
        f"samples={len(rows)} valid_input_contracts={valid} unique_companies={companies}"
    )
    if len(rows) < 30 or valid != len(rows):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
