import json
from pathlib import Path

import pytest
import yaml

from normalize import normalize

pipeline_dir = Path(__file__).parent.parent
princeton_mapping_path = pipeline_dir / "mappings" / "princeton.yaml"
princeton_raw_dir = pipeline_dir.parent / "data" / "raw" / "princeton"
durer_path = princeton_raw_dir / "47087.json"
dragon_path = princeton_raw_dir / "129239.json"

# A small mapping shaped like princeton.yaml: a nested image base, then templates built from it
mapping = {
    "fields": {
        "source_id": "objectid",
        "artist": "makers.0.displayname",
        "image_base": "primaryimage.0",
    },
    "fixed": {"museum": "princeton"},
    "built": {
        "url": "https://example.org/objects/{source_id}",
        "image_large": "{image_base}/full/max/0/default.jpg",
    },
}
with_image = {
    "objectid": 1,
    "makers": [{"displayname": "Albrecht Dürer"}],
    "primaryimage": ["https://media.example.org/iiif/abc"],
}
without_image = {"objectid": 2, "makers": [], "primaryimage": []}


def test_fills_template_from_record():
    record = normalize(with_image, mapping)

    assert record["url"] == "https://example.org/objects/1"


def test_fills_template_from_a_nested_value():
    record = normalize(with_image, mapping)

    assert record["image_large"] == "https://media.example.org/iiif/abc/full/max/0/default.jpg"


def test_missing_value_gives_none_not_a_broken_link():
    record = normalize(without_image, mapping)

    assert record["image_large"] is None


def test_other_templates_still_build_when_one_is_missing():
    record = normalize(without_image, mapping)

    assert record["url"] == "https://example.org/objects/2"


def test_empty_fields_stay_in_record():
    # known (the copy without None values) is only for building; record keeps every field
    record = normalize(without_image, mapping)

    assert "artist" in record and record["artist"] is None
    assert "image_base" in record and record["image_base"] is None


def test_mapping_without_built_section():
    met_style = {"fields": {"source_id": "objectID"}, "fixed": {"museum": "met"}}

    record = normalize({"objectID": 123}, met_style)

    assert record == {"source_id": 123, "museum": "met", "id": "met-123"}


def test_does_not_change_mapping():
    built_before = dict(mapping["built"])

    normalize(without_image, mapping)

    assert mapping["built"] == built_before


needs_princeton = pytest.mark.skipif(
    not (durer_path.exists() and dragon_path.exists()),
    reason="no raw Princeton files; run harvest_princeton.py first",
)


@needs_princeton
def test_real_princeton_mapping_on_durer():
    real_mapping = yaml.safe_load(princeton_mapping_path.read_text())
    durer = json.loads(durer_path.read_text())

    record = normalize(durer, real_mapping)

    assert record["url"] == "https://artmuseum.princeton.edu/art/collections/objects/47087"
    assert record["image_large"].startswith(record["image_base"] + "/full/")
    assert record["image_small"].startswith(record["image_base"] + "/full/")


@needs_princeton
def test_real_princeton_mapping_on_record_without_image():
    real_mapping = yaml.safe_load(princeton_mapping_path.read_text())
    dragon = json.loads(dragon_path.read_text())

    record = normalize(dragon, real_mapping)

    assert record["title"] == "The Dragon"
    assert record["image_base"] is None
    assert record["image_large"] is None
    assert record["image_small"] is None
    assert record["url"] == "https://artmuseum.princeton.edu/art/collections/objects/129239"
