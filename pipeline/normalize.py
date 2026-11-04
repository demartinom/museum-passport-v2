import yaml
from pathlib import Path
import json

REPO_ROOT = Path(__file__).parent.parent


def normalize(raw: dict, mapping: dict) -> dict:
    record = {}

    for my_field, met_field in mapping["fields"].items():
        record[my_field] = raw[met_field]

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

        item_string = json.dumps(normalized_item)
        path.write_text(item_string)


if __name__ == "__main__":
    mapping_path = REPO_ROOT / "pipeline" / "mappings" / "met.yaml"
    yaml_text = mapping_path.read_text()
    mapping = yaml.safe_load(yaml_text)

    raw_path = REPO_ROOT / "data" / "raw" / "met" / "49925.json"
    raw_text = raw_path.read_text()

    raw = json.loads(raw_text)
    print(normalize(raw, mapping))
