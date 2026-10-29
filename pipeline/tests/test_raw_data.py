import json
from pathlib import Path

import pytest

# Raw files live in data/ at the repo root, which is gitignored
raw_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "met"
raw_paths = sorted(raw_dir.glob("*.json"))

pytestmark = pytest.mark.skipif(
    not raw_paths, reason="no raw Met files; run harvest_met.py first"
)


def test_raw_files_are_met_objects():
    # Catches error pages (e.g. a firewall's HTML) saved as {id}.json
    bad = []
    for path in raw_paths:
        try:
            raw = json.loads(path.read_text())
        except json.JSONDecodeError:
            bad.append(f"{path.name}: not valid JSON")
            continue
        if not isinstance(raw, dict) or "objectID" not in raw:
            bad.append(f"{path.name}: no objectID")

    assert not bad, "\n".join(bad)


def test_raw_file_name_matches_object_id():
    # Catches one object's data saved under another object's ID
    bad = []
    for path in raw_paths:
        raw = json.loads(path.read_text())
        if str(raw.get("objectID")) != path.stem:
            bad.append(f"{path.name} contains object {raw.get('objectID')}")

    assert not bad, "\n".join(bad)
