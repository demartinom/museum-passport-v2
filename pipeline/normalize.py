import yaml
from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).parent.parent


# Returns data from nested path, e.g. "makers.0.displayname" → raw["makers"][0]["displayname"]
def get_path(raw: dict, path: str):
    steps = path.split(".")
    value = raw
    for step in steps:
        if step.isdigit():
            # Empty list (e.g. no makers) is normal data, so None instead of crashing
            if len(value) == 0:
                return None
            value = value[int(step)]
        else:
            value = value[step]
    return value


def normalize(raw: dict, mapping: dict) -> dict:
    record = {}

    for my_field, museum_field in mapping["fields"].items():
        value = get_path(raw, museum_field)
        if value == "":
            value = None
        record[my_field] = value

    for my_field, fixed_value in mapping["fixed"].items():
        record[my_field] = fixed_value

    for my_field, museum_field in mapping.get("is_empty", {}).items():
        record[my_field] = get_path(raw, museum_field) is None

    # record without None values, so a template missing a value raises KeyError
    # instead of becoming the text "None"
    known = {}

    for name, value in record.items():
        if value is not None:
            known[name] = value

    for my_field, built_value in mapping.get("built", {}).items():
        try:
            record[my_field] = built_value.format(**known)
        except KeyError:
            record[my_field] = None

    record["id"] = f"{record['museum']}-{record['source_id']}"

    if record["date_begin"] == 0 and record["date_end"] == 0:
        record["date_begin"] = None
        record["date_end"] = None
    elif record["date_begin"] == 0:
        record["date_begin"] = record["date_end"]

    return record


def normalize_all(museum: str, items: list[dict], mapping: dict):
    normalized_folder = REPO_ROOT / "data" / "normalized" / museum
    normalized_folder.mkdir(parents=True, exist_ok=True)

    for item in items:
        normalized_item = normalize(item, mapping)
        path = normalized_folder / f"{normalized_item["source_id"]}.json"

        item_string = json.dumps(normalized_item, ensure_ascii=False)
        path.write_text(item_string)


if __name__ == "__main__":
    museum = sys.argv[1]
    mapping_path = REPO_ROOT / "pipeline" / "mappings" / f"{museum}.yaml"
    yaml_text = mapping_path.read_text()
    mapping = yaml.safe_load(yaml_text)

    raw_dir = REPO_ROOT / "data" / "raw" / museum
    raw_files = raw_dir.glob("*.json")
    all_records = []
    for raw_path in raw_files:
        raw_text = raw_path.read_text()
        raw_data = json.loads(raw_text)
        all_records.append(raw_data)
    normalize_all(museum, all_records, mapping)
