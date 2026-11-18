import json
from pathlib import Path

import pytest
import yaml

from normalize import normalize

pipeline_dir = Path(__file__).parent.parent
mapping_path = pipeline_dir / "mappings" / "met.yaml"
brick_path = pipeline_dir.parent / "data" / "raw" / "met" / "49925.json"

# Small made-up inputs, so each test shows exactly what goes in and comes out
mapping = {
    "fields": {"source_id": "objectID", "title": "title"},
    "fixed": {"museum": "met"},
}
raw = {"objectID": 123, "title": "Vase", "culture": "China"}


def test_copies_fields_under_schema_names():
    record = normalize(raw, mapping)

    assert record["source_id"] == 123
    assert record["title"] == "Vase"


def test_sets_fixed_values():
    record = normalize(raw, mapping)

    assert record["museum"] == "met"


def test_builds_id_from_museum_and_source_id():
    record = normalize(raw, mapping)

    assert record["id"] == "met-123"


def test_leaves_out_fields_not_in_mapping():
    record = normalize(raw, mapping)

    assert "culture" not in record
    assert "objectID" not in record


def test_keeps_values_unchanged():
    raw_with_types = {"objectID": 1, "title": "Bowl", "isPublicDomain": False, "objectBeginDate": -200}
    mapping_with_types = {
        "fields": {
            "source_id": "objectID",
            "title": "title",
            "public_domain": "isPublicDomain",
            "date_begin": "objectBeginDate",
        },
        "fixed": {"museum": "met"},
    }

    record = normalize(raw_with_types, mapping_with_types)

    assert record["public_domain"] is False
    assert record["date_begin"] == -200


def test_does_not_change_inputs():
    raw_copy = dict(raw)
    mapping_copy = {"fields": dict(mapping["fields"]), "fixed": dict(mapping["fixed"])}

    normalize(raw, mapping)

    assert raw == raw_copy
    assert mapping == mapping_copy


# Current behavior: a mapped field missing from the raw record stops normalizing.
# If you decide it should store None instead, change this test to match.
def test_missing_raw_field_raises_key_error():
    raw_without_title = {"objectID": 123}

    with pytest.raises(KeyError):
        normalize(raw_without_title, mapping)


@pytest.mark.skipif(not brick_path.exists(), reason="no raw Met files; run harvest_met.py first")
def test_real_mapping_on_porcelain_pagoda_brick():
    real_mapping = yaml.safe_load(mapping_path.read_text())
    brick = json.loads(brick_path.read_text())

    record = normalize(brick, real_mapping)

    # Every field in docs/schema.md
    assert set(record) == {
        "id", "museum", "museum_full_name", "source_id", "title", "artist",
        "date_display", "date_begin", "date_end", "url",
        "image_large", "image_small", "medium", "public_domain",
        "culture", "period",
    }
    assert record["id"] == "met-49925"
    assert record["title"] == "Brick from the Porcelain Pagoda"
    assert record["date_display"] == "early 15th century"
    assert record["date_begin"] == 1403
    assert record["date_end"] == 1430
    assert record["public_domain"] is True
    assert record["culture"] == "China"
    assert record["period"] == "Ming dynasty (1368–1644), Yongle period (1403–24)"


bowl_path = pipeline_dir.parent / "data" / "raw" / "met" / "63706.json"


@pytest.mark.skipif(not bowl_path.exists(), reason="no raw file for met-63706")
def test_empty_met_title_falls_back_to_object_name():
    # met-63706 (Hizen-ware bowl) has title "" in the raw record, objectName "Bowl"
    real_mapping = yaml.safe_load(mapping_path.read_text())
    bowl = json.loads(bowl_path.read_text())

    record = normalize(bowl, real_mapping)

    assert record["title"] == "Bowl"


def test_fallback_not_used_when_field_has_a_value():
    mapping = {
        "fields": {"source_id": "objectID", "title": "title"},
        "fixed": {"museum": "met"},
        "fallback": {"title": "objectName"},
    }
    raw = {"objectID": 1, "title": "Brick from the Porcelain Pagoda", "objectName": "Brick"}

    assert normalize(raw, mapping)["title"] == "Brick from the Porcelain Pagoda"


def test_fallback_used_when_field_is_empty_string():
    mapping = {
        "fields": {"source_id": "objectID", "title": "title"},
        "fixed": {"museum": "met"},
        "fallback": {"title": "objectName"},
    }
    raw = {"objectID": 1, "title": "", "objectName": "Bowl"}

    assert normalize(raw, mapping)["title"] == "Bowl"


def test_date_rule_skipped_when_mapping_has_no_dates():
    mapping = {"fields": {"source_id": "objectID"}, "fixed": {"museum": "met"}}

    record = normalize({"objectID": 1}, mapping)

    assert "date_begin" not in record
    assert "date_end" not in record


def date_mapping():
    return {
        "fields": {"source_id": "objectid", "date_begin": "datebegin", "date_end": "dateend"},
        "fixed": {"museum": "princeton"},
    }


def test_zero_begin_and_zero_end_become_unknown():
    # Like princeton-32504 (Sword guard): 0 / 0 in the source
    record = normalize({"objectid": 32504, "datebegin": 0, "dateend": 0}, date_mapping())

    assert record["date_begin"] is None
    assert record["date_end"] is None


def test_zero_begin_copies_end_year():
    # Like princeton-57301: 0 / 1912 means "made by 1912"
    record = normalize({"objectid": 57301, "datebegin": 0, "dateend": 1912}, date_mapping())

    assert record["date_begin"] == 1912
    assert record["date_end"] == 1912


def test_real_dates_are_left_alone():
    record = normalize({"objectid": 1, "datebegin": 1403, "dateend": 1430}, date_mapping())

    assert record["date_begin"] == 1403
    assert record["date_end"] == 1430


def test_bce_dates_are_left_alone():
    record = normalize({"objectid": 1, "datebegin": -206, "dateend": 220}, date_mapping())

    assert record["date_begin"] == -206
    assert record["date_end"] == 220
