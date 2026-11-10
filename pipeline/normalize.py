import yaml
from pathlib import Path
import json

REPO_ROOT = Path(__file__).parent.parent


def normalize(raw: dict, mapping: dict) -> dict:
    record = {}

    for my_field, museum_field in mapping["fields"].items():
        record[my_field] = raw[museum_field]

    for my_field, fixed_value in mapping["fixed"].items():
        record[my_field] = fixed_value

    record["id"] = f"{record['museum']}-{record['source_id']}"

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
    museum = "met"
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
