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


if __name__ == "__main__":
    mapping_path = REPO_ROOT / "pipeline" / "mappings" / "met.yaml"
    yaml_text = mapping_path.read_text()
    mapping = yaml.safe_load(yaml_text)

    raw_path = REPO_ROOT / "data" / "raw" / "met" / "49925.json"
    raw_text = raw_path.read_text()

    raw = json.loads(raw_text)
    print(normalize(raw, mapping))
