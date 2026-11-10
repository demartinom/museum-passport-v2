import json
from pathlib import Path

import pytest

from normalize import get_path, normalize

pipeline_dir = Path(__file__).parent.parent
durer_path = pipeline_dir.parent / "data" / "raw" / "princeton" / "47087.json"

# A small made-up record shaped like Princeton's, so each test shows the path it follows
raw = {
    "objectid": 47087,
    "displaytitle": "The Engraved Passion",
    "makers": [
        {"displayname": "Albrecht Dürer", "datebegin": 1471},
        {"displayname": "Second maker", "datebegin": 1500},
    ],
    "location": {"lat": "49.45", "lon": "11.08"},
    "periodterms": [],
}


def test_one_step_path_reads_top_level_field():
    assert get_path(raw, "displaytitle") == "The Engraved Passion"


def test_dict_path_reads_nested_field():
    assert get_path(raw, "location.lat") == "49.45"


def test_number_step_reads_list_item():
    assert get_path(raw, "makers.0.displayname") == "Albrecht Dürer"
    assert get_path(raw, "makers.1.displayname") == "Second maker"


def test_path_can_stop_at_a_list_or_dict():
    assert get_path(raw, "makers.0") == {"displayname": "Albrecht Dürer", "datebegin": 1471}
    assert len(get_path(raw, "makers")) == 2


def test_empty_list_returns_none():
    assert get_path(raw, "periodterms.0.period") is None


def test_keeps_value_types():
    assert get_path(raw, "objectid") == 47087
    assert get_path(raw, "makers.0.datebegin") == 1471


# A missing key is a mapping mistake (e.g. a typo in the YAML), so it should stop the run
def test_missing_key_raises_key_error():
    with pytest.raises(KeyError):
        get_path(raw, "displaytitel")


def test_missing_key_inside_list_item_raises_key_error():
    with pytest.raises(KeyError):
        get_path(raw, "makers.0.nickname")


def test_does_not_change_raw():
    makers_before = [dict(maker) for maker in raw["makers"]]

    get_path(raw, "makers.0.displayname")

    assert raw["makers"] == makers_before


def test_normalize_follows_nested_paths():
    mapping = {
        "fields": {"source_id": "objectid", "artist": "makers.0.displayname"},
        "fixed": {"museum": "princeton"},
    }

    record = normalize(raw, mapping)

    assert record["artist"] == "Albrecht Dürer"
    assert record["id"] == "princeton-47087"


def test_normalize_stores_none_when_list_is_empty():
    anonymous = {"objectid": 1, "makers": []}
    mapping = {
        "fields": {"source_id": "objectid", "artist": "makers.0.displayname"},
        "fixed": {"museum": "princeton"},
    }

    record = normalize(anonymous, mapping)

    assert record["artist"] is None


@pytest.mark.skipif(not durer_path.exists(), reason="no raw Princeton files; run harvest_princeton.py first")
def test_real_durer_record():
    durer = json.loads(durer_path.read_text())

    assert get_path(durer, "displaytitle") == "The Engraved Passion"
    assert get_path(durer, "makers.0.displayname") == "Albrecht Dürer"
    assert get_path(durer, "cultureterms.0.culture") == "European"
